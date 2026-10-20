#!/usr/bin/env python3
"""Local authorization-gated task operations; does not spawn agents or sandbox source writes."""
import argparse
import json
import os
import platform
import re
import shutil
from pathlib import Path
import secrets
import subprocess
import sys
# A standalone preflight must not create bytecode beside a copied tool module.
sys.dont_write_bytecode = True
from coordination_store import Store, Rejected, atomic, encoded, file_hash, now, safe, sha


def read(root, path):
    return json.loads(safe(root, path).read_text(encoding='utf-8'))


def require(condition, message):
    if not condition:
        raise Rejected(message)


def config_for(root, bundle):
    plan = bundle['plan']; path = plan['configPath']
    require(file_hash(root, path) == plan['configHash'], 'Authorization configuration changed; a new reviewed authorization is required')
    return read(root, path)


def owned_code_directory(path):
    """Recognize bounded common/test subtrees, never a whole source root."""
    if not path.endswith('/'):
        return False
    parts = Path(path).parts
    if 'common' in parts:
        return parts.index('common') < len(parts) - 1
    return len(parts) > 1 and parts[0] in {'test', 'tests'}


def claim_scope(ownership, path, role_id):
    for existing, owner in ownership.items():
        overlaps = (path == existing
                    or existing.endswith('/') and path.startswith(existing)
                    or path.endswith('/') and existing.startswith(path))
        require(owner == role_id or not overlaps, 'Duplicate or overlapping file owner: '+path)
    ownership[path] = role_id


def boundary_paths(root, path):
    """Read only the existing Markdown Section 1 table whitelist."""
    paths = set()
    active = False
    for line in safe(root, path).read_text(encoding='utf-8').splitlines():
        if line.lstrip().startswith('#'):
            is_section = 'section 1' in line.lower() or '第 1 节' in line or '第1节' in line
            if active and not is_section:
                break
            if is_section:
                active = True
        if active and line.lstrip().startswith('|'):
            columns = line.strip().split('|')
            if len(columns) >= 4:
                paths.update(re.findall(r'`([^`]+)`', columns[2]))
    return paths


def canonical_scope(root, path, exact=False):
    resolved = safe(root, path)
    canonical = resolved.relative_to(root).as_posix()
    if path.endswith('/') and not exact:
        canonical += '/'
    require(canonical == path and not any(char in path for char in '*?[]'), 'Scope must use a canonical path: '+path)
    if path.endswith('/') and not exact:
        require(not resolved.exists() or resolved.is_dir(), 'Directory scope points to a file: '+path)
    else:
        require(not resolved.is_dir(), 'Scope must be an exact file: '+path)
    return resolved


def scope_overlap(first, second):
    return (first == second or first.endswith('/') and second.startswith(first)
            or second.endswith('/') and first.startswith(second))


ROOT_WORK_FILES = {'feature-map.md', 'memo.md', 'functional-description.md', 'api-spec.md'}
GOVERNANCE_NAMES = {'role-card.md', 'boundary.md', 'boundary.yaml', 'changelog.md'}


def work_document(path, definition, directory=False):
    role_root = definition['root']+'/'
    if not path.startswith(role_root):
        return False
    local = path[len(role_root):]
    if not directory and local in ROOT_WORK_FILES:
        return local != 'api-spec.md' or definition['apiSpec'] == 'required'
    if not local.startswith('docs/'):
        return False
    if any(part in GOVERNANCE_NAMES for part in Path(local).parts):
        return False
    if directory:
        return path.endswith('/')
    return path.endswith('.md')


def definitions_for(root, config):
    definitions = config.get('roleDefinitions')
    require(isinstance(definitions, dict) and definitions, 'Complete roleDefinitions required')
    registered = {}
    protected = set()
    for role_id, definition in definitions.items():
        require(isinstance(role_id, str) and role_id and isinstance(definition, dict), 'Invalid roleDefinitions entry')
        for key in ['card', 'boundary']:
            canonical_scope(root, definition[key], exact=True)
            require(file_hash(root, definition[key]), 'Missing '+role_id+' '+key+': '+definition[key])
        parent = Path(definition['card']).parent.as_posix()
        require(parent != '.' and parent == Path(definition['boundary']).parent.as_posix(), 'Role '+role_id+' card/boundary must share a role root')
        require(parent != '.ans' and not parent.startswith(('.ans/', 'docs/scheduling/')) and parent != 'docs/scheduling', 'Role root cannot be in task state: '+parent)
        for other_id, other in registered.items():
            require(not scope_overlap(parent+'/', other['root']+'/'), 'Overlapping role roots: '+role_id+' and '+other_id)
        require(definition.get('apiSpec') in {'required', 'not-applicable'}, 'Role '+role_id+' apiSpec must be required or not-applicable')
        require(isinstance(definition.get('apiSpecReason'), str) and definition['apiSpecReason'].strip(), 'Role '+role_id+' apiSpecReason required')
        required = definition.get('requiredWorkDocuments')
        require(isinstance(required, list) and all(isinstance(path, str) for path in required), 'Role '+role_id+' requiredWorkDocuments must be exact files')
        registered[role_id] = {**definition, 'root': parent, 'scopes': boundary_paths(root, definition['boundary'])}
        protected.update([definition['card'], definition['boundary'], str(Path(definition['boundary']).with_suffix('.yaml')), parent+'/changelog.md'])
    required_ids = set(config.get('roles', {})) | {config.get('schedulerRoleId', 'scheduler')}
    authority = config.get('acceptanceAuthority')
    if isinstance(authority, dict):
        required_ids.add(authority['roleId'])
    require(required_ids <= set(registered), 'Role definitions missing: '+', '.join(sorted(required_ids-set(registered))))
    bindings = dict(config.get('roles', {}))
    if isinstance(authority, dict):
        bindings[authority['roleId']] = authority
    for role_id, role in bindings.items():
        require(all(role[key] == registered[role_id][key] for key in ['card', 'boundary']), 'Role '+role_id+' card/boundary differs from roleDefinitions')
    return registered, protected


def registered_path_valid(root, path, role_id, definitions, protected):
    resolved = canonical_scope(root, path)
    require(not any(scope_overlap(path, item) for item in protected), 'Role '+role_id+' scope includes protected governance: '+path)
    for owner, definition in definitions.items():
        if scope_overlap(path, definition['root']+'/'):
            require(owner == role_id and work_document(path, definition, directory=path.endswith('/')), 'Role '+role_id+' scope includes another role or invalid work document: '+path)
    # A docs grant cannot hide conventional governance files that were not selected for this task.
    if path.endswith('/') and work_document(path, definitions[role_id], directory=True) and resolved.exists():
        for nested in resolved.rglob('*'):
            require(nested.name not in GOVERNANCE_NAMES, 'Role '+role_id+' document directory includes governance: '+nested.relative_to(root).as_posix())


