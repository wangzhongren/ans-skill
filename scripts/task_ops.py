#!/usr/bin/env python3
"""Local authorization-gated task operations; does not spawn agents or sandbox source writes."""
import argparse
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
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


def roles_valid(root, config):
    require(config.get('schemaVersion') == 1 and isinstance(config.get('roles'), dict), 'Invalid configuration')
    ownership = {}
    for role_id, role in config['roles'].items():
        require(isinstance(role, dict), 'Invalid role configuration')
        for key in ['card', 'boundary']:
            require(file_hash(root, role[key]), 'Missing role '+key)
        require(isinstance(role.get('writeFiles'), list), 'writeFiles must be exact file paths')
        boundary = safe(root, role['boundary']).read_text()
        # Only backtick paths inside table rows of Section 1 are recognized by v1.
        lines = boundary.splitlines(); section = []; active = False
        for line in lines:
            if line.lstrip().startswith('#'):
                is_section = 'section 1' in line.lower() or '第 1 节' in line or '第1节' in line
                if active and not is_section:
                    break
                if is_section:
                    active = True
            if active and line.lstrip().startswith('|'):
                section.append(line)
        boundary_paths = set()
        import re
        for line in section:
            boundary_paths.update(re.findall(r'`([^`]+)`', line))
        for path in role['writeFiles']:
            safe(root, path)
            require(path in boundary_paths, 'Configured write file is absent from boundary Section 1: '+path)
            require(path not in ownership, 'Duplicate file owner: '+path)
            require(not path.startswith(('.ans/', 'docs/scheduling/', 'role-cards/', '角色卡/')), 'Execution scope cannot include governance/state files')
            ownership[path] = role_id
        require(isinstance(role.get('operations'), list), 'Role operations required')
        for check_id, check in role.get('checks', {}).items():
            require(check_id and all(c.isalnum() or c in '-_' for c in check_id), 'Invalid check ID')
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
    ids = {planned['nodeId']}; todo = list(planned.get('dependsOn', []))
    while todo:
        key = todo.pop()
        if key in ids: continue
        ids.add(key); n,_ = node_pair(bundle,key);todo.extend(n.get('dependsOn', []))
    paths = set()
    for n in bundle['plan']['nodes']:
        if n['nodeId'] in ids: paths.update(n['writeSet']); paths.update(n.get('readSet',[]))
    return sha(encoded({p:file_hash(root,p) for p in sorted(paths)}))


def authenticate(state, request, acknowledged=True):
    require(state.get('attemptId') == request.get('attemptId') and state.get('workerId') == request.get('workerId'), 'Stale attempt or wrong worker')
    token = request.get('token', '')
    require(isinstance(token,str) and secrets.compare_digest(state.get('tokenHash',''),sha(token.encode())), 'Invalid assignment token')
    require(state.get('active'), 'Assignment is not active')
    if acknowledged:
        require(request.get('revisions') == state['assignedRevisions'] == state.get('acknowledgedRevisions'), 'Revision mismatch or missing acknowledgment')
        require(not state.get('pauseRequested'), 'Assignment paused for revision')


def status(bundle):
    result = json.loads(json.dumps(bundle['state']))
    result.pop('coordinatorTokenHash',None)
    for node in result['nodes']:
        node.pop('tokenHash',None);node.pop('previousAttempts',None)
    return {'status':'ok','state':result}


