"""Independent QA: invoke the actual task CLI in isolated projects.

Set ANS_QA_LOG_DIR to retain isolated projects and redacted JSONL CLI transcripts.
No production operate()/developer test helper is imported.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[2]
CLI = REPO / 'scripts/task_ops.py'
BASELINE = '6a7d4fe'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def redacted(value):
    if isinstance(value, dict):
        return {k: ('<redacted>' if any(s in k.lower() for s in ('token', 'credential')) else redacted(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redacted(v) for v in value]
    return value


class RoleAuthorityCLIFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.retained = os.environ.get('ANS_QA_LOG_DIR')
        cls.scratch = Path(tempfile.mkdtemp(prefix='ans-independent-qa-', dir=cls.retained)).resolve()
        cls.old = cls.scratch / 'baseline'
        cls.old.mkdir()
        manifest = {'baseline': BASELINE, 'files': {}, 'commands': []}
        for name in ('task_ops.py', 'coordination_store.py'):
            argv = ['git', 'show', BASELINE + ':scripts/' + name]
            proc = subprocess.run(argv, cwd=REPO, capture_output=True, check=True)
            (cls.old / name).write_bytes(proc.stdout)
            manifest['commands'].append({'argv': argv, 'exitCode': proc.returncode})
            manifest['files'][name] = digest(proc.stdout)
        (cls.scratch / 'baseline-manifest.json').write_text(json.dumps(manifest, indent=2))
        print('Independent QA artifacts: ' + str(cls.scratch), flush=True)

    @classmethod
    def tearDownClass(cls):
        if not cls.retained:
            shutil.rmtree(cls.scratch)

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix=self._testMethodName + '-', dir=self.scratch))
        self.task = 'qa-task'
        self.scheduler = 'fixture-scheduler-' + 's' * 40
        self.acceptance = 'fixture-acceptance-' + 'v' * 40
        self.transcript = self.root / 'cli-transcript.jsonl'
        for path, value in {'docs/requirements.md': 'R1: independent acceptance',
                            'docs/design.md': 'D1: approved isolated CLI design',
                            'docs/criteria.md': 'C1: actual outputs and required checks',
                            'src/a.txt': 'developer output', 'src/b.txt': 'build output',
                            'test/result.txt': 'independent test output',
                            'checks/check.py': 'print("real subprocess check")\n'}.items():
            self.put(path, value)
        roles = {}
        for role, path in [('developer', 'src/a.txt'), ('builder', 'src/b.txt'), ('tester', 'test/result.txt')]:
            card = 'role-cards/' + role + '/role-card.md'
            boundary = 'role-cards/' + role + '/boundary.md'
            self.put(card, '# ' + role)
            self.put(boundary, '# Section 1\n| file | `' + path + '` | owner |\n')
            roles[role] = {'card': card, 'boundary': boundary, 'writeFiles': [path],
                           'operations': ['implement'], 'autoDispatch': True,
                           'checks': {'check': {'argv': [sys.executable, 'checks/check.py'], 'timeoutSeconds': 3}}}
        roles['tester']['purpose'] = 'independent-test'
        self.put('role-cards/acceptance/role-card.md', '# independent acceptance')
        self.put('role-cards/acceptance/boundary.md', '# Section 1\n| file | `docs/criteria.md` | criteria |\n')
        authority = {'roleId': 'acceptance', 'card': 'role-cards/acceptance/role-card.md',
                     'boundary': 'role-cards/acceptance/boundary.md',
                     'credentialHash': digest(self.acceptance.encode()), 'criteriaFiles': ['docs/criteria.md']}
        for key in ('card', 'boundary'):
            authority[key + 'Sha256'] = self.hash(authority[key])
        self.config = {'schemaVersion': 1, 'roles': roles, 'acceptanceAuthority': authority,
                       'designFiles': ['docs/design.md'], 'allowDesignRevision': True,
                       'allowRequirementRevision': True, 'maxConcurrentWorkers': 4}
        self.plan = {'schemaVersion': 1, 'taskId': self.task,
                     'requirement': {'path': 'docs/requirements.md', 'version': 'R1'},
                     'design': {'path': 'docs/design.md', 'version': 'D1'},
                     'nodes': [self.node('a', 'developer', 'src/a.txt', [], ['checks/check.py']),
                               self.node('b', 'builder', 'src/b.txt', ['a'], ['checks/check.py']),
                               self.node('t', 'tester', 'test/result.txt', ['b'], ['src/a.txt', 'src/b.txt', 'checks/check.py'])]}

    @staticmethod
    def node(node, role, path, deps, reads):
        return {'nodeId': node, 'roleId': role, 'stage': 'verification' if role == 'tester' else 'implementation',
                'operation': 'implement', 'writeSet': [path], 'readSet': reads,
                'checks': ['check'], 'dependsOn': deps}

    def put(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        return target

    def hash(self, path):
        return digest((self.root / path).read_bytes())

    @property
    def record(self):
        return self.root / 'docs/scheduling' / (self.task + '.md')

    def request_init(self):
        self.put('.ans/project.json', json.dumps(self.config))
        return {'configPath': '.ans/project.json', 'approvedConfigSha256': self.hash('.ans/project.json'),
                'plan': self.plan, 'schedulerToken': self.scheduler}

    def cli(self, command, request=None, code=0, old=False, env=None, prefix=None):
        script = self.old / 'task_ops.py' if old else CLI
        argv = (prefix or [sys.executable, str(script)]) + ['--root', str(self.root), '--task', self.task, command, '--request', '-']
        proc = subprocess.run(argv, input=json.dumps(request or {}), text=True, capture_output=True,
                              cwd=REPO, env=env, timeout=25)
        try:
            result = json.loads(proc.stdout)
        except ValueError:
            result = {'unparsedStdout': proc.stdout}
        with self.transcript.open('a') as log:
            log.write(json.dumps({'argv': argv, 'request': redacted(request or {}), 'exitCode': proc.returncode,
                                  'stdout': redacted(result), 'stderr': proc.stderr}, ensure_ascii=False) + '\n')
        self.assertEqual(proc.returncode, code, (command, redacted(result), proc.stderr))
        return result

    def reject(self, command, request, old=False, message=None):
        before = self.record.read_bytes() if self.record.exists() else None
        result = self.cli(command, request, code=2, old=old)
        after = self.record.read_bytes() if self.record.exists() else None
        self.assertEqual(before, after, 'Rejected CLI mutated task document')
        if message:
            self.assertIn(message.lower(), result['message'].lower())
        return result

    def initialize(self, accept=True):
        result = self.cli('init', self.request_init())
        self.assertEqual(result['schedulerToken'], self.scheduler)
        if accept:
            self.approve()
        return result

    def snapshot(self):
        return self.cli('status')['state']

    def state(self, node='a'):
        return next(n for n in self.snapshot()['nodes'] if n['nodeId'] == node)

    def approval_request(self):
        state = self.snapshot()
        return {'acceptanceToken': self.acceptance, 'stateRevision': state['stateRevision'],
                'planRevision': state['planRevision'],
                'criteria': {'path': 'docs/criteria.md', 'version': 'C1', 'sha256': self.hash('docs/criteria.md'), 'criterionIds': ['C1']},
                'customerApproval': {'source': 'isolated test operator', 'reference': 'authorized QA fixture only'},
                'requiredNodes': [n['nodeId'] for n in self.plan['nodes']],
                'independentTests': [{'nodeId': 't', 'covers': [n['nodeId'] for n in self.plan['nodes'] if n['nodeId'] != 't']}]}

    def approve(self):
        return self.cli('accept-plan', self.approval_request())

    def dispatch(self, node='a', **extra):
        result = self.cli('dispatch', {'schedulerToken': self.scheduler, 'nodeId': node, 'workerId': 'worker-' + node, **extra})
        assignment = result['assignment']
        self.cli('ack', assignment)
        return assignment

    def report(self, assignment, report='done', **extra):
        return self.cli('report', {**assignment, 'reportId': assignment['attemptId'] + '-' + report,
                                  'kind': 'complete', 'summary': 'actual current candidate done', **extra})

    def ready(self, assignment):
        result = self.cli('run-check', {**assignment, 'checkId': 'check'})
        self.report(assignment)
        return result

    def verify_request(self, node='a', verdict='pass'):
        snapshot = self.snapshot()
        state = next(n for n in snapshot['nodes'] if n['nodeId'] == node)
        criteria = snapshot['planAcceptance']['criteria']
        refs = [{'kind': 'report', 'reportId': state['latestReport']['reportId']}] if verdict == 'pass' else []
        return {'acceptanceToken': self.acceptance, 'stateRevision': snapshot['stateRevision'], 'nodeId': node,
                'attemptId': state['attemptId'], 'candidate': state['currentCandidate'],
                'criteriaVersion': criteria['version'], 'criteriaSha256': criteria['sha256'], 'verdict': verdict,
                'summary': 'independent QA fixture verdict: ' + verdict,
                'criteriaResults': [{'criterionId': 'C1', 'verdict': verdict, 'evidence': refs,
                                     'summary': 'current output/check reviewed' if verdict == 'pass' else 'required evidence or implementation incomplete'}]}

    def verify(self, node='a', verdict='pass'):
        return self.cli('verify', self.verify_request(node, verdict))

    def finish(self, node):
        assignment = self.dispatch(node)
        self.ready(assignment)
        self.verify(node)
        return assignment

    def registered_project(self, custom=False):
        """Declare fixture roles independently of role IDs and grant only their docs."""
        definitions = {}
        bindings = {**self.config['roles'], 'acceptance': self.config['acceptanceAuthority']}
        for role_id in ['developer', 'builder', 'tester', 'acceptance', 'scheduler', 'planning']:
            if role_id in bindings:
                binding = bindings[role_id]
                root = str(Path(binding['card']).parent)
            else:
                root = 'role-cards/' + role_id
                binding = {'card': root + '/role-card.md', 'boundary': root + '/boundary.md'}
                self.put(binding['card'], '# fixture ' + role_id)
                self.put(binding['boundary'], '# Section 1\n')
            if custom and role_id == 'developer':
                root = '角色卡/能力甲'
                for key, name in [('card', 'identity.md'), ('boundary', 'scope.md')]:
                    content = (self.root / binding[key]).read_text()
                    binding[key] = root + '/' + name
                    self.put(binding[key], content)
            core = [root + '/' + name for name in ['feature-map.md', 'memo.md', 'functional-description.md']]
            for path in core:
                self.put(path, '# fixture work document')
            boundary = (self.root / binding['boundary']).read_text()
            for path in core + [root + '/docs/design/', root + '/docs/change/']:
                boundary += '\n| scope | `' + path + '` | fixture owner |'
            if role_id == 'scheduler':
                for path in ['.ans/project.json', '.ans/runtime/', 'docs/scheduling/']:
                    boundary += '\n| scope | `' + path + '` | management only |'
            self.put(binding['boundary'], boundary + '\n')
            definitions[role_id] = {'card': binding['card'], 'boundary': binding['boundary'],
                                    'requiredWorkDocuments': core, 'apiSpec': 'not-applicable',
                                    'apiSpecReason': 'This fixture role exposes no inter-role code interface.'}
        self.config['schedulerRoleId'] = 'scheduler'
        self.config['roleDefinitions'] = definitions
        for key in ['card', 'boundary']:
            authority = self.config['acceptanceAuthority']
            authority[key + 'Sha256'] = self.hash(authority[key])
        return definitions

    def project_tree(self):
        snapshot = {}
        for path in self.root.rglob('*'):
            relative = path.relative_to(self.root).as_posix()
            if path.is_symlink():
                snapshot[relative] = ('symlink', os.readlink(path))
            elif path.is_file():
                snapshot[relative] = ('file', self.hash(relative), path.stat().st_mode & 0o777)
            else:
                snapshot[relative] = ('directory', path.stat().st_mode & 0o777)
        return snapshot

    def role_preflight(self, code=0, request=None):
        self.put('.ans/project.json', json.dumps(self.config))
        argv = [sys.executable, str(CLI), '--root', str(self.root), 'preflight-role', '--request', '-']
        payload = {'configPath': '.ans/project.json'} if request is None else request
        before = self.project_tree()
        result = subprocess.run(argv, input=json.dumps(payload), text=True, capture_output=True,
                                cwd=REPO, timeout=25)
        self.assertEqual(self.project_tree(), before, 'Preflight itself changed the project tree')
        parsed = json.loads(result.stdout)
        with self.transcript.open('a') as stream:
            stream.write(json.dumps({'argv': argv, 'request': redacted(payload), 'exitCode': result.returncode,
                                     'stdout': redacted(parsed), 'stderr': result.stderr}, ensure_ascii=False) + '\n')
        self.assertEqual(result.returncode, code, redacted(parsed))
        return parsed

    def test_role_preflight_is_readonly_and_missing_permission_is_not_missing_content(self):
        definitions = self.registered_project()
        developer = definitions['developer']
        future = 'role-cards/developer/docs/design/future.md'
        developer['requiredWorkDocuments'].append(future)
        result = self.role_preflight()
        documents = next(role['documents'] for role in result['roles'] if role['roleId'] == 'developer')
        document = next(item for item in documents if item['path'] == future)
        self.assertFalse(document['exists'])
        self.assertTrue(document['permissionGranted'])
        missing = developer['requiredWorkDocuments'][1]
        boundary = developer['boundary']
        original = (self.root / boundary).read_text()
        self.put(boundary, '\n'.join(line for line in original.splitlines() if '`' + missing + '`' not in line))
        result = self.role_preflight(2)
        self.assertFalse(result['permissionsComplete'])
        issue = next(role for role in result['roles'] if role['roleId'] == 'developer')['issues']
        self.assertTrue(any(item.get('path') == missing for item in issue))
        self.reject('init', self.request_init(), message='preflight')
        self.assertFalse(self.record.exists())
        self.put(boundary, original)
        self.role_preflight()
        self.role_preflight(2, {'configPath': '.ans/project.json', 'schedulerToken': self.scheduler})

    def test_role_preflight_requires_explicit_api_and_complete_matching_registration(self):
        definitions = self.registered_project()
        developer = definitions['developer']
        developer['apiSpec'] = 'required'
        self.role_preflight(2)
        api = 'role-cards/developer/api-spec.md'
        developer['requiredWorkDocuments'].append(api)
        self.role_preflight(2)
        self.put(developer['boundary'], (self.root / developer['boundary']).read_text() + '\n| file | `' + api + '` | API |\n')
        self.role_preflight()
        for role_id in ['scheduler', 'acceptance', 'builder']:
            with self.subTest(missingRole=role_id):
                saved = definitions.pop(role_id)
                self.role_preflight(2)
                definitions[role_id] = saved
        saved = developer['card']
        developer['card'] = 'role-cards/builder/role-card.md'
        self.role_preflight(2)
        developer['card'] = saved
        developer['apiSpecReason'] = ''
        self.role_preflight(2)

    def test_registered_custom_role_documents_run_full_actual_cli_flow(self):
        definitions = self.registered_project(custom=True)
        paths = ['角色卡/能力甲/memo.md', 'role-cards/builder/docs/change/new.md',
                 'role-cards/tester/docs/change/independent.md']
        for node, role_id, path in zip(self.plan['nodes'], ['developer', 'builder', 'tester'], paths):
            self.config['roles'][role_id]['writeFiles'] = [path]
            node['writeSet'] = [path]
            reads = [path]
            if role_id == 'tester':
                node['readSet'] = paths[:2] + ['checks/check.py']
                reads = paths
            program = 'from pathlib import Path;assert all(Path(p).read_text() == "approved-document-content" for p in ' + repr(reads) + ')'
            self.config['roles'][role_id]['checks']['check']['argv'] = [sys.executable, '-c', program]
        self.role_preflight()
        self.initialize()
        for node, path in zip(['a', 'b', 't'], paths):
            assignment = self.dispatch(node)
            self.put(path, 'approved-document-content')
            self.ready(assignment)
            self.verify(node)
        self.assertTrue(self.snapshot()['taskComplete'])
        self.assertEqual(definitions['developer']['card'], '角色卡/能力甲/identity.md')
        self.assertEqual(self.state('t')['checkEvidence']['check']['producer']['roleId'], 'tester')
        self.reject('run-check', {**self.state('t'), 'checkId': 'check'})

    def test_role_documents_still_require_exact_task_scope_and_registration(self):
        self.registered_project()
        permitted = 'role-cards/developer/docs/design/new.md'
        self.config['roles']['developer']['writeFiles'] = [permitted]
        self.plan['nodes'][0]['writeSet'] = [permitted]
        self.role_preflight()
        self.plan['nodes'][0]['writeSet'] = ['role-cards/developer/docs/design/other.md']
        self.reject('init', self.request_init(), message='scope')
        self.plan['nodes'][0]['writeSet'] = [permitted]
        self.config.pop('roleDefinitions')
        rejected = self.reject('init', self.request_init())
        self.assertIn(permitted, rejected['message'])
        self.assertRegex(rejected['message'], 'boundary Section 1|governance/state')

    def test_preflight_detects_unselected_cross_role_ownership_and_governance(self):
        self.registered_project()
        developer_boundary = self.config['roles']['developer']['boundary']
        original = (self.root / developer_boundary).read_text()
        for path in ['role-cards/builder/memo.md', 'role-cards/builder/docs/',
                     'role-cards/developer/', 'test/', 'src/', '.ans/unselected.md',
                     'docs/scheduling/unselected.md']:
            with self.subTest(scope=path):
                self.put(developer_boundary, original + '\n| scope | `' + path + '` | illegal |\n')
                self.role_preflight(2)
        self.put(developer_boundary, original)
        self.put('role-cards/developer/docs/change/nested/boundary.yaml', 'source: governance')
        self.role_preflight(2)

    def test_all_registered_governance_and_state_files_rejected_as_execution_files(self):
        for path in ['role-cards/developer/role-card.md', 'role-cards/developer/boundary.md',
                     'role-cards/developer/boundary.yaml', 'role-cards/developer/changelog.md',
                     'role-cards/planning/memo.md', 'role-cards/acceptance/role-card.md',
                     '.ans/extra.md', 'docs/scheduling/other.md', 'role-cards/developer/docs/change/']:
            with self.subTest(path=path):
                self.setUp()
                self.registered_project()
                self.config['roles']['developer']['writeFiles'] = [path]
                self.plan['nodes'][0]['writeSet'] = [path]
                self.reject('init', self.request_init())

    def test_custom_governance_in_allowed_test_tree_and_nested_roots_are_protected(self):
        definitions = self.registered_project()
        planning = definitions['planning']
        for key, name in [('card', 'charter.md'), ('boundary', 'limits.md')]:
            planning[key] = 'test/fixtures/planning/' + name
            self.put(planning[key], '# fixture' if key == 'card' else '# Section 1\n')
        root = 'test/fixtures/planning'
        planning['requiredWorkDocuments'] = [root + '/' + name for name in ['feature-map.md', 'memo.md', 'functional-description.md']]
        self.put(planning['boundary'], '# Section 1\n' + '\n'.join('| file | `' + path + '` | own |' for path in planning['requiredWorkDocuments']))
        self.role_preflight()
        boundary = self.config['roles']['developer']['boundary']
        self.put(boundary, (self.root / boundary).read_text() + '\n| directory | `test/fixtures/` | unsafe |\n')
        self.role_preflight(2)
        definitions['planning']['card'] = 'role-cards/developer/docs/planning/card.md'
        definitions['planning']['boundary'] = 'role-cards/developer/docs/planning/limits.md'
        self.put(definitions['planning']['card'], '# nested')
        self.put(definitions['planning']['boundary'], '# Section 1\n')
        self.role_preflight(2)

    def test_role_document_canonical_prefix_and_symlink_boundaries(self):
        self.registered_project()
        role = self.config['roles']['developer']
        for path in ['role-cards/developer/docs/design/../change/a.md', './role-cards/developer/memo.md',
                     '/tmp/qa-outside.md', 'role-cards\\developer\\memo.md',
                     'role-cards/developer/docs/design-other/a.md']:
            with self.subTest(path=path):
                role['writeFiles'] = [path]
                self.plan['nodes'][0]['writeSet'] = [path]
                self.reject('init', self.request_init())
        target = self.put('outside.md', 'fixture only')
        leaf = self.root / 'role-cards/developer/docs/design/link.md'
        leaf.parent.mkdir(parents=True, exist_ok=True)
        leaf.symlink_to(target)
        role['writeFiles'] = [leaf.relative_to(self.root).as_posix()]
        self.plan['nodes'][0]['writeSet'] = role['writeFiles']
        self.reject('init', self.request_init(), message='symlink')
        leaf.unlink()
        parent = self.root / 'role-cards/developer/docs/design/linked'
        parent.symlink_to(self.root, target_is_directory=True)
        role['writeFiles'] = [parent.relative_to(self.root).as_posix() + '/future.md']
        self.plan['nodes'][0]['writeSet'] = role['writeFiles']
        self.reject('init', self.request_init(), message='symlink')

    def test_v2_different_query_path_preserves_verify_dependency_and_completion(self):
        self.initialize()
        assignment = self.dispatch()
        evidence = self.ready(assignment)['evidence']
        snapshot = self.hash(evidence['environmentSnapshot']['path'])
        query = {**os.environ, 'PATH': str(self.root / 'unused-query-bin') + os.pathsep + os.environ.get('PATH', os.defpath)}
        self.assertNotEqual(digest(query['PATH'].encode()), digest(os.environ.get('PATH', '').encode()))
        self.cli('verify', self.verify_request(), env=query)
        state = self.cli('status', env=query)['state']
        self.assertTrue(next(node for node in state['nodes'] if node['nodeId'] == 'a')['currentAcceptanceValid'])
        assignment = self.cli('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'different-terminal'}, env=query)['assignment']
        self.cli('ack', assignment, env=query)
        self.ready(assignment)
        self.verify('b')
        self.finish('t')
        state = self.cli('status', env=query)['state']
        self.assertTrue(state['taskComplete'])
        self.assertEqual(snapshot, self.hash(evidence['environmentSnapshot']['path']))
        self.assertEqual(len(state['nodes'][0]['checkHistory']), 1)

    def test_v2_private_snapshot_absent_keys_and_no_environment_values_in_task(self):
        check = self.config['roles']['developer']['checks']['check']
        check['env'] = {'QA_DECLARED_PRIVATE': 'synthetic-private-marker'}
        self.initialize()
        assignment = self.dispatch()
        environment = {**os.environ, 'QA_UNTRACKED_PRIVATE': 'synthetic-untracked-marker'}
        environment.pop('NODE_OPTIONS', None)
        evidence = self.cli('run-check', {**assignment, 'checkId': 'check'}, env=environment)['evidence']
        reference = evidence['environmentSnapshot']
        path = self.root / reference['path']
        self.assertEqual(evidence['environmentVersion'], 2)
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)
        self.assertEqual(path.parent.parent.stat().st_mode & 0o777, 0o700)
        snapshot = json.loads(path.read_text())
        self.assertIn('NODE_OPTIONS', snapshot['absentKeys'])
        self.assertNotIn('QA_UNTRACKED_PRIVATE', snapshot['values'])
        self.assertEqual(snapshot['values']['QA_DECLARED_PRIVATE'], 'synthetic-private-marker')
        public = self.record.read_text() + json.dumps(self.snapshot())
        self.assertNotIn('synthetic-private-marker', public)
        self.assertNotIn('synthetic-untracked-marker', public)
        self.assertNotIn('declaredEnvironment"', public)
        self.report(assignment)
        self.verify()

    def test_v2_snapshot_loss_or_tampering_invalidates_transitive_pass_without_fallback(self):
        self.initialize()
        self.finish('a')
        evidence = self.state()['checkEvidence']['check']
        snapshot = self.root / evidence['environmentSnapshot']['path']
        saved = snapshot.read_bytes()
        for replacement in [None, b'{}', saved + b'\n']:
            with self.subTest(change='missing' if replacement is None else digest(replacement)):
                if replacement is None:
                    snapshot.unlink()
                else:
                    snapshot.write_bytes(replacement)
                state = self.state()
                self.assertFalse(state['currentAcceptanceValid'])
                self.assertIn('snapshot', state['currentAcceptanceReason'].lower())
                self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'blocked'})
                snapshot.write_bytes(saved)
                self.assertTrue(self.state()['currentAcceptanceValid'])
        self.assertEqual(evidence['environmentSnapshot']['sha256'], self.hash(evidence['environmentSnapshot']['path']))

    def test_v2_real_readset_resource_config_and_executable_target_changes_invalidate(self):
        resource = self.put('checks/runtime-resource.txt', 'resource-one')
        configuration = self.put('checks/probe-config.txt', 'config-one')
        self.plan['nodes'][0]['readSet'] += ['checks/runtime-resource.txt', 'checks/probe-config.txt']
        for path in ['checks/runtime-resource.txt', 'checks/probe-config.txt']:
            self.plan['nodes'][2]['readSet'].append(path)
        self.initialize()
        self.finish('a')
        for path in [resource, configuration]:
            saved = path.read_bytes()
            path.write_bytes(saved + b'changed')
            self.assertFalse(self.state()['currentAcceptanceValid'])
            self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'resource-change'})
            path.write_bytes(saved)
        self.assertTrue(self.state()['currentAcceptanceValid'])
        saved = (self.root / '.ans/project.json').read_bytes()
        self.config['roles']['developer']['checks']['check']['env'] = {'QA_FLAG': 'actual-new-environment'}
        self.put('.ans/project.json', json.dumps(self.config))
        state = self.snapshot()
        self.assertFalse(state['taskComplete'])
        self.assertIn('configuration', state['currentValidityReason'].lower())
        (self.root / '.ans/project.json').write_bytes(saved)
        self.assertTrue(self.state()['currentAcceptanceValid'])

    def test_v2_selected_executable_symlink_target_change_and_inflight_mutation_fail(self):
        first = self.put('tools/first', '#!/bin/sh\nprintf fixture-ok\n')
        second = self.put('tools/second', '#!/bin/sh\nprintf fixture-ok\n')
        first.chmod(0o755)
        second.chmod(0o755)
        selected = self.root / 'tools/selected'
        selected.symlink_to(first)
        self.config['roles']['developer']['checks']['check']['argv'] = [str(selected)]
        self.initialize()
        self.finish('a')
        selected.unlink()
        selected.symlink_to(second)
        self.assertEqual(digest(first.read_bytes()), digest(second.read_bytes()))
        self.assertFalse(self.state()['currentAcceptanceValid'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'different-executable'})
        selected.unlink()
        selected.symlink_to(first)
        self.assertTrue(self.state()['currentAcceptanceValid'])
        self.setUp()
        executable = self.put('tools/self-changing', '#!/bin/sh\nprintf "# mutation\\n" >> "$0"\n')
        executable.chmod(0o755)
        self.config['roles']['developer']['checks']['check']['argv'] = [str(executable)]
        self.initialize()
        assignment = self.dispatch()
        result = self.cli('run-check', {**assignment, 'checkId': 'check'}, code=4)
        self.assertFalse(result['evidence']['environmentUnchanged'])
        self.report(assignment)
        self.reject('verify', self.verify_request())

    def test_legacy_hash_only_evidence_is_not_upgraded_by_new_queries(self):
        legacy = self.root / 'legacy-tools'
        legacy.mkdir()
        for name in ['task_ops.py', 'coordination_store.py']:
            result = subprocess.run(['git', 'show', 'd95d006:scripts/' + name], cwd=REPO,
                                    capture_output=True, check=True)
            (legacy / name).write_bytes(result.stdout)
        self.initialize()
        assignment = self.dispatch()
        evidence = self.cli('run-check', {**assignment, 'checkId': 'check'},
                            prefix=[sys.executable, str(legacy / 'task_ops.py')])['evidence']
        self.assertNotIn('environmentVersion', evidence)
        self.report(assignment)
        self.verify()
        before = self.record.read_bytes()
        query = {**os.environ, 'PATH': str(self.root / 'legacy-query') + os.pathsep + os.environ.get('PATH', os.defpath)}
        state = self.cli('status', env=query)['state']
        self.assertFalse(state['nodes'][0]['currentAcceptanceValid'])
        self.assertEqual(before, self.record.read_bytes())
        self.assertFalse((self.root / '.ans/runtime/check-environments').exists())

    def test_environment_snapshot_write_failure_cannot_create_a_pass(self):
        self.initialize()
        assignment = self.dispatch()
        injection = ('import os,runpy,sys;from unittest.mock import patch;'
                     'sys.path.insert(0,' + repr(str(CLI.parent)) + ');'
                     'sys.argv=[' + repr(str(CLI)) + ']+sys.argv[1:];original=os.replace;'
                     'exec("def guarded(source,destination):\\n'
                     ' if \'check-environments\' in str(destination): raise OSError(\'QA snapshot write failure\')\\n'
                     ' return original(source,destination)\\n");'
                     'patch("os.replace",side_effect=guarded).start();'
                     'runpy.run_path(' + repr(str(CLI)) + ',run_name="__main__")')
        before = self.record.read_bytes()
        self.cli('run-check', {**assignment, 'checkId': 'check'}, code=2,
                 prefix=[sys.executable, '-c', injection])
        self.assertEqual(before, self.record.read_bytes())
        self.assertEqual(self.state()['checkEvidence'], {})
        self.report(assignment)
        self.reject('verify', self.verify_request())

    def test_init_does_not_mint_acceptance_and_rejects_override_or_equal_secret(self):
        base = self.request_init()
        for key, value in [('acceptanceToken', self.acceptance), ('coordinatorToken', self.scheduler),
                           ('acceptanceAuthority', self.config['acceptanceAuthority']), ('credentialHash', '0' * 64)]:
            with self.subTest(override=key):
                self.reject('init', {**base, key: value})
        self.reject('init', {**base, 'schedulerToken': self.acceptance}, message='different')
        saved = self.config.pop('acceptanceAuthority')
        self.reject('init', self.request_init(), message='acceptanceAuthority')
        self.config['acceptanceAuthority'] = saved
        result = self.initialize(False)
        self.assertEqual(set(result), {'status', 'stateRevision', 'eventId', 'schedulerToken'})
        self.assertNotIn(self.acceptance, self.record.read_text())
        self.assertNotIn(self.scheduler, self.record.read_text())

    def test_credentials_are_not_role_names_scopes_or_project_keys(self):
        self.initialize(False)
        for token in [self.scheduler, 'project-key-fixture', 'acceptance', '', 'forged-scope']:
            with self.subTest(tokenClass=token[:12]):
                self.reject('accept-plan', {**self.approval_request(), 'acceptanceToken': token, 'roleId': 'acceptance', 'scope': '*'}, message='credential')
        self.approve()
        a = self.dispatch()
        self.ready(a)
        for request in [{'schedulerToken': self.scheduler}, {'acceptanceToken': self.scheduler},
                        {'acceptanceToken': a['token']}, {'coordinatorToken': self.scheduler},
                        {'acceptanceToken': 'project-key-fixture', 'roleId': 'acceptance', 'scope': '*'}]:
            valid = self.verify_request()
            valid.pop('acceptanceToken')
            self.reject('verify', {**valid, **request}, message='credential')
        self.reject('accept-plan', {**self.approval_request(), 'acceptanceToken': a['token']})
        for command, request in [('dispatch', {'nodeId': 'b', 'workerId': 'w'}),
                                 ('revise', {'version': 'D2', 'affected': ['a'], 'reason': 'attempt'}), ('recover', {})]:
            self.reject(command, {**request, 'schedulerToken': self.acceptance}, message='credential')
            self.reject(command, {**request, 'coordinatorToken': self.scheduler}, message='credential')
            self.reject(command, {**request, 'schedulerToken': a['token']}, message='credential')
        for command in ['close', 'mint', 'reset']:
            self.reject(command, {'schedulerToken': self.scheduler})

    def test_accept_plan_required_complete_and_idempotent(self):
        self.initialize(False)
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'a', 'workerId': 'w'}, message='accept-plan')
        for field, value in [('independentTests', []), ('requiredNodes', ['a']), ('customerApproval', {})]:
            with self.subTest(field=field):
                self.reject('accept-plan', {**self.approval_request(), field: value})
        self.approve()
        before = self.record.read_bytes()
        self.assertEqual(self.approve()['status'], 'duplicate')
        self.assertEqual(before, self.record.read_bytes())

    def test_real_developer_builder_test_flow_and_event_producers(self):
        self.initialize()
        for node in ['a', 'b', 't']:
            a = self.dispatch(node)
            result = self.ready(a)
            state = self.state(node)
            self.assertEqual(state['status'], 'awaiting-verification')
            self.assertTrue(state['active'])
            self.assertFalse(self.snapshot()['taskComplete'])
            evidence = result['evidence']
            self.assertEqual(evidence['producer'], {k: a[k] for k in ['roleId', 'nodeId', 'workerId', 'attemptId']})
            self.assertEqual(evidence['argv'], [sys.executable, 'checks/check.py'])
            for key in ['startedAt', 'finishedAt', 'configHash', 'environment', 'sha256']:
                self.assertIn(key, evidence)
            self.verify(node)
            self.assertFalse(self.state(node)['active'])
        self.assertTrue(self.snapshot()['taskComplete'])
        raw = self.record.read_text()
        self.assertIn('| t | tester | verified |', raw)
        self.assertNotIn('coordinatorTokenHash', raw)
        self.assertNotIn('"tokenHash"', raw)
        block = raw.split('<!-- ANS-TASK-EVENTS-V1\n')[1].split('\nANS-TASK-EVENTS-END -->')[0]
        events = [json.loads(line) for line in block.splitlines()]
        self.assertEqual({e['producer']['roleId'] for e in events}, {'scheduler', 'acceptance', 'developer', 'builder', 'tester'})
        self.assertEqual(events[-1]['after']['state']['taskComplete'], True)

    def test_missing_evidence_retains_scope_allows_same_attempt_supplement(self):
        self.initialize()
        a = self.dispatch()
        self.report(a)
        self.reject('verify', self.verify_request(), message='check')
        self.verify(verdict='missing-evidence')
        state = self.state()
        self.assertEqual(state['status'], 'awaiting-verification')
        self.assertTrue(state['active'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'b'})
        self.cli('run-check', {**a, 'checkId': 'check'})
        self.report(a, 'supplement')
        self.verify()
        self.assertEqual([v['verdict'] for v in self.state()['acceptanceHistory']], ['missing-evidence', 'pass'])

    def test_needs_work_cannot_be_bypassed_without_stop_and_retry(self):
        self.initialize()
        a = self.dispatch()
        self.ready(a)
        self.verify(verdict='needs-work')
        self.assertTrue(self.state()['active'])
        self.assertEqual(self.state()['status'], 'blocked')
        self.reject('run-check', {**a, 'checkId': 'check'}, message='new authorized attempt')
        self.reject('report', {**a, 'reportId': 'forbidden-complete', 'kind': 'complete', 'summary': 'bypass'}, message='new authorized attempt')
        self.reject('verify', self.verify_request())
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'b'})
        self.cli('stop', {**a, 'summary': 'actual isolated worker exited'})
        self.assertFalse(self.state()['active'])
        self.assertFalse(self.snapshot()['taskComplete'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'a', 'workerId': 'a'}, message='retry')
        fresh = self.dispatch(retryReason='owner corrected issue and original worker stopped')
        self.assertNotEqual(a['attemptId'], fresh['attemptId'])
        self.cli('report', {**a, 'reportId': 'late-old-attempt', 'kind': 'complete', 'summary': 'late'}, code=3)
        self.ready(fresh)
        self.verify()
        self.assertEqual([x['verdict'] for x in self.state()['acceptanceHistory']], ['needs-work', 'pass'])
        raw = self.record.read_text()
        self.assertNotIn('"tokenHash"', raw)
        self.assertNotIn('coordinatorTokenHash', raw)

    def test_failure_history_timeout_and_candidate_mutating_check(self):
        cases = [('failed', 'raise SystemExit(7)\n', 7),
                 ('timeout', 'import time;time.sleep(2)\n', 124),
                 ('mutation', 'from pathlib import Path;Path("src/a.txt").write_text("changed")\n', 0)]
        for label, program, expected in cases:
            with self.subTest(case=label):
                self.task = 'case-' + label
                self.plan['taskId'] = self.task
                self.put('checks/check.py', program)
                self.config['roles']['developer']['checks']['check']['timeoutSeconds'] = 1
                self.initialize()
                a = self.dispatch()
                evidence = self.cli('run-check', {**a, 'checkId': 'check'}, code=4)['evidence']
                self.assertEqual(evidence['exitCode'], expected)
                self.assertEqual(evidence['timedOut'], label == 'timeout')
                self.assertEqual(evidence['candidateUnchanged'], label != 'mutation')
                self.report(a)
                self.reject('verify', self.verify_request())
                self.put('checks/check.py', 'print("corrected harness")\n')
                self.cli('run-check', {**a, 'checkId': 'check'})
                self.report(a, 'current')
                self.verify()
                self.assertEqual(len(self.state()['checkHistory']), 2)
                self.assertEqual(self.state()['checkHistory'][0]['exitCode'], expected)

    def test_candidate_output_harness_and_log_invalidation(self):
        self.initialize()
        a = self.dispatch()
        check = self.ready(a)['evidence']
        request = self.verify_request()
        for path in ['src/a.txt', 'checks/check.py']:
            saved = (self.root / path).read_bytes()
            self.put(path, 'changed after completion')
            self.reject('verify', request, message='candidate')
            (self.root / path).write_bytes(saved)
        output = self.root / 'src/a.txt'
        saved = output.read_bytes()
        output.unlink()
        self.reject('verify', self.verify_request(), message='output')
        output.write_bytes(saved)
        log = self.root / check['path']
        saved = log.read_bytes()
        log.write_bytes(saved + b'tampered')
        self.reject('verify', self.verify_request(), message='evidence')
        log.unlink()
        self.reject('verify', self.verify_request(), message='evidence')
        log.write_bytes(saved)
        self.verify()
        self.put('src/a.txt', 'new candidate after pass')
        self.assertFalse(self.snapshot()['taskComplete'])
        self.assertFalse(self.state()['currentAcceptanceValid'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'b'})

    def test_stale_state_criteria_role_authority_and_config_cannot_pass(self):
        self.initialize()
        a = self.dispatch()
        self.ready(a)
        request = self.verify_request()
        self.cli('report', {**a, 'reportId': 'fresh-complete', 'kind': 'complete', 'summary': 'new report'})
        self.reject('verify', request, message='stateRevision')
        for path in ['docs/criteria.md', 'role-cards/developer/role-card.md', 'role-cards/developer/boundary.md',
                     'role-cards/acceptance/role-card.md', '.ans/project.json']:
            with self.subTest(path=path):
                before = (self.root / path).read_bytes()
                request = self.verify_request()
                (self.root / path).write_bytes(before + b'\n')
                self.reject('verify', request)
                self.assertFalse(self.snapshot()['taskComplete'])
                (self.root / path).write_bytes(before)
        self.verify()

    def test_environment_snapshot_uses_merged_path_cwd_and_detects_binary_change(self):
        probe = self.put('tools/probe', '#!/bin/sh\nexec ' + sys.executable + ' -c \'import os,json;print(json.dumps({"cwd":os.getcwd(),"flag":os.getenv("QA_FLAG"),"bytecode":os.getenv("PYTHONDONTWRITEBYTECODE")}))\'\n')
        probe.chmod(0o755)
        check = self.config['roles']['developer']['checks']['check']
        check.update(argv=['probe'], env={'PATH': 'tools', 'QA_FLAG': 'merged-environment', 'PYTHONDONTWRITEBYTECODE': '0'})
        self.initialize()
        a = self.dispatch()
        evidence = self.ready(a)['evidence']
        observed = json.loads((self.root / evidence['path']).read_text())
        self.assertEqual(observed, {'cwd': str(self.root), 'flag': 'merged-environment', 'bytecode': '1'})
        self.assertEqual(evidence['environment']['executable'], str(probe))
        self.assertEqual(evidence['environment']['executableHash'], self.hash('tools/probe'))
        actual = {**os.environ, **check['env'], 'PYTHONDONTWRITEBYTECODE': '1'}
        variables = {key: actual.get(key) for key in ['PATH', 'PYTHONPATH', 'NODE_PATH', 'NODE_OPTIONS', 'LANG', 'LC_ALL', 'TZ', 'PYTHONDONTWRITEBYTECODE']}
        variables.update({key: actual[key] for key in check['env']})
        self.assertEqual(evidence['environment']['variablesHash'], digest(json.dumps(variables, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()))
        before = self.state()['currentCandidate']
        probe.write_text(probe.read_text() + '# binary changed\n')
        self.assertEqual(before, self.state()['currentCandidate'])
        self.reject('verify', self.verify_request(), message='environment')

    def test_ancestor_missing_log_invalidates_transitive_dependencies_and_completion(self):
        self.initialize()
        a = self.finish('a')
        self.finish('b')
        t = self.dispatch('t')
        self.ready(t)
        log = self.root / self.state('a')['checkEvidence']['check']['path']
        saved = log.read_bytes()
        direct_candidate = self.state('b')['currentCandidate']
        log.unlink()
        self.assertEqual(direct_candidate, self.state('b')['currentCandidate'])
        self.reject('verify', self.verify_request('t'), message='evidence')
        self.verify('t', 'missing-evidence')
        self.assertTrue(self.state('t')['active'])
        self.assertFalse(self.snapshot()['taskComplete'])
        self.assertFalse(self.state('b')['currentAcceptanceValid'])
        log.write_bytes(saved)
        self.verify('t')
        self.assertTrue(self.snapshot()['taskComplete'])
        log.unlink()
        self.assertFalse(self.snapshot()['taskComplete'])
        self.assertEqual(self.state('b')['acceptance']['verdict'], 'pass')

    def test_ancestor_log_loss_blocks_dispatch_and_allows_needs_work(self):
        self.initialize()
        self.finish('a')
        self.finish('b')
        log = self.root / self.state('a')['checkEvidence']['check']['path']
        saved = log.read_bytes()
        log.unlink()
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 't', 'workerId': 't'}, message='evidence')
        log.write_bytes(saved)
        t = self.dispatch('t')
        self.ready(t)
        log.unlink()
        self.verify('t', 'needs-work')
        self.assertEqual(self.state('t')['status'], 'blocked')
        self.assertTrue(self.state('t')['active'])

    def test_revision_invalidates_preflight_and_cannot_delete_dependencies_to_bypass(self):
        self.initialize()
        a = self.dispatch()
        self.ready(a)
        self.put('docs/design.md', 'D2: reviewed dependency correction')
        self.cli('revise', {'schedulerToken': self.scheduler, 'version': 'D2', 'affected': ['a'],
                            'dependencies': {'t': []}, 'reason': 'actual design change'})
        self.assertTrue(self.state()['active'])
        self.assertTrue(self.state()['pauseRequested'])
        self.cli('report', {**a, 'reportId': 'late-revision', 'kind': 'complete', 'summary': 'old design'}, code=3)
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 't', 'workerId': 't'}, message='accept-plan')
        self.approve()
        self.cli('stop', {**a, 'summary': 'old execution stopped'})
        t = self.dispatch('t')
        self.ready(t)
        self.reject('verify', self.verify_request('t'), message='verified')
        self.assertFalse(self.snapshot()['taskComplete'])

    def test_requirement_revision_transitively_invalidates_verified_nodes(self):
        self.initialize()
        self.finish('a')
        self.finish('b')
        self.put('docs/requirements.md', 'R2: changed required behavior')
        self.cli('revise', {'schedulerToken': self.scheduler, 'document': 'requirement', 'version': 'R2',
                            'affected': ['a'], 'reason': 'customer requirement changed'})
        self.assertEqual({n['status'] for n in self.snapshot()['nodes']}, {'pending'})
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'a', 'workerId': 'a'}, message='accept-plan')
        self.approve()
        self.assertFalse(self.snapshot()['taskComplete'])

    def test_unaffected_pass_requires_new_preflight_review(self):
        self.plan['nodes'][1]['dependsOn'] = []
        self.initialize()
        self.finish('a')
        self.put('docs/design.md', 'D2: builder-only correction')
        self.cli('revise', {'schedulerToken': self.scheduler, 'version': 'D2', 'affected': ['b'],
                            'reason': 'builder contract correction', 'unaffectedReason': 'developer contract and declared inputs unchanged'})
        self.assertFalse(self.state('a')['currentAcceptanceValid'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'b'}, message='accept-plan')
        self.approve()
        snapshot = self.snapshot()
        self.assertIn('a', snapshot['planAcceptance']['carriedAcceptances'])
        self.assertEqual(snapshot['planAcceptance']['unaffectedReview']['unaffected'], ['a'])
        self.assertTrue(self.state('a')['currentAcceptanceValid'])
        self.dispatch('b')

    def test_criteria_change_requires_new_task_not_reacceptance(self):
        self.initialize()
        self.put('docs/criteria.md', 'C2: materially different completion criteria')
        self.reject('accept-plan', self.approval_request(), message='new reviewed task')
        self.assertFalse(self.snapshot()['taskComplete'])

    def test_independent_test_readset_must_cover_tested_inputs(self):
        self.plan['nodes'][2]['readSet'] = ['src/b.txt', 'checks/check.py']
        self.initialize(False)
        self.reject('accept-plan', self.approval_request(), message='readSet')

    def test_external_logs_and_developer_checks_cannot_be_independent_test_evidence(self):
        self.initialize()
        self.finish('a')
        self.finish('b')
        t = self.dispatch('t')
        self.report(t)
        request = self.verify_request('t')
        developer_check = self.state('a')['checkEvidence']['check']
        request['criteriaResults'][0]['evidence'] = [{'kind': 'check', 'checkId': 'check', 'sha256': developer_check['sha256']}]
        self.reject('verify', request, message='check evidence')
        self.put('external-success.log', 'success')
        request['criteriaResults'][0]['evidence'] = [{'kind': 'output', 'path': 'external-success.log', 'sha256': self.hash('external-success.log')}]
        self.reject('verify', request, message='scope')
        self.reject('verify', self.verify_request('t'), message='check')
        self.ready(t)
        self.verify('t')
        self.assertEqual(self.state('t')['checkEvidence']['check']['producer']['roleId'], 'tester')

    def test_real_baseline_six_commands_cannot_write_v2(self):
        self.initialize()
        a = self.dispatch()
        self.ready(a)
        requests = [('dispatch', {'coordinatorToken': self.scheduler, 'nodeId': 'b', 'workerId': 'old'}),
                    ('verify', {'coordinatorToken': self.scheduler, 'nodeId': 'a'}), ('ack', a),
                    ('run-check', {**a, 'checkId': 'check'}),
                    ('report', {**a, 'reportId': 'old-tool', 'kind': 'complete', 'summary': 'old'}),
                    ('stop', {**a, 'summary': 'old stop'})]
        for command, request in requests:
            with self.subTest(oldCommand=command):
                self.reject(command, request, old=True)
        self.verify()

    def test_old_v1_actual_render_is_readonly_and_no_auto_release(self):
        request = self.request_init()
        request.pop('schedulerToken')
        old = self.cli('init', request, old=True)
        worker = self.cli('dispatch', {'coordinatorToken': old['coordinatorToken'], 'nodeId': 'a', 'workerId': 'old-worker'}, old=True)['assignment']
        self.cli('ack', worker, old=True)
        status = self.snapshot()
        self.assertTrue(status['legacyReadOnly'])
        self.assertFalse(status['taskComplete'])
        self.assertTrue(status['nodes'][0]['active'])
        for command in ['dispatch', 'verify', 'ack', 'run-check', 'report', 'stop', 'revise', 'recover', 'accept-plan']:
            self.reject(command, {**worker, 'coordinatorToken': old['coordinatorToken'], 'schedulerToken': self.scheduler,
                                  'acceptanceToken': self.acceptance}, message='read-only')
        self.assertNotIn('Token', json.dumps(status))
        self.assertNotIn('tokenHash', json.dumps(status))
        self.record.write_bytes(self.record.read_bytes().replace(b'\n', b'\r\n'))
        self.assertTrue(self.snapshot()['legacyReadOnly'])

    def test_legacy_json_readonly_redacts_history_and_rejects_leaf_symlinks(self):
        self.put('docs/scheduling/qa-task/plan.json', json.dumps(self.plan))
        state = {'schemaVersion': 1, 'taskId': self.task, 'nodes': [{'nodeId': 'a', 'active': True,
                 'tokenHash': 'legacy-hash', 'previousAttempts': [{'tokenHash': 'old-hash', 'assignmentCredentialHash': 'new-hash'}]}],
                 'coordinatorTokenHash': 'scheduler-hash'}
        self.put('docs/scheduling/qa-task/state.json', json.dumps(state))
        status = self.snapshot()
        self.assertTrue(status['nodes'][0]['active'])
        self.assertNotIn('hash', json.dumps(status))
        self.reject('stop', {'schedulerToken': self.scheduler}, message='read-only')
        self.reject('init', self.request_init(), message='JSON task records')
        for leaf in ['plan.json', 'state.json']:
            path = self.root / 'docs/scheduling/qa-task' / leaf
            saved = path.read_bytes()
            outside = self.root.parent / (self.root.name + '-' + leaf)
            outside.write_bytes(saved)
            path.unlink()
            path.symlink_to(outside)
            self.reject('status', {}, message='symlink')
            path.unlink()
            path.write_bytes(saved)

    def test_lock_atomic_failure_recover_and_duplicate_report_are_safe(self):
        import fcntl
        self.initialize()
        a = self.dispatch()
        lock = self.root / '.ans/runtime/qa-task/.lock'
        with lock.open('a+b') as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.reject('report', {**a, 'reportId': 'locked', 'kind': 'progress', 'summary': 'locked'}, message='active')
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
        # Inject only os.replace failure in a subprocess running the real CLI via runpy.
        injection = ('import os,runpy,sys;from unittest.mock import patch;'
                     'sys.path.insert(0,' + repr(str(CLI.parent)) + ');'
                     'sys.argv=[' + repr(str(CLI)) + ']+sys.argv[1:];'
                     'p=patch("os.replace",side_effect=OSError("QA atomic replacement failure"));p.start();'
                     'runpy.run_path(' + repr(str(CLI)) + ',run_name="__main__")')
        before = self.record.read_bytes()
        self.cli('report', {**a, 'reportId': 'atomic-failure', 'kind': 'progress', 'summary': 'fail replacement'}, code=2,
                 prefix=[sys.executable, '-c', injection])
        self.assertEqual(before, self.record.read_bytes())
        self.cli('recover', {'schedulerToken': self.scheduler})
        self.assertEqual(before, self.record.read_bytes())
        report = {**a, 'reportId': 'progress', 'kind': 'progress', 'summary': 'idempotent progress'}
        self.cli('report', report)
        before = self.record.read_bytes()
        self.assertEqual(self.cli('report', report)['status'], 'duplicate')
        self.assertEqual(before, self.record.read_bytes())
        self.reject('report', {**report, 'summary': 'conflicting duplicate'})
        self.record.write_bytes(before.replace(b'| running |', b'| verified |', 1))
        self.reject('recover', {'schedulerToken': self.scheduler}, message='edited')

    def test_git_copy_missing_local_logs_invalidates_current_pass(self):
        self.initialize()
        self.finish('a')
        original = self.root
        destination = self.root.parent / (self.root.name + '-copy')
        shutil.copytree(self.root, destination, ignore=shutil.ignore_patterns('runtime'))
        self.root = destination
        self.transcript = self.root / 'copy-cli-transcript.jsonl'
        self.assertEqual(self.state()['status'], 'verified')
        self.assertFalse(self.state()['currentAcceptanceValid'])
        self.reject('dispatch', {'schedulerToken': self.scheduler, 'nodeId': 'b', 'workerId': 'copy-worker'}, message='evidence')
        self.assertTrue((original / 'docs/scheduling/qa-task.md').exists())

    def test_dashboard_reads_real_cli_record_without_mutation(self):
        self.initialize()
        for node in ['a', 'b', 't']:
            self.finish(node)
        before = self.record.read_bytes()
        program = ('import json,sys;sys.path.insert(0,' + repr(str(REPO)) + ');'
                   'from dashboard.server import Dashboard;'
                   'print(json.dumps(Dashboard(sys.argv[1]).snapshot()))')
        argv = [sys.executable, '-c', program, str(self.root)]
        result = subprocess.run(argv, cwd=self.root, text=True, capture_output=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        snapshot = json.loads(result.stdout)
        self.assertEqual(snapshot['issues'], [])
        self.assertEqual({row['status'] for row in snapshot['tasks']}, {'verified'})
        self.assertEqual({row['nodeId'] for row in snapshot['tasks']}, {'a', 'b', 't'})
        self.assertEqual(before, self.record.read_bytes())
        (self.root / 'dashboard-read.json').write_text(json.dumps({'argv': argv, 'exitCode': result.returncode, 'snapshot': snapshot}, indent=2))

    def test_git_actual_cli_merges_separate_tasks_and_rejects_same_task_conflict(self):
        def git(root, *args, expected=0):
            argv = ['git', '-C', str(root), '-c', 'user.name=Independent QA', '-c', 'user.email=qa@example.invalid', *args]
            result = subprocess.run(argv, capture_output=True, text=True, timeout=20)
            with (self.scratch / 'git-transcript.jsonl').open('a') as stream:
                stream.write(json.dumps({'argv': argv, 'exitCode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}) + '\n')
            if expected is not None:
                self.assertEqual(result.returncode, expected, result.stderr)
            return result

        self.initialize()
        original = self.root
        git(original, 'init', '-q')
        git(original, 'add', '--', 'docs', 'src', 'test', 'checks', 'role-cards', '.ans/project.json')
        git(original, 'commit', '-qm', 'initial independent QA task')
        clone = self.scratch / (original.name + '-git-clone')
        git(self.scratch, 'clone', '-q', str(original), str(clone))
        self.task = 'local-task'
        self.plan['taskId'] = self.task
        self.initialize()
        git(original, 'add', '--', 'docs/scheduling/local-task.md')
        git(original, 'commit', '-qm', 'local independent task')

        self.root = clone
        self.transcript = clone / 'cli-transcript.jsonl'
        self.task = 'other-task'
        self.plan['taskId'] = self.task
        self.initialize()
        git(clone, 'add', '--', 'docs/scheduling/other-task.md')
        git(clone, 'commit', '-qm', 'other independent task')
        git(clone, 'fetch', '-q', str(original), 'HEAD')
        git(clone, 'merge', '-q', '--no-ff', 'FETCH_HEAD', '-m', 'merge separate tasks')
        self.assertEqual({p.stem for p in (clone / 'docs/scheduling').glob('*.md')}, {'qa-task', 'local-task', 'other-task'})
        self.task = 'local-task'
        self.snapshot()
        self.dispatch('a')
        git(clone, 'add', '--', 'docs/scheduling/local-task.md')
        git(clone, 'commit', '-qm', 'clone assignment')
        self.root = original
        self.transcript = original / 'cli-transcript.jsonl'
        self.dispatch('a')
        git(original, 'add', '--', 'docs/scheduling/local-task.md')
        git(original, 'commit', '-qm', 'original assignment')
        git(clone, 'fetch', '-q', str(original), 'HEAD')
        conflict = git(clone, 'merge', '--no-ff', 'FETCH_HEAD', '-m', 'must reject competing task', expected=None)
        self.assertNotEqual(conflict.returncode, 0)
        self.root = clone
        self.transcript = clone / 'cli-transcript.jsonl'
        self.reject('status', {}, message='invalid task event')


if __name__ == '__main__':
    unittest.main()