def preflight_role(root, config):
    result = {'status': 'rejected', 'permissionsComplete': False, 'roles': [], 'issues': []}
    try:
        require(config.get('schemaVersion') == 1 and isinstance(config.get('roles'), dict), 'Invalid configuration')
        definitions, protected = definitions_for(root, config)
    except (Rejected, OSError, KeyError, TypeError, ValueError) as exc:
        result['issues'].append({'reason': str(exc)})
        return result
    ownership = {}
    for role_id, definition in definitions.items():
        role_result = {'roleId': role_id, 'permissionsComplete': False, 'documents': [], 'issues': []}
        for path in sorted(definition['scopes']):
            try:
                registered_path_valid(root, path, role_id, definitions, protected)
                if path in {'.ans', 'docs/scheduling'} or path.startswith(('.ans/', 'docs/scheduling/')):
                    require(role_id == config.get('schedulerRoleId', 'scheduler'), 'Task management scope belongs to scheduler: '+path)
                if path.endswith('/'):
                    management_scope = role_id == config.get('schedulerRoleId', 'scheduler') and path in {'.ans/runtime/', 'docs/scheduling/'}
                    require(owned_code_directory(path) or work_document(path, definition, directory=True) or management_scope, 'Role '+role_id+' directory scope is too broad or unsupported: '+path)
                claim_scope(ownership, path, role_id)
            except (Rejected, OSError, ValueError) as exc:
                role_result['issues'].append({'path': path, 'reason': str(exc)})
        mandatory = {definition['root']+'/'+name for name in ['feature-map.md', 'memo.md', 'functional-description.md']}
        if definition['apiSpec'] == 'required':
            mandatory.add(definition['root']+'/api-spec.md')
        for path in sorted(mandatory-set(definition['requiredWorkDocuments'])):
            role_result['issues'].append({'path': path, 'reason': 'Required core/API document absent from requiredWorkDocuments'})
        for path in definition['requiredWorkDocuments']:
            document = {'path': path, 'exists': False, 'permissionGranted': False}
            try:
                document['exists'] = canonical_scope(root, path, exact=True).is_file()
                registered_path_valid(root, path, role_id, definitions, protected)
                require(work_document(path, definition), 'Required document is not this role work document: '+path)
                require(any(scope_overlap(scope, path) for scope in definition['scopes']), 'Required document missing from boundary Section 1: '+path)
                document['permissionGranted'] = True
            except (Rejected, OSError, ValueError) as exc:
                role_result['issues'].append({'path': path, 'reason': str(exc)})
            role_result['documents'].append(document)
        role_result['permissionsComplete'] = not role_result['issues']
        result['roles'].append(role_result)
    result['permissionsComplete'] = all(role['permissionsComplete'] for role in result['roles'])
    if result['permissionsComplete']:
        result['status'] = 'ok'
    return result


def roles_valid(root, config):
    require(config.get('schemaVersion') == 1 and isinstance(config.get('roles'), dict), 'Invalid configuration')
    ownership = {}
    definitions = {}
    protected = set()
    if 'roleDefinitions' in config:
        preflight = preflight_role(root, config)
        require(preflight['permissionsComplete'], 'Role permission preflight failed: '+json.dumps(preflight, ensure_ascii=False))
        definitions, protected = definitions_for(root, config)
    for role_id, role in config['roles'].items():
        require(isinstance(role, dict), 'Invalid role configuration')
        for key in ['card', 'boundary']:
            require(file_hash(root, role[key]), 'Missing role '+key)
        require(isinstance(role.get('writeFiles'), list), 'writeFiles must be exact file paths')
        paths = boundary_paths(root, role['boundary'])
        directories = [path for path in paths if owned_code_directory(path) or definitions and work_document(path, definitions[role_id], directory=True)]
        for directory in directories:
            resolved = safe(root, directory)
            require(resolved.relative_to(root).as_posix()+'/' == directory, 'Directory scope must use a canonical path')
            if definitions:
                registered_path_valid(root, directory, role_id, definitions, protected)
            else:
                require(not directory.startswith(('role-cards/', '角色卡/')), 'Execution scope cannot include governance/state files')
            require(not directory.startswith(('.ans/', 'docs/scheduling/')), 'Execution scope cannot include governance/state files')
            claim_scope(ownership, directory, role_id)
        for path in role['writeFiles']:
            resolved = safe(root, path)
            require(resolved.relative_to(root).as_posix() == path and not resolved.is_dir(), 'writeFiles must use exact canonical file paths')
            require(path in paths or any(path.startswith(directory) for directory in directories), 'Configured write file is absent from boundary Section 1: '+path)
            if definitions:
                registered_path_valid(root, path, role_id, definitions, protected)
                require(not path.startswith(('role-cards/', '角色卡/')) or work_document(path, definitions[role_id]), 'Execution scope cannot include unregistered role documents: '+path)
            else:
                require(not path.startswith(('role-cards/', '角色卡/')), 'Execution scope cannot include governance/state files')
            require(path not in {'.ans', 'docs/scheduling'} and not path.startswith(('.ans/', 'docs/scheduling/')), 'Execution scope cannot include governance/state files')
            claim_scope(ownership, path, role_id)
        require(isinstance(role.get('operations'), list), 'Role operations required')
        for check_id, check in role.get('checks', {}).items():
            require(check_id and all(c.isalnum() or c in '-_' for c in check_id), 'Invalid check ID')
            require(isinstance(check.get('env', {}), dict) and all(isinstance(k, str) and isinstance(v, str) for k,v in check.get('env', {}).items()), 'Check env requires string keys and values')
            require(isinstance(check.get('argv'), list) and check['argv'] and all(isinstance(a,str) for a in check['argv']), 'Check requires explicit argv')
    return ownership