def operate(root, task, command, request):
    store = Store(root,task); root=store.root
    with store.locked():
        if command == 'init':
            require(not store.journal(), 'Task already initialized')
            require(not any((store.folder/name).exists() for name in ['plan.json','state.json']), 'Existing unmanaged records must not be overwritten')
            config_path=request.get('configPath','.ans/project.json');config=read(root,config_path)
            plan=normalize_plan(root,request['plan'],config,config_path,request['approvedConfigSha256'],task)
            states=[{'nodeId':n['nodeId'],'roleId':n['roleId'],'status':'pending','attemptId':None,'active':False,'assignedRevisions':n['revisions'],'acknowledgedRevisions':None,'checkEvidence':{},'attemptNumber':0} for n in plan['nodes']]
            coordinator_token=request.get('coordinatorToken') or secrets.token_urlsafe(32)
            require(isinstance(coordinator_token,str) and len(coordinator_token)>=32,'Coordinator token must be at least 32 characters')
            bundle={'plan':plan,'state':{'schemaVersion':1,'taskId':task,'planRevision':1,'nodes':states,'reportReceipts':{},'coordinatorTokenHash':sha(coordinator_token.encode())}}
            result=store.commit(bundle,'initialized','Reviewed plan and configuration pinned')
            result['coordinatorToken']=coordinator_token
            return result
        if command in {'dispatch','revise','verify','recover'}:
            history=store.journal();require(history,'Task not initialized')
            expected=history[-1]['after']['state'].get('coordinatorTokenHash')
            require(expected is not None,'Legacy task is read-only; initialize a new task with coordinator credentials')
            supplied=request.get('coordinatorToken','')
            require(isinstance(supplied,str) and secrets.compare_digest(expected,sha(supplied.encode())),'Coordinator credential required')
        bundle=store.load(recover=command=='recover')
        if command in {'status','recover'}:return status(bundle)
        config=config_for(root,bundle); roles_valid(root,config)
        node_id=request.get('nodeId')
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
                state['nextAction']={'summary':'Stop old attempt, then redispatch against revised design','responsibleRole':planned['roleId']}
            # Unaffected nodes acknowledge that the new document was reviewed as non-impacting.
            for n in bundle['plan']['nodes']:
                if n['nodeId'] not in affected and n['documentHashes'][document]==old_digest:n['documentHashes'][document]=digest
            return store.commit(bundle,'design-revised' if document=='design' else 'requirement-change-accepted',request['reason'],extra={'affected':sorted(affected),'unaffectedReason':request.get('unaffectedReason')})
        planned,state=node_pair(bundle,node_id);role=config['roles'][planned['roleId']]
        if command == 'dispatch':
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
            for dep in planned.get('dependsOn',[]):
                dp,ds=node_pair(bundle,dep);require(ds['status']=='verified','Prerequisite is not verified: '+dep)
                current_inputs(root,bundle,dp,config)
                require(ds.get('verifiedCandidate')==candidate(root,bundle,dp),'Prerequisite evidence is stale: '+dep)
            authorization={'kind':'configuration','sha256':bundle['plan']['configHash']}
            if role.get('autoDispatch') is not True:
                consent_path=request.get('consentPath');require(consent_path,'Customer consent required: automatic dispatch is not authorized')
                consent=read(root,consent_path);require(file_hash(root,consent_path)==request.get('approvedConsentSha256'),'Consent hash not approved')
                expected={'taskId':task,'nodeId':node_id,'roleId':planned['roleId'],'workerId':request['workerId'],'operation':planned['operation'],'writeSet':planned['writeSet'],'planRevision':bundle['plan']['planRevision'],'attemptNumber':state['attemptNumber']+1}
                require(all(consent.get(k)==v for k,v in expected.items()),'Consent does not match this activation')
                authorization={'kind':'explicit-consent','path':consent_path,'sha256':request['approvedConsentSha256']}
            if state.get('attemptId'):state.setdefault('previousAttempts',[]).append({'attemptId':state['attemptId'],'workerId':state['workerId'],'tokenHash':state['tokenHash']})
            token=secrets.token_urlsafe(32);state['attemptNumber']+=1
            state.update(attemptId=node_id+'-'+str(state['attemptNumber']),workerId=request['workerId'],tokenHash=sha(token.encode()),status='running',active=True,pauseRequested=False,acknowledgedRevisions=None,checkEvidence={},authorization=authorization)
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
            authenticate(state,request);current_inputs(root,bundle,planned,config)
            check_id=request['checkId'];require(check_id in planned['checks'],'Check not assigned')
            check=role['checks'][check_id];before=candidate(root,bundle,planned)
            timeout=check.get('timeoutSeconds',60);require(type(timeout) is int and 1<=timeout<=300,'Check timeout must be 1..300 seconds')
            path=safe(root,(store.folder/'evidence'/(state['attemptId']+'-'+check_id+'-'+secrets.token_hex(4)+'.log')).relative_to(root).as_posix());path.parent.mkdir(exist_ok=True)
            timed_out=False
            # Deliberately no shell. This command is pinned in the reviewed configuration.
            with path.open('wb') as output:
                try:
                    proc=subprocess.run(check['argv'],cwd=root,stdout=output,stderr=subprocess.STDOUT,timeout=timeout,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
                    code=proc.returncode
                except subprocess.TimeoutExpired:
                    code=124;timed_out=True
            after=candidate(root,bundle,planned)
            evidence={'checkId':check_id,'argv':check['argv'],'exitCode':code,'timedOut':timed_out,'candidate':before,'candidateUnchanged':before==after,'path':path.relative_to(root).as_posix(),'sha256':sha(path.read_bytes()),'recordedAt':now()}
            state['checkEvidence'][check_id]=evidence
            if code or before!=after:state.update(status='failed',reason='Check failed or changed the candidate')
            result=store.commit(bundle,'check-passed' if code==0 and before==after else 'verification-failed','Executed approved check '+check_id,node_id,{'evidence':evidence});result['evidence']=evidence
            if code or before!=after:result['status']='check-failed'
            return result
        if command == 'report':
            report_id=request.get('reportId');require(isinstance(report_id,str) and report_id,'reportId required')
            known=[state,*state.get('previousAttempts',[])]
            require(any(a.get('attemptId')==request.get('attemptId') and a.get('workerId')==request.get('workerId') and secrets.compare_digest(a.get('tokenHash',''),sha(str(request.get('token','')).encode())) for a in known),'Unknown worker report')
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
                require(any(a.get('attemptId')==request.get('attemptId') and a.get('workerId')==request.get('workerId') and secrets.compare_digest(a.get('tokenHash',''),sha(str(request.get('token','')).encode())) for a in known),'Unknown worker report')
                receipts[report_id]={'digest':digest,'accepted':False,'reason':str(exc)}
                result=store.commit(bundle,'report-rejected','Stale or out-of-scope feedback retained',node_id,{'reportId':report_id,'reason':str(exc)});result.update(accepted=False,reason=str(exc));return result
            kind=request.get('kind');require(kind in {'progress','issue','complete'},'Unknown report kind')
            require(isinstance(request.get('summary'),str) and request['summary'],'Report summary required')
            state['latestReport']={'reportId':report_id,'summary':request['summary'],'revisions':request['revisions'],'candidate':candidate(root,bundle,planned)}
            if kind=='issue':state.update(status='blocked',reason=request['summary'],nextAction={'summary':request['summary'],'responsibleRole':'project'})
            elif kind=='complete':state.update(status='awaiting-verification',reason='Awaiting current evidence verification')
            receipts[report_id]={'digest':digest,'accepted':True,'nodeId':node_id}
            return store.commit(bundle,{'progress':'progress','issue':'issue-reported','complete':'implementation-reported'}[kind],request['summary'],node_id,{'reportId':report_id})
        if command == 'verify':
            current_inputs(root,bundle,planned,config)
            require(state['status']=='awaiting-verification' and not state.get('pauseRequested'),'Stage is not awaiting verification')
            current=candidate(root,bundle,planned)
            for output in planned.get('requiredOutputs',planned['writeSet']):
                require(file_hash(root,output) is not None,'Missing required output: '+output)
            require(state.get('latestReport',{}).get('candidate')==current,'Implementation changed after completion report')
            for check_id in planned['checks']:
                evidence=state['checkEvidence'].get(check_id);require(evidence is not None,'Missing required check: '+check_id)
                require(evidence['exitCode']==0 and evidence['candidateUnchanged'] and evidence['candidate']==current,'Required check failed or evidence is stale')
                require(file_hash(root,evidence['path'])==evidence['sha256'],'Evidence artifact changed')
            state.update(status='verified',active=False,verifiedCandidate=current,reason='',nextAction={'summary':'Release eligible dependents','responsibleRole':'project'})
            return store.commit(bundle,'verification-passed','All assigned checks passed for the current candidate',node_id)
        raise Rejected('Unknown command')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--task',required=True)
    parser.add_argument('command',choices=['init','status','recover','dispatch','ack','run-check','report','stop','revise','verify'])
    parser.add_argument('--request',type=Path,help='JSON request file; contains assignment token for worker operations')
    args=parser.parse_args(argv)
    try:
        request=json.loads(args.request.read_text()) if args.request else {}
        require(args.root.is_dir(),'Project root missing')
        result=operate(args.root,args.task,args.command,request)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 3 if result.get('accepted') is False else 4 if result.get('status')=='check-failed' else 0
    except (Rejected,OSError,ValueError,KeyError,TypeError) as exc:
        print(json.dumps({'status':'rejected','message':str(exc)},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