def normalize_plan(root, raw, config, config_path, approved_hash, task):
    require(file_hash(root, config_path) == approved_hash, 'Approved configuration hash does not match actual file')
    roles_valid(root, config)
    require(raw.get('schemaVersion') == 1 and raw.get('taskId') == task, 'Plan schema/task mismatch')
    plan = json.loads(json.dumps(raw)); plan['planRevision'] = 1
    plan['configPath'] = config_path; plan['configHash'] = approved_hash
    for name in ['requirement', 'design']:
        ref = plan[name]
        require(isinstance(ref.get('version'), str) and ref['version'], 'Version required')
        ref['sha256'] = file_hash(root, ref['path'])
        require(ref['sha256'], 'Missing '+name+' document')
    require(plan['design']['path'] in config.get('designFiles', []), 'Design path is not permitted')
    require(isinstance(plan.get('nodes'), list) and plan['nodes'], 'Plan nodes required')
    ids = set()
    for node in plan['nodes']:
        node_id = node.get('nodeId')
        require(isinstance(node_id,str) and node_id and all(c.isalnum() or c in '-_' for c in node_id) and node_id not in ids, 'Invalid/duplicate node ID')
        ids.add(node_id)
        role = config['roles'].get(node.get('roleId')); require(role is not None, 'Unknown role')
        require(node.get('operation') in role['operations'], 'Operation not permitted')
        require(isinstance(node.get('writeSet'), list) and set(node['writeSet']) <= set(role['writeFiles']), 'Node exceeds role write scope')
        node['requiredOutputs']=node.get('requiredOutputs',list(node['writeSet']))
        require(isinstance(node['requiredOutputs'],list) and set(node['requiredOutputs'])<=set(node['writeSet']),'Required outputs must fit the assigned write set')
        require(isinstance(node.get('checks'), list) and node['checks'], 'Every executable stage requires checks')
        require(all(c in role.get('checks', {}) for c in node['checks']), 'Unknown required check')
        node['readSet'] = node.get('readSet', [])
        require(isinstance(node['readSet'],list),'readSet must be a path list')
        for path in node['readSet']: safe(root,path)
        node['roleHashes'] = {k: file_hash(root,role[k]) for k in ['card','boundary']}
        node['revisions'] = {'requirement':plan['requirement']['version'], 'design':plan['design']['version'], 'boundary':node['roleHashes']['boundary']}
        node['documentHashes'] = {n:plan[n]['sha256'] for n in ['requirement','design']}
        require(isinstance(node.get('dependsOn', []),list), 'dependsOn must be a node-ID array')
    nodes = {n['nodeId']:n for n in plan['nodes']}; done = set()
    while len(done) < len(nodes):
        eligible = {i for i,n in nodes.items() if i not in done and set(n.get('dependsOn',[])) <= done}
        require(eligible, 'Plan contains unknown prerequisites or a dependency cycle')
        done |= eligible
    return plan


def node_pair(bundle, node_id):
    planned = next((n for n in bundle['plan']['nodes'] if n['nodeId']==node_id), None)
    state = next((n for n in bundle['state']['nodes'] if n['nodeId']==node_id), None)
    require(planned is not None and state is not None, 'Unknown stage')
    return planned,state


def current_inputs(root, bundle, planned, config):
    role = config['roles'][planned['roleId']]
    for key, expected in planned['roleHashes'].items():
        require(file_hash(root,role[key]) == expected, 'Role definition changed; redispatch needs accepted definitions')
    for key, expected in planned['documentHashes'].items():
        require(file_hash(root,bundle['plan'][key]['path']) == expected, key+' content changed; revise/reconcile before execution')


def candidate(root, bundle, planned):
    coverage = {test['nodeId']: test['covers'] for test in bundle['state'].get('planAcceptance', {}).get('independentTests', [])}
    ids = {planned['nodeId']}; todo = list(planned.get('dependsOn', [])) + list(coverage.get(planned['nodeId'], []))
    while todo:
        key = todo.pop()
        if key in ids: continue
        ids.add(key); n,_ = node_pair(bundle,key);todo.extend(n.get('dependsOn', []));todo.extend(coverage.get(key, []))
    paths = set()
    for n in bundle['plan']['nodes']:
        if n['nodeId'] in ids: paths.update(n['writeSet']); paths.update(n.get('readSet',[]))
    return sha(encoded({p:file_hash(root,p) for p in sorted(paths)}))


def authenticate(state, request, acknowledged=True):
    require(state.get('attemptId') == request.get('attemptId') and state.get('workerId') == request.get('workerId'), 'Stale attempt or wrong worker')
    token = request.get('token', '')
    require(isinstance(token,str) and secrets.compare_digest(state.get('assignmentCredentialHash',''),sha(token.encode())), 'Invalid assignment token')
    require(state.get('active'), 'Assignment is not active')
    if acknowledged:
        require(request.get('revisions') == state['assignedRevisions'] == state.get('acknowledgedRevisions'), 'Revision mismatch or missing acknowledgment')
        require(not state.get('pauseRequested'), 'Assignment paused for revision')


def authority_valid(root, config):
    authority = config.get('acceptanceAuthority')
    require(isinstance(authority, dict), 'Approved acceptanceAuthority required')
    require(isinstance(authority.get('roleId'), str) and authority['roleId'], 'Acceptance roleId required')
    require(authority['roleId'] != config.get('schedulerRoleId', 'scheduler') and authority['roleId'] not in config['roles'], 'Acceptance role must be independent of scheduler and executors')
    for key in ['card', 'boundary']:
        digest = file_hash(root, authority[key])
        require(digest and digest == authority.get(key+'Sha256'), 'Approved acceptance '+key+' hash required')
    digest = authority.get('credentialHash', '')
    require(isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest), 'Acceptance credentialHash must be SHA-256')
    require(isinstance(authority.get('criteriaFiles'), list) and authority['criteriaFiles'], 'Allowed criteriaFiles required')
    for path in authority['criteriaFiles']:
        safe(root, path)
    return authority


def credential(expected, supplied, message):
    require(isinstance(supplied, str) and bool(expected) and secrets.compare_digest(expected, sha(supplied.encode())), message)


def plan_snapshot(bundle):
    return sha(encoded(bundle['plan']))


def accepted_plan(root, bundle, config):
    authority = authority_valid(root, config)
    require(authority == bundle['state']['acceptanceAuthority'], 'Acceptance authority changed; initialize a new reviewed task')
    approval = bundle['state'].get('planAcceptance')
    require(approval and approval['planHash'] == plan_snapshot(bundle), 'Current accept-plan required')
    criteria = approval['criteria']
    require(file_hash(root, criteria['path']) == criteria['sha256'], 'Acceptance criteria changed')
    for planned in bundle['plan']['nodes']:
        current_inputs(root, bundle, planned, config)
    return approval


def execution_environment(check):
    return {**os.environ, **check.get('env', {}), 'PYTHONDONTWRITEBYTECODE': '1'}


def environment(root, check):
    # Same environment and cwd as subprocess. Undeclared dependencies remain outside this model.
    actual = execution_environment(check)
    keys = ['PATH', 'PYTHONPATH', 'NODE_PATH', 'NODE_OPTIONS', 'LANG', 'LC_ALL', 'TZ', 'PYTHONDONTWRITEBYTECODE']
    values = {key: actual.get(key) for key in keys}
    values.update({key: actual[key] for key in check.get('env', {})})
    command = check['argv'][0]
    if os.path.dirname(command):
        executable = str((root / command).resolve())
    else:
        paths = actual.get('PATH', os.defpath).split(os.pathsep)
        search_path = os.pathsep.join(str((root / entry).resolve()) for entry in paths)
        executable = shutil.which(command, path=search_path)
    return {'platform': platform.platform(), 'python': platform.python_version(),
            'executable': executable, 'executableHash': sha(Path(executable).read_bytes()) if executable and Path(executable).is_file() else None,
            'variablesHash': sha(encoded(values)), 'declaredEnvironment': check.get('env', {})}


TRACKED_ENVIRONMENT_KEYS = {'PATH', 'PYTHONPATH', 'NODE_PATH', 'NODE_OPTIONS', 'LANG', 'LC_ALL', 'TZ', 'PYTHONDONTWRITEBYTECODE'}


def environment_identity(root, check, actual):
    """Fingerprint the captured execution inputs, never the status caller's environment."""
    keys = sorted(TRACKED_ENVIRONMENT_KEYS | set(check.get('env', {})))
    command = check['argv'][0]
    if os.path.dirname(command):
        selected = os.path.abspath(root / command)
    else:
        search_path = os.pathsep.join(os.path.abspath(root / entry) for entry in actual.get('PATH', os.defpath).split(os.pathsep))
        selected = shutil.which(command, path=search_path)
    executable = None
    digest = None
    if selected:
        executable = str(Path(selected).resolve())
        if Path(executable).is_file():
            digest = sha(Path(executable).read_bytes())
    return {'platform': platform.platform(), 'python': platform.python_version(),
            'selectedExecutable': selected, 'executable': executable, 'executableHash': digest,
            'trackedKeys': keys, 'variablesHash': sha(encoded({key: actual.get(key) for key in keys})),
            'declaredEnvironmentHash': sha(encoded(check.get('env', {})))}


def save_environment_snapshot(root, task, state, check_id, check, actual):
    keys = sorted(TRACKED_ENVIRONMENT_KEYS | set(check.get('env', {})))
    snapshot = {'environmentVersion': 2, 'trackedKeys': keys,
                'values': {key: actual[key] for key in keys if key in actual},
                'absentKeys': [key for key in keys if key not in actual]}
    for relative in ['.ans/runtime/check-environments', '.ans/runtime/check-environments/'+task]:
        directory = safe(root, relative)
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        directory.chmod(0o700)
    relative = '.ans/runtime/check-environments/'+task+'/'+state['attemptId']+'-'+check_id+'-'+secrets.token_hex(8)+'.json'
    path = safe(root, relative)
    atomic(path, encoded(snapshot))
    path.chmod(0o600)
    return {'path': relative, 'sha256': file_hash(root, relative)}


def check_environment_valid(root, bundle, state, check_id, check, evidence):
    if 'environmentVersion' not in evidence:
        require(evidence['environment'] == environment(root, check), 'Check environment or approved command changed')
        return
    require(type(evidence['environmentVersion']) is int and evidence['environmentVersion'] == 2, 'Unknown check environment version')
    reference = evidence.get('environmentSnapshot')
    require(isinstance(reference, dict), 'Execution environment snapshot missing or changed')
    prefix = '.ans/runtime/check-environments/'+bundle['state']['taskId']+'/'+state['attemptId']+'-'+check_id+'-'
    path = reference.get('path')
    require(isinstance(path, str) and path.startswith(prefix) and re.fullmatch(r'[0-9a-f]{16}\.json', path[len(prefix):]), 'Invalid execution environment snapshot path')
    canonical_scope(root, path, exact=True)
    digest = file_hash(root, path)
    require(digest and digest == reference.get('sha256'), 'Execution environment snapshot missing or changed')
    try:
        snapshot = read(root, path)
    except ValueError as exc:
        raise Rejected('Invalid execution environment snapshot JSON') from exc
    keys = sorted(TRACKED_ENVIRONMENT_KEYS | set(check.get('env', {})))
    require(isinstance(snapshot, dict) and set(snapshot) == {'environmentVersion', 'trackedKeys', 'values', 'absentKeys'}
            and type(snapshot.get('environmentVersion')) is int and snapshot['environmentVersion'] == 2
            and snapshot.get('trackedKeys') == keys, 'Invalid execution environment snapshot shape')
    values = snapshot.get('values')
    absent = snapshot.get('absentKeys')
    require(isinstance(values, dict) and all(isinstance(key, str) and isinstance(value, str) for key, value in values.items())
            and isinstance(absent, list) and all(isinstance(key, str) for key in absent)
            and len(absent) == len(set(absent)) and not set(values) & set(absent)
            and set(values) | set(absent) == set(keys), 'Invalid execution environment snapshot keys/absent values')
    expected = {**check.get('env', {}), 'PYTHONDONTWRITEBYTECODE': '1'}
    require(all(values.get(key) == value for key, value in expected.items()), 'Declared check environment changed')
    require(evidence['environment'] == environment_identity(root, check, values), 'Check execution environment or approved command changed')


def producer(planned, state):
    return {key: value for key, value in {'roleId': planned['roleId'], 'nodeId': planned['nodeId'], 'workerId': state['workerId'], 'attemptId': state['attemptId']}.items()}


def evidence_valid(root, bundle, planned, state, config):
    current_inputs(root, bundle, planned, config)
    current = candidate(root, bundle, planned)
    for output in planned['requiredOutputs']:
        require(file_hash(root, output) is not None, 'Missing required output: '+output)
    report = state.get('latestReport', {})
    require(report.get('kind') == 'complete' and report.get('candidate') == current and report.get('attemptId') == state['attemptId'], 'Implementation changed after completion report or no current completion report')
    for check_id in planned['checks']:
        evidence = state['checkEvidence'].get(check_id)
        require(evidence is not None, 'Missing required check: '+check_id)
        require(evidence['producer'] == producer(planned, state), 'Check producer or attempt mismatch')
        check = config['roles'][planned['roleId']]['checks'][check_id]
        require(file_hash(root, evidence['path']) == evidence['sha256'], 'Check evidence is unavailable or changed')
        require(evidence['argv'] == check['argv'] and evidence['configHash'] == bundle['plan']['configHash'], 'Check environment or approved command changed')
        check_environment_valid(root, bundle, state, check_id, check, evidence)
        require(evidence['exitCode'] == 0 and not evidence['timedOut'] and evidence['candidateUnchanged'] and evidence.get('environmentUnchanged') and evidence['candidate'] == current, 'Required check failed or evidence is stale')
    return current


def valid_pass(root, bundle, node_id, config, seen=None):
    seen = set() if seen is None else seen
    require(node_id not in seen, 'Acceptance dependency cycle')
    seen = seen | {node_id}
    approval = accepted_plan(root, bundle, config)
    planned, state = node_pair(bundle, node_id)
    require(state['status'] == 'verified', 'Prerequisite is not verified: '+node_id)
    current = evidence_valid(root, bundle, planned, state, config)
    acceptance = state.get('acceptance', {})
    require(acceptance.get('verdict') == 'pass' and acceptance.get('candidate') == current and acceptance.get('attemptId') == state['attemptId'], 'Acceptance candidate or attempt is stale: '+node_id)
    current_approval = acceptance.get('planAcceptanceHash') == sha(encoded(approval)) or approval.get('carriedAcceptances', {}).get(node_id) == sha(encoded(acceptance))
    require(current_approval and acceptance.get('reportId') == state['latestReport']['reportId'] and acceptance.get('evidenceHash') == sha(encoded(state['checkEvidence'])), 'Acceptance standards, report or evidence changed: '+node_id)
    dependencies = set(planned.get('dependsOn', []))
    for test in approval['independentTests']:
        if test['nodeId'] == node_id:
            dependencies.update(test['covers'])
    for dep in dependencies:
        valid_pass(root, bundle, dep, config, seen)
        require(acceptance.get('dependencyAcceptances', {}).get(dep) == sha(encoded(node_pair(bundle, dep)[1]['acceptance'])), 'Ancestor acceptance changed: '+dep)
    return current


def redact(value):
    if isinstance(value, dict):
        return {key: redact(item) for key, item in value.items() if not any(word in key.lower() for word in ['token', 'credential'])}
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def status(root, bundle):
    result = json.loads(json.dumps(bundle['state']))
    result['taskComplete'] = False
    if result.get('schemaVersion') != 2:
        result['legacyReadOnly'] = True
        result['legacyAcceptance'] = 'Original workflow; not independent acceptance'
    else:
        valid = []
        try:
            config = config_for(root, bundle)
            roles_valid(root, config)
            for node in result['nodes']:
                planned, _ = node_pair(bundle, node['nodeId'])
                node['currentCandidate'] = candidate(root, bundle, planned)
                try:
                    valid_pass(root, bundle, node['nodeId'], config)
                    node['currentAcceptanceValid'] = True
                except (Rejected, OSError, KeyError, TypeError) as exc:
                    node['currentAcceptanceValid'] = False
                    node['currentAcceptanceReason'] = str(exc)
                valid.append(node['currentAcceptanceValid'])
            result['taskComplete'] = bool(valid) and all(valid)
        except (Rejected, OSError, KeyError, TypeError) as exc:
            result['currentValidityReason'] = str(exc)
    return {'status': 'ok', 'state': redact(result)}


def acceptance_results(root, bundle, planned, state, request, approval):
    results = request.get('criteriaResults')
    require(isinstance(results, list) and len(results) == len(approval['criteria']['criterionIds']), 'Every criterion requires a result')
    require({r.get('criterionId') for r in results} == set(approval['criteria']['criterionIds']), 'Criteria result IDs mismatch')
    for result in results:
        require(result.get('verdict') in {'pass', 'needs-work', 'missing-evidence'}, 'Invalid criterion verdict')
        references = result.get('evidence')
        require(isinstance(references, list), 'Criterion evidence references required')
        if request['verdict'] == 'pass':
            require(result['verdict'] == 'pass' and references, 'Pass requires evidence for every criterion')
        else:
            require(result.get('summary') or references, 'Explain criterion gap or reference evidence')
        for ref in references:
            kind = ref.get('kind')
            if kind == 'output':
                require(ref.get('path') in set(planned['writeSet']) | set(planned['readSet']), 'Output reference exceeds stage scope')
                digest = file_hash(root, ref['path'])
                require(digest and digest == ref.get('sha256'), 'Output evidence changed')
            elif kind == 'check':
                evidence = state['checkEvidence'].get(ref.get('checkId'))
                require(evidence and evidence['sha256'] == ref.get('sha256') and file_hash(root, evidence['path']) == evidence['sha256'], 'Invalid check evidence reference')
            elif kind == 'report':
                require(state.get('latestReport', {}).get('reportId') == ref.get('reportId'), 'Invalid report reference')
            else:
                raise Rejected('Unknown criterion evidence kind')
    if request['verdict'] != 'pass':
        require(any(r['verdict'] == request['verdict'] for r in results), 'Verdict must identify at least one corresponding criterion')
    return results


def operate(root, task, command, request):
    if command == 'preflight-role':
        root = Path(root).resolve()
        require(root.is_dir(), 'Project root missing')
        require(set(request) <= {'configPath'}, 'Preflight request accepts only configPath')
        return preflight_role(root, read(root, request.get('configPath', '.ans/project.json')))
    store = Store(root,task); root=store.root
    store.derive = lambda bundle: status(root, bundle)['state']['taskComplete']
    with store.locked():
        if command == 'init':
            require(not store.document.exists(), 'Task already initialized')
            legacy = safe(root, 'docs/scheduling/'+task)
            require(not any((legacy/name).exists() for name in ['plan.json','state.json','events.jsonl']), 'Existing JSON task records must not be overwritten')
            config_path=request.get('configPath','.ans/project.json');config=read(root,config_path)
            plan=normalize_plan(root,request['plan'],config,config_path,request['approvedConfigSha256'],task)
            states=[{'nodeId':n['nodeId'],'roleId':n['roleId'],'status':'pending','attemptId':None,'active':False,'assignedRevisions':n['revisions'],'acknowledgedRevisions':None,'checkEvidence':{},'attemptNumber':0} for n in plan['nodes']]
            require(not any(key in request for key in ['coordinatorToken', 'acceptanceToken', 'acceptanceAuthority', 'credentialHash']), 'Init cannot override or mint acceptance credentials; use schedulerToken')
            authority = authority_valid(root, config)
            scheduler_token = request.get('schedulerToken') or secrets.token_urlsafe(32)
            require(isinstance(scheduler_token, str) and len(scheduler_token) >= 32, 'Scheduler token must be at least 32 characters')
            require(sha(scheduler_token.encode()) != authority['credentialHash'], 'Scheduler and acceptance credentials must be different')
            bundle={'plan':plan,'state':{'schemaVersion':2,'taskId':task,'planRevision':1,'nodes':states,'reportReceipts':{},'schedulerCredentialHash':sha(scheduler_token.encode()),'acceptanceAuthority':authority}}
            store.producer = {'roleId': config.get('schedulerRoleId', 'scheduler'), 'kind': 'scheduler'}
            result=store.commit(bundle,'initialized','Reviewed plan and independent authority pinned')
            result['schedulerToken']=scheduler_token
            return result
        bundle=store.load(recover=command=='recover')
        if command == 'status':
            return status(root, bundle)
        require(bundle['state'].get('schemaVersion') == 2, 'Legacy task is read-only; initialize a new reviewed v2 task')
        if command in {'dispatch','revise','recover'}:
            credential(bundle['state'].get('schedulerCredentialHash'), request.get('schedulerToken'), 'Scheduler credential required')
            store.producer = {'roleId': 'scheduler', 'kind': 'scheduler'}
        if command == 'recover':
            return status(root, bundle)
        config=config_for(root,bundle); roles_valid(root,config)
        node_id=request.get('nodeId')
        if command in {'accept-plan', 'verify'}:
            authority = authority_valid(root, config)
            require(authority == bundle['state']['acceptanceAuthority'], 'Acceptance authority changed')
            credential(authority['credentialHash'], request.get('acceptanceToken'), 'Independent acceptance credential required')
            require(type(request.get('stateRevision')) is int and request['stateRevision'] == bundle['state']['stateRevision'], 'Stale stateRevision')
            store.producer = {'roleId': authority['roleId'], 'kind': 'acceptance'}
        elif command in {'dispatch', 'revise'}:
            store.producer = {'roleId': config.get('schedulerRoleId', 'scheduler'), 'kind': 'scheduler'}
        if command == 'accept-plan':
            require(request.get('planRevision') == bundle['plan']['planRevision'], 'Stale planRevision')
            authority = authority_valid(root, config)
            criteria = request.get('criteria', {})
            require(criteria.get('path') in authority['criteriaFiles'], 'Criteria path is not approved')
            require(isinstance(criteria.get('version'), str) and criteria['version'], 'Criteria version required')
            require(file_hash(root, criteria['path']) and file_hash(root, criteria['path']) == criteria.get('sha256'), 'Criteria hash mismatch')
            ids = criteria.get('criterionIds')
            require(isinstance(ids, list) and ids and all(isinstance(i, str) and i for i in ids) and len(set(ids)) == len(ids), 'Unique criterionIds required')
            source = request.get('customerApproval', {})
            require(isinstance(source, dict) and all(isinstance(source.get(k), str) and source[k] for k in ['source', 'reference']), 'Traceable customer approval source/reference required; this is not identity authentication')
            nodes = {n['nodeId']: n for n in bundle['plan']['nodes']}
            required = request.get('requiredNodes')
            require(isinstance(required, list) and len(required) == len(nodes) and set(required) == set(nodes), 'All plan nodes are required')
            tests = request.get('independentTests', [])
            require(isinstance(tests, list), 'independentTests must be an array')
            test_ids = set()
            covered = set()
            for test in tests:
                tid = test.get('nodeId')
                require(tid in nodes and tid not in test_ids and config['roles'][nodes[tid]['roleId']].get('purpose') == 'independent-test', 'Independent test node requires approved independent-test role')
                test_ids.add(tid)
                covers = test.get('covers')
                require(isinstance(covers, list) and covers and len(set(covers)) == len(covers), 'Independent test covers required')
                for target in covers:
                    require(target in nodes and nodes[target]['roleId'] != nodes[tid]['roleId'] and config['roles'][nodes[target]['roleId']].get('purpose') != 'independent-test', 'Test producer must differ from tested developer')
                    require(set(nodes[target]['writeSet'] + nodes[target]['readSet']) <= set(nodes[tid]['readSet']), 'Independent test readSet must include tested inputs and outputs')
                covered.update(covers)
            dev_ids = {i for i,n in nodes.items() if config['roles'][n['roleId']].get('purpose') != 'independent-test'}
            cross_role = len({n['roleId'] for n in nodes.values()}) > 1
            require(not cross_role or covered == dev_ids and test_ids == set(nodes)-dev_ids, 'Cross-role task requires independent test coverage of every developer stage')
            graph = {nid: set(n.get('dependsOn', [])) for nid,n in nodes.items()}
            for test in tests: graph[test['nodeId']].update(test['covers'])
            done = set()
            while len(done) < len(nodes):
                ready = {nid for nid, deps in graph.items() if nid not in done and deps <= done}
                require(ready, 'Independent testing coverage creates a dependency cycle')
                done.update(ready)
            criteria = {key: criteria[key] for key in ['path','version','sha256','criterionIds']}
            source = {key: source[key] for key in ['source','reference']}
            tests = [{'nodeId': test['nodeId'], 'covers': test['covers']} for test in tests]
            for planned in nodes.values():
                current_inputs(root, bundle, planned, config)
            approval = {'planHash': plan_snapshot(bundle), 'planRevision': bundle['plan']['planRevision'], 'criteria': criteria, 'customerApproval': source, 'requiredNodes': required, 'independentTests': tests, 'acceptedBy': authority['roleId'], 'authorityHashes': {k: authority[k+'Sha256'] for k in ['card','boundary']}, 'recordedAt': now()}
            previous = bundle['state'].get('planAcceptance', {})
            require(not previous or previous['criteria'] == criteria, 'Criteria changes require a new reviewed task')
            if previous and previous['planHash'] == approval['planHash']:
                require(all(previous[key] == approval[key] for key in ['criteria','requiredNodes','independentTests','customerApproval']), 'Current plan already accepted; changed acceptance scope requires a new reviewed task')
                return {'status': 'duplicate', 'stateRevision': bundle['state']['stateRevision']}
            revision = bundle['state'].get('revisionReview', {})
            if previous.get('criteria') == criteria and revision.get('unaffectedReason'):
                carried = {}
                for nid in revision.get('unaffected', []):
                    planned, state = node_pair(bundle, nid)
                    if state['status'] == 'verified' and state.get('acceptance', {}).get('verdict') == 'pass':
                        evidence_valid(root, bundle, planned, state, config)
                        carried[nid] = sha(encoded(state['acceptance']))
                approval['carriedAcceptances'] = carried
                approval['unaffectedReview'] = revision
            bundle['state']['planAcceptance'] = approval
            return store.commit(bundle, 'plan-accepted', 'Independent acceptance approved current plan and criteria')
        if command == 'revise':
            document=request.get('document','design')
            require(document in {'design','requirement'},'Only design or requirement revisions are supported')
            permission='allowDesignRevision' if document=='design' else 'allowRequirementRevision'
            require(config.get(permission) is True, document+' revisions are not preauthorized in the pinned configuration')
            require(request.get('reason') and request.get('version'), 'Revision version and reason required')
            require(request['version'] != bundle['plan'][document]['version'], 'Use a new design revision')
            # Revision can change prerequisite edges, never role identity, checks or write authority.
            changes=request.get('dependencies', {})
            require(isinstance(changes,dict),'dependencies must map node IDs to prerequisite arrays')
            nodes={n['nodeId']:n for n in bundle['plan']['nodes']}
            for nid,deps in changes.items():
                require(nid in nodes and isinstance(deps,list) and all(d in nodes for d in deps),'Invalid revised prerequisite')
                nodes[nid]['dependsOn']=deps
            done=set()
            while len(done)<len(nodes):
                ready={i for i,n in nodes.items() if i not in done and set(n.get('dependsOn',[]))<=done}
                require(ready,'Revised execution graph contains a cycle')
                done|=ready
            affected=set(request['affected'])|set(changes); require(affected, 'Affected stage IDs required')
            all_ids={n['nodeId'] for n in bundle['plan']['nodes']};require(affected <= all_ids,'Unknown affected stage')
            changed=True
            while changed:
                before=len(affected)
                for n in bundle['plan']['nodes']:
                    if set(n.get('dependsOn',[])) & affected:affected.add(n['nodeId'])
                changed=len(affected)!=before
            require(affected==all_ids or request.get('unaffectedReason'), 'Explain why other stages are unaffected')
            ref=bundle['plan'][document];digest=file_hash(root,ref['path']);require(digest and digest!=ref['sha256'],'Design document must actually change')
            old_digest=ref['sha256'];ref.update(version=request['version'],sha256=digest);bundle['plan']['planRevision']+=1
            for nid in affected:
                planned,state=node_pair(bundle,nid)
                planned['revisions'][document]=request['version'];planned['documentHashes'][document]=digest
                state['assignedRevisions']=dict(planned['revisions']);state['status']='blocked' if state['active'] else 'pending'
                state['pauseRequested']=bool(state['active']);state['reason']='Design changed; reconcile and acknowledge new assignment'
                state['checkEvidence']={};state.pop('verifiedCandidate',None)
                state.pop('acceptance', None)
                state['nextAction']={'summary':'Stop old attempt, then redispatch against revised design','responsibleRole':planned['roleId']}
            # Unaffected nodes acknowledge that the new document was reviewed as non-impacting.
            for n in bundle['plan']['nodes']:
                if n['nodeId'] not in affected and n['documentHashes'][document]==old_digest:n['documentHashes'][document]=digest
            bundle['state']['revisionReview'] = {'affected': sorted(affected), 'unaffected': sorted(all_ids-affected), 'unaffectedReason': request.get('unaffectedReason')}
            return store.commit(bundle,'design-revised' if document=='design' else 'requirement-change-accepted',request['reason'],extra={'affected':sorted(affected),'unaffectedReason':request.get('unaffectedReason')})
        planned,state=node_pair(bundle,node_id);role=config['roles'][planned['roleId']]
        if command in {'ack','stop','run-check','report'}:
            store.producer = producer(planned, state)
        if command == 'dispatch':
            accepted_plan(root, bundle, config)
            current_inputs(root,bundle,planned,config)
            require(not state['active'] and state['status']!='verified','Stage already active or verified')
            capacity=config.get('maxConcurrentWorkers',4)
            require(type(capacity) is int and capacity>0,'Invalid worker capacity')
            require(sum(bool(n.get('active')) for n in bundle['state']['nodes'])<capacity,'Worker capacity exhausted')
            if state['status'] in {'failed','blocked'}:require(request.get('retryReason'),'Retry requires a concrete changed condition')
            require(isinstance(request.get('workerId'),str) and request['workerId'],'workerId required')
            for other in bundle['state']['nodes']:
                if other.get('active'):
                    require(other['workerId']!=request['workerId'],'Worker is locked to another active stage')
                    op,_=node_pair(bundle,other['nodeId']);require(not set(op['writeSet']) & set(planned['writeSet']),'Concurrent write conflict')
            for dep in planned.get('dependsOn', []):
                valid_pass(root, bundle, dep, config)
            authorization={'kind':'configuration','sha256':bundle['plan']['configHash']}
            if role.get('autoDispatch') is not True:
                consent_path=request.get('consentPath')
                if request.get('consent') is not None:
                    require(consent_path is None, 'Provide consent inline or by path, not both')
                    consent=request['consent']
                    require(isinstance(consent,dict) and sha(encoded(consent))==request.get('approvedConsentSha256'), 'Consent hash not approved')
                else:
                    require(consent_path,'Customer consent required: automatic dispatch is not authorized')
                    consent=read(root,consent_path)
                    require(file_hash(root,consent_path)==request.get('approvedConsentSha256'),'Consent hash not approved')
                expected={'taskId':task,'nodeId':node_id,'roleId':planned['roleId'],'workerId':request['workerId'],'operation':planned['operation'],'writeSet':planned['writeSet'],'planRevision':bundle['plan']['planRevision'],'attemptNumber':state['attemptNumber']+1}
                require(all(consent.get(k)==v for k,v in expected.items()),'Consent does not match this activation')
                authorization={'kind':'explicit-consent','sha256':request['approvedConsentSha256']}
                if consent_path:
                    authorization['path']=consent_path
            if state.get('attemptId'):state.setdefault('previousAttempts',[]).append({'attemptId':state['attemptId'],'workerId':state['workerId'],'assignmentCredentialHash':state['assignmentCredentialHash']})
            state.pop('acceptance', None);state.pop('latestReport', None)
            token=secrets.token_urlsafe(32);state['attemptNumber']+=1
            state.update(attemptId=node_id+'-'+str(state['attemptNumber']),workerId=request['workerId'],assignmentCredentialHash=sha(token.encode()),status='running',active=True,pauseRequested=False,acknowledgedRevisions=None,checkEvidence={},authorization=authorization)
            state['assignedRevisions']=dict(planned['revisions']);state['reason']='Awaiting worker revision acknowledgment'
            result=store.commit(bundle,'assigned','Authorized worker assignment',node_id)
            result['assignment']={'taskId':task,'nodeId':node_id,'roleId':planned['roleId'],'attemptId':state['attemptId'],'workerId':state['workerId'],'token':token,'revisions':state['assignedRevisions'],'writeSet':planned['writeSet'],'card':role['card'],'boundary':role['boundary']}
            return result
        if command == 'ack':
            authenticate(state,request,False);current_inputs(root,bundle,planned,config)
            require(not state.get('pauseRequested') and request.get('revisions')==state['assignedRevisions'],'Cannot acknowledge stale or paused assignment')
            state['acknowledgedRevisions']=dict(request['revisions']);state['reason']=''
            return store.commit(bundle,'revision-acknowledged','Worker acknowledged assigned versions',node_id)
        if command == 'stop':
            authenticate(state,request,False);require(request.get('summary'),'Stop acknowledgment requires a summary')
            state.update(active=False,status='pending' if state.get('pauseRequested') else 'blocked',pauseRequested=False,reason=request['summary'])
            return store.commit(bundle,'stopped',request['summary'],node_id)
        if command == 'run-check':
            require(state.get('acceptance', {}).get('verdict') != 'needs-work', 'Needs-work requires stop and a new authorized attempt')
            authenticate(state,request);current_inputs(root,bundle,planned,config)
            check_id=request['checkId'];require(check_id in planned['checks'],'Check not assigned')
            check=role['checks'][check_id];before=candidate(root,bundle,planned)
            timeout=check.get('timeoutSeconds',60);require(type(timeout) is int and 1<=timeout<=300,'Check timeout must be 1..300 seconds')
            path=safe(root,(store.folder/'evidence'/(state['attemptId']+'-'+check_id+'-'+secrets.token_hex(4)+'.log')).relative_to(root).as_posix());path.parent.mkdir(exist_ok=True)
            timed_out=False;started=now()
            actual = execution_environment(check)
            runtime = environment_identity(root, check, actual)
            snapshot = save_environment_snapshot(root, task, state, check_id, check, actual)
            # Deliberately no shell. This command is pinned in the reviewed configuration.
            with path.open('wb') as output:
                try:
                    require(runtime['executable'] and runtime['executableHash'], 'Check executable unavailable')
                    proc=subprocess.run(check['argv'],executable=runtime['executable'],cwd=root,stdout=output,stderr=subprocess.STDOUT,timeout=timeout,env=actual)
                    code=proc.returncode
                except subprocess.TimeoutExpired:
                    code=124;timed_out=True
                except (OSError, Rejected) as exc:
                    output.write(('Check could not execute: '+str(exc)+'\n').encode())
                    code=127
            after=candidate(root,bundle,planned)
            evidence={'checkId':check_id,'argv':check['argv'],'exitCode':code,'timedOut':timed_out,'candidate':before,'candidateUnchanged':before==after,'path':path.relative_to(root).as_posix(),'sha256':sha(path.read_bytes()),'recordedAt':now()}
            evidence.update(producer=producer(planned, state), environment=runtime, environmentVersion=2, environmentSnapshot=snapshot, configHash=bundle['plan']['configHash'], startedAt=started, finishedAt=now())
            evidence['environmentUnchanged'] = bool(runtime['executableHash']) and runtime == environment_identity(root, check, actual) and file_hash(root, snapshot['path']) == snapshot['sha256']
            state.setdefault('checkHistory', []).append(evidence)
            state['checkEvidence'][check_id]=evidence
            if code or before!=after or not evidence['environmentUnchanged']:state.update(status='failed',reason='Check failed or changed the candidate')
            result=store.commit(bundle,'check-passed' if code==0 and before==after and evidence['environmentUnchanged'] else 'verification-failed','Executed approved check '+check_id,node_id,{'evidence':evidence});result['evidence']=evidence
            if code or before!=after or not evidence['environmentUnchanged']:result['status']='check-failed'
            return result
        if command == 'report':
            report_id=request.get('reportId');require(isinstance(report_id,str) and report_id,'reportId required')
            known=[state,*state.get('previousAttempts',[])]
            require(any(a.get('attemptId')==request.get('attemptId') and a.get('workerId')==request.get('workerId') and secrets.compare_digest(a.get('assignmentCredentialHash',''),sha(str(request.get('token','')).encode())) for a in known),'Unknown worker report')
            store.producer = {'roleId': planned['roleId'], 'nodeId': node_id, 'workerId': request['workerId'], 'attemptId': request['attemptId']}
            digest=sha(encoded({k:v for k,v in request.items() if k!='token'}))
            receipts=bundle['state']['reportReceipts']
            if report_id in receipts:
                require(receipts[report_id]['digest']==digest,'Conflicting duplicate report ID')
                return {'status':'duplicate',**receipts[report_id]}
            try:
                authenticate(state,request);current_inputs(root,bundle,planned,config)
                require(set(request.get('changedPaths',[]))<=set(planned['writeSet']),'Reported changes exceed write scope')
            except Rejected as exc:
                # Only retain authenticated old/current worker feedback; do not accept arbitrary writes.
                known=[state,*state.get('previousAttempts',[])]
                require(any(a.get('attemptId')==request.get('attemptId') and a.get('workerId')==request.get('workerId') and secrets.compare_digest(a.get('assignmentCredentialHash',''),sha(str(request.get('token','')).encode())) for a in known),'Unknown worker report')
                receipts[report_id]={'digest':digest,'accepted':False,'reason':str(exc)}
                result=store.commit(bundle,'report-rejected','Stale or out-of-scope feedback retained',node_id,{'reportId':report_id,'reason':str(exc)});result.update(accepted=False,reason=str(exc));return result
            kind=request.get('kind');require(state.get('acceptance', {}).get('verdict') != 'needs-work' or kind != 'complete', 'Needs-work requires stop and a new authorized attempt');require(kind in {'progress','issue','complete'},'Unknown report kind')
            require(isinstance(request.get('summary'),str) and request['summary'],'Report summary required')
            state['latestReport']={'reportId':report_id,'summary':request['summary'],'revisions':request['revisions'],'candidate':candidate(root,bundle,planned),'kind':kind,'attemptId':state['attemptId']}
            if kind=='issue':state.update(status='blocked',reason=request['summary'],nextAction={'summary':request['summary'],'responsibleRole':'project'})
            elif kind=='complete':state.update(status='awaiting-verification',reason='Awaiting current evidence verification')
            receipts[report_id]={'digest':digest,'accepted':True,'nodeId':node_id}
            return store.commit(bundle,{'progress':'progress','issue':'issue-reported','complete':'implementation-reported'}[kind],request['summary'],node_id,{'reportId':report_id})
        if command == 'verify':
            approval = accepted_plan(root, bundle, config)
            current_inputs(root, bundle, planned, config)
            require(state['status'] == 'awaiting-verification' and state['active'] and not state.get('pauseRequested'), 'Stage is not awaiting verification')
            require(request.get('attemptId') == state['attemptId'], 'Stale acceptance attempt')
            current = candidate(root, bundle, planned)
            require(request.get('candidate') == current, 'Stale acceptance candidate')
            criteria = approval['criteria']
            require(request.get('criteriaVersion') == criteria['version'] and request.get('criteriaSha256') == criteria['sha256'], 'Stale acceptance criteria')
            verdict = request.get('verdict')
            require(verdict in {'pass','needs-work','missing-evidence'} and isinstance(request.get('summary'), str) and request['summary'], 'Explicit verdict and summary required')
            results = acceptance_results(root, bundle, planned, state, request, approval)
            dependencies = set(planned.get('dependsOn', []))
            for test in approval['independentTests']:
                if test['nodeId'] == node_id: dependencies.update(test['covers'])
            if verdict == 'pass':
                for dep in dependencies: valid_pass(root, bundle, dep, config)
                evidence_valid(root, bundle, planned, state, config)
            acceptance = {'verdict': verdict, 'summary': request['summary'], 'criteriaResults': results, 'candidate': current, 'attemptId': state['attemptId'], 'planAcceptanceHash': sha(encoded(approval)), 'reportId': state.get('latestReport', {}).get('reportId'), 'evidenceHash': sha(encoded(state['checkEvidence'])), 'acceptedBy': bundle['state']['acceptanceAuthority']['roleId'], 'recordedAt': now(), 'dependencyAcceptances': {dep: sha(encoded(node_pair(bundle, dep)[1].get('acceptance'))) for dep in sorted(dependencies)}}
            state.setdefault('acceptanceHistory', []).append(acceptance)
            state['acceptance'] = acceptance
            if verdict == 'pass':
                state.update(status='verified', active=False, verifiedCandidate=current, reason='', nextAction={'summary':'Release eligible dependents','responsibleRole':config.get('schedulerRoleId','scheduler')})
            elif verdict == 'needs-work':
                state.update(status='blocked', reason=request['summary'])
            else:
                state.update(status='awaiting-verification', reason=request['summary'])
            return store.commit(bundle, 'verification-'+verdict, request['summary'], node_id)
        raise Rejected('Unknown command')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--task')
    parser.add_argument('command',choices=['init','status','recover','dispatch','ack','run-check','report','stop','revise','accept-plan','verify','preflight-role'])
    parser.add_argument('--request',type=Path,help='Request file, or - to read JSON from standard input; keep worker tokens private')
    args=parser.parse_args(argv)
    try:
        request=json.loads(sys.stdin.read() if str(args.request) == '-' else args.request.read_text()) if args.request else {}
        require(args.root.is_dir(),'Project root missing')
        require(args.command == 'preflight-role' or args.task is not None, '--task required for task commands')
        result=operate(args.root,args.task,args.command,request)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        if result.get('status') == 'rejected':
            return 2
        if result.get('accepted') is False:
            return 3
        if result.get('status') == 'check-failed':
            return 4
        return 0
    except (Rejected,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'rejected','message':str(exc)},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
