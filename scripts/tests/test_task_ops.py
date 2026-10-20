import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from coordination_store import Store, Rejected, encoded, file_hash, sha
from task_ops import operate, roles_valid, preflight_role, environment

class TaskOpsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve();self.task='case'
  self.put('docs/requirements.md','R1');self.put('docs/design.md','D1');self.put('src/a.py','value=1');self.put('src/b.py','value=2')
  roles={}
  for r in ['a','b']:
   self.put('role-cards/'+r+'/role-card.md','# '+r)
   self.put('role-cards/'+r+'/boundary.md','# Section 1\n| file | `src/'+r+'.py` | owner |')
   roles[r]={'card':'role-cards/'+r+'/role-card.md','boundary':'role-cards/'+r+'/boundary.md','writeFiles':['src/'+r+'.py'],'operations':['implement'],'autoDispatch':True,'checks':{'ok':{'argv':[sys.executable,'-c','assert True']}}}
  self.acceptance='isolated-test-acceptance-secret-'+'a'*32
  self.put('role-cards/acceptance/role-card.md','# independent acceptance')
  self.put('role-cards/acceptance/boundary.md','# Section 1\n| file | `docs/criteria.md` | criteria |')
  self.put('docs/criteria.md','C1: current candidate and real check pass')
  roles['b']['purpose']='independent-test'
  self.config={'schemaVersion':1,'roles':roles,'designFiles':['docs/design.md'],'allowDesignRevision':True}
  self.plan={'schemaVersion':1,'taskId':self.task,'requirement':{'path':'docs/requirements.md','version':'R1'},'design':{'path':'docs/design.md','version':'D1'},'nodes':[{'nodeId':r,'roleId':r,'stage':'implementation','operation':'implement','writeSet':['src/'+r+'.py'],'checks':['ok'],'dependsOn':[] if r=='a' else ['a']} for r in ['a','b']]}
  self.initialize()
 def put(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value);return p
 def initialize(self, accept=True):
  self.config['acceptanceAuthority']={'roleId':'acceptance','card':'role-cards/acceptance/role-card.md','boundary':'role-cards/acceptance/boundary.md','cardSha256':file_hash(self.root,'role-cards/acceptance/role-card.md'),'boundarySha256':file_hash(self.root,'role-cards/acceptance/boundary.md'),'credentialHash':sha(self.acceptance.encode()),'criteriaFiles':['docs/criteria.md']}
  self.plan['nodes'][1]['readSet']=self.plan['nodes'][0]['writeSet']+self.plan['nodes'][0].get('readSet',[])
  self.put('.ans/project.json',json.dumps(self.config))
  self.request={'configPath':'.ans/project.json','approvedConfigSha256':file_hash(self.root,'.ans/project.json'),'plan':self.plan}
  self.scheduler=self.op('init',self.request)['schedulerToken']
  if accept:self.accept_plan()
 def op(self,command,request=None):
  request=dict(request or {})
  if command in {'dispatch','revise','recover'}:request['schedulerToken']=self.scheduler
  if command in {'accept-plan','verify'}:request['acceptanceToken']=self.acceptance
  if command == 'verify':
   state=self.state(request['nodeId']);approval=self.op('status')['state']['planAcceptance']
   request={'stateRevision':self.op('status')['state']['stateRevision'],'attemptId':state['attemptId'],'candidate':state['currentCandidate'],'criteriaVersion':approval['criteria']['version'],'criteriaSha256':approval['criteria']['sha256'],'verdict':'pass','summary':'independent stage acceptance','criteriaResults':[{'criterionId':'C1','verdict':'pass','evidence':[{'kind':'report','reportId':state.get('latestReport',{}).get('reportId')}]}],**request}
  return operate(self.root,self.task,command,request)
 def accept_plan(self):
  return self.op('accept-plan',{'stateRevision':self.op('status')['state']['stateRevision'],'planRevision':Store(self.root,self.task).load()['plan']['planRevision'],'criteria':{'path':'docs/criteria.md','version':'C1','sha256':file_hash(self.root,'docs/criteria.md'),'criterionIds':['C1']},'customerApproval':{'source':'isolated fixture operator','reference':'explicit unittest fixture scope'},'requiredNodes':['a','b'],'independentTests':[{'nodeId':'b','covers':['a']}]})
 def state(self,n='a'):return next(x for x in self.op('status')['state']['nodes'] if x['nodeId']==n)
 def dispatch(self,n='a'):
  a=self.op('dispatch',{'nodeId':n,'workerId':'worker-'+n})['assignment'];self.op('ack',a);return a
 def complete(self,a,report='complete'):
  self.op('run-check',{**a,'checkId':'ok'})
  self.op('report',{**a,'reportId':report,'kind':'complete','summary':'done','changedPaths':['src/'+a['nodeId']+'.py']})
  self.op('verify',{'nodeId':a['nodeId']})
 def test_worker_cannot_self_verify_or_dispatch(self):
  a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'});self.op('report',{**a,'reportId':'r','kind':'complete','summary':'done'})
  with self.assertRaises(Rejected):operate(self.root,self.task,'verify',{'nodeId':'a',**a})
  with self.assertRaises(Rejected):operate(self.root,self.task,'dispatch',{'nodeId':'b','workerId':'self','schedulerToken':a['token']})
  self.assertNotIn('coordinatorTokenHash',self.op('status')['state'])
 def test_lifecycle_and_dependency_release(self):
  with self.assertRaises(Rejected):self.dispatch('b')
  a=self.dispatch();self.complete(a);b=self.dispatch('b');self.complete(b,'b-done')
  self.assertTrue(all(n['status']=='verified' for n in self.op('status')['state']['nodes']))
 def test_configuration_and_boundary_pinning(self):
  self.put('.ans/project.json',json.dumps({**self.config,'extra':'tamper'}))
  with self.assertRaises(Rejected):self.dispatch()
 def test_dispatch_requires_explicit_consent_without_auto(self):
  self.task='manual';self.plan['taskId']=self.task;self.config['roles']['a']['autoDispatch']=False;self.initialize()
  with self.assertRaises(Rejected):self.dispatch()
  receipt={'taskId':self.task,'nodeId':'a','roleId':'a','workerId':'w','operation':'implement','writeSet':['src/a.py'],'planRevision':1,'attemptNumber':1}
  self.put('.ans/consent.json',json.dumps(receipt))
  result=self.op('dispatch',{'nodeId':'a','workerId':'w','consentPath':'.ans/consent.json','approvedConsentSha256':file_hash(self.root,'.ans/consent.json')})
  self.assertEqual(result['assignment']['roleId'],'a')
  self.op('stop',{**result['assignment'],'summary':'first activation stopped'})
  with self.assertRaises(Rejected):self.op('dispatch',{'nodeId':'a','workerId':'w','retryReason':'retry needs new consent','consentPath':'.ans/consent.json','approvedConsentSha256':file_hash(self.root,'.ans/consent.json')})
  next_receipt={**receipt,'attemptNumber':2}
  approved=sha(encoded(next_receipt))
  result=self.op('dispatch',{'nodeId':'a','workerId':'w','retryReason':'approved retry','consent':next_receipt,'approvedConsentSha256':approved})
  self.assertEqual(result['assignment']['attemptId'],'a-2')
  self.assertEqual(self.state()['authorization'],{'kind':'explicit-consent','sha256':approved})
 def test_worker_locked_and_revisions_required(self):
  a=self.op('dispatch',{'nodeId':'a','workerId':'worker'})['assignment']
  with self.assertRaises(Rejected):self.op('run-check',{**a,'checkId':'ok'})
  with self.assertRaises(Rejected):self.op('dispatch',{'nodeId':'a','workerId':'other'})
  with self.assertRaises(Rejected):self.op('ack',{**a,'revisions':{'design':'wrong'}})
 def test_duplicate_report_is_idempotent(self):
  a=self.dispatch();req={**a,'reportId':'r1','kind':'progress','summary':'working'}
  self.op('report',req);seq=self.op('status')['state']['lastEventSeq'];res=self.op('report',req)
  self.assertEqual(res['status'],'duplicate');self.assertEqual(seq,self.op('status')['state']['lastEventSeq'])
  with self.assertRaises(Rejected):self.op('report',{**req,'summary':'different'})
 def test_revision_holds_active_writer_and_rejects_old_report(self):
  a=self.dispatch();self.put('docs/design.md','D2 changed')
  self.op('revise',{'version':'D2','affected':['a'],'reason':'correct contract'})
  self.assertTrue(self.state()['active']);self.assertEqual(self.state('b')['assignedRevisions']['design'],'D2')
  with self.assertRaises(Rejected):self.dispatch()
  res=self.op('report',{**a,'reportId':'old','kind':'complete','summary':'late D1'})
  self.assertFalse(res['accepted']);self.assertNotEqual(self.state()['status'],'verified')
  self.op('stop',{**a,'summary':'Stopped old attempt'})
  self.accept_plan()
  fresh=self.dispatch();self.assertNotEqual(a['attemptId'],fresh['attemptId']);self.assertEqual(fresh['revisions']['design'],'D2')
 def test_failed_or_stale_evidence_never_verifies(self):
  a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'});self.op('report',{**a,'reportId':'done','kind':'complete','summary':'done'})
  self.put('src/a.py','value=3')
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'a'})
 def test_scope_escape_rejected(self):
  a=self.dispatch();res=self.op('report',{**a,'reportId':'bad','kind':'complete','summary':'bad','changedPaths':['src/b.py']})
  self.assertFalse(res['accepted']);self.assertEqual(self.state()['status'],'running')
 def test_atomic_write_failure_preserves_previous_record(self):
  a=self.dispatch()
  before=(Store(self.root,self.task).document).read_bytes()
  with patch.object(Store,'materialize',side_effect=OSError('simulated interrupted replacement')):
   with self.assertRaises(OSError):self.op('report',{**a,'reportId':'r','kind':'progress','summary':'saved in log'})
  self.assertEqual((Store(self.root,self.task).document).read_bytes(),before)
  recovered=self.op('recover');self.assertEqual(recovered['state']['nodes'][0]['status'],'running')
  self.assertNotIn('latestReport',recovered['state']['nodes'][0])
 def test_tamper_partial_record_and_lock(self):
  store=Store(self.root,self.task)
  with store.locked():
   with self.assertRaises(Rejected):
    with Store(self.root,self.task).locked():pass
  with store.document.open('ab') as f:f.write(b'partial')
  with self.assertRaises(Rejected):self.op('recover')
 def test_rejects_widened_plan_and_cycles(self):
  self.task='invalid';self.plan['taskId']=self.task;self.plan['nodes'][0]['writeSet'].append('src/b.py')
  with self.assertRaises(Rejected):self.initialize()
 def test_missing_checks_and_actual_failed_check(self):
  self.task='failure';self.plan['taskId']=self.task
  self.config['roles']['a']['checks']['ok']['argv']=[sys.executable,'-c','raise SystemExit(7)']
  self.initialize();a=self.dispatch()
  self.op('report',{**a,'reportId':'no-evidence','kind':'complete','summary':'claims completion'})
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'a'})
  result=self.op('run-check',{**a,'checkId':'ok'})
  self.assertEqual(result['status'],'check-failed');self.assertEqual(result['evidence']['exitCode'],7)
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'a'})
 def test_stale_prerequisite_blocks_dispatch(self):
  a=self.dispatch();self.complete(a);self.put('src/a.py','value=99')
  with self.assertRaises(Rejected):self.dispatch('b')
 def test_revised_graph_cycle_rejected_without_commit(self):
  seq=self.op('status')['state']['lastEventSeq'];self.put('docs/design.md','D2')
  with self.assertRaises(Rejected):self.op('revise',{'version':'D2','affected':['a'],'dependencies':{'a':['b']},'reason':'cycle'})
  self.assertEqual(self.op('status')['state']['lastEventSeq'],seq)
 def test_requirement_revision_needs_its_own_permission(self):
  self.put('docs/requirements.md','R2')
  with self.assertRaises(Rejected):self.op('revise',{'document':'requirement','version':'R2','affected':['a'],'reason':'new intent'})
 def test_generated_document_symlink_rejected(self):
  store=Store(self.root,self.task);record=store.document;saved=record.read_bytes();record.unlink()
  outside=Path(self.tmp.name).parent/'not-an-existing-ans-log'
  record.symlink_to(outside)
  with self.assertRaises(Rejected):self.op('recover')
  record.unlink();record.write_bytes(saved)
 def test_board_and_dashboard_agree(self):
  from serve_dashboard import Dashboard
  a=self.dispatch();self.complete(a)
  snapshot=Dashboard(self.root).snapshot();self.assertEqual(snapshot['issues'],[])
  self.assertEqual(next(n for n in snapshot['tasks'] if n['nodeId']=='a')['status'],'verified')
  document=Store(self.root,self.task).document
  self.assertIn('| a | a | verified |',document.read_text())
  self.assertEqual(list((self.root/'docs/scheduling').glob('*.md')),[document])
  self.assertFalse((self.root/'docs/scheduling/case/plan.json').exists())

 def test_two_tasks_have_separate_git_readable_records(self):
  first=Store(self.root,self.task).document
  self.task='second';self.plan['taskId']=self.task;self.initialize()
  second=Store(self.root,self.task).document
  self.assertEqual({p.name for p in first.parent.glob('*.md')},{'case.md','second.md'})
  self.assertIn('## 变化记录',second.read_text())
  self.assertTrue((self.root/'.ans/runtime/.gitignore').exists())
  self.assertFalse((self.root/'docs/scheduling/second').exists())

 def test_git_copy_requires_fresh_local_check_evidence(self):
  assignment=self.dispatch();self.complete(assignment)
  second_root=Path(self.tmp.name).parent/(Path(self.tmp.name).name+'-git-copy')
  self.addCleanup(lambda:shutil.rmtree(second_root,ignore_errors=True))
  shutil.copytree(self.root,second_root,ignore=shutil.ignore_patterns('runtime'))
  from_second=Store(second_root,self.task)
  self.assertEqual(from_second.load()['state']['nodes'][0]['status'],'verified')
  from serve_dashboard import Dashboard
  snapshot=Dashboard(second_root).snapshot()
  self.assertEqual(next(row for row in snapshot['tasks'] if row['nodeId']=='a')['status'],'inconsistent')
  self.assertTrue(any('evidence' in issue['message'] for issue in snapshot['issues']))
  with self.assertRaisesRegex(Rejected,'evidence is unavailable'):
   operate(second_root,self.task,'dispatch',{'nodeId':'b','workerId':'other','schedulerToken':self.scheduler})

 def test_git_merges_different_tasks_and_stops_same_task_conflict(self):
  def git(root,*args,check=True):
   result=subprocess.run(['git','-C',str(root),'-c','user.name=ANS Test','-c','user.email=ans-test@example.invalid',*args],text=True,capture_output=True,check=check)
   return result
  git(self.root,'init','-q')
  git(self.root,'add','--','docs','src','.ans/project.json','role-cards')
  git(self.root,'commit','-qm','initial task')
  second_root=self.root.parent/(self.root.name+'-git-branch')
  self.addCleanup(lambda:shutil.rmtree(second_root,ignore_errors=True))
  subprocess.run(['git','clone','-q',str(self.root),str(second_root)],check=True)
  self.task='local-task';self.plan['taskId']=self.task;self.initialize()
  git(self.root,'add','--','docs/scheduling/local-task.md')
  git(self.root,'commit','-qm','local task')
  remote_plan=json.loads(json.dumps(self.plan));remote_plan['taskId']='other-task'
  operate(second_root,'other-task','init',{'configPath':'.ans/project.json','approvedConfigSha256':file_hash(second_root,'.ans/project.json'),'plan':remote_plan})
  git(second_root,'add','--','docs/scheduling/other-task.md')
  git(second_root,'commit','-qm','other task')
  git(second_root,'fetch','-q',str(self.root),'HEAD')
  git(second_root,'merge','-q','--no-ff','FETCH_HEAD','-m','merge separate tasks')
  self.assertEqual({p.stem for p in (second_root/'docs/scheduling').glob('*.md')},{'case','local-task','other-task'})
  self.assertEqual(Store(second_root,'local-task').load()['plan']['taskId'],'local-task')

  first=self.op('dispatch',{'nodeId':'a','workerId':'first'})
  git(self.root,'add','--','docs/scheduling/local-task.md')
  git(self.root,'commit','-qm','first assignment')
  other=operate(second_root,'local-task','dispatch',{'nodeId':'a','workerId':'second','schedulerToken':self.scheduler})
  self.assertEqual(other['assignment']['workerId'],'second')
  git(second_root,'add','--','docs/scheduling/local-task.md')
  git(second_root,'commit','-qm','competing assignment')
  git(second_root,'fetch','-q',str(self.root),'HEAD')
  result=git(second_root,'merge','--no-ff','FETCH_HEAD','-m','must conflict',check=False)
  self.assertNotEqual(result.returncode,0)
  with self.assertRaises(Rejected):Store(second_root,'local-task').load()

 def test_manual_change_or_merge_conflict_is_not_accepted(self):
  document=Store(self.root,self.task).document
  document.write_text(document.read_text().replace('| pending |','| verified |',1))
  with self.assertRaises(Rejected):self.op('status')
  document.write_text('<<<<<<< ours\n'+document.read_text()+'=======\nother\n>>>>>>> theirs\n')
  with self.assertRaises(Rejected):self.op('status')

 def test_git_checkout_crlf_keeps_the_same_task_history(self):
  document=Store(self.root,self.task).document
  document.write_bytes(document.read_bytes().replace(b'\n',b'\r\n'))
  self.assertEqual(self.op('status')['state']['lastEventSeq'],2)
  self.dispatch()
  self.assertEqual(self.state()['status'],'running')
  self.assertNotIn(b'\r\n',document.read_bytes())

 def test_cli_reads_request_from_standard_input(self):
  script=Path(__file__).parents[1]/'task_ops.py'
  result=subprocess.run([sys.executable,str(script),'--root',str(self.root),'--task',self.task,'status','--request','-'],input='{}',text=True,capture_output=True,check=True)
  self.assertEqual(json.loads(result.stdout)['state']['taskId'],self.task)

 def test_common_directory_allows_new_file_without_boundary_rewrite(self):
  self.task='common';self.plan['taskId']=self.task
  boundary='# Section 1\n| directory | `src/common/a/` | private framework |'
  self.put('role-cards/a/boundary.md',boundary)
  path='src/common/a/validation.py'
  self.config['roles']['a']['writeFiles']=[path]
  self.plan['nodes'][0]['writeSet']=[path]
  self.initialize();assignment=self.dispatch()
  self.put(path,'def valid(value):\n return bool(value)\n')
  self.op('run-check',{**assignment,'checkId':'ok'})
  self.op('report',{**assignment,'reportId':'new-helper','kind':'complete','summary':'created helper','changedPaths':[path]})
  self.op('verify',{'nodeId':'a'})
  self.assertEqual(self.state()['status'],'verified')
  self.assertEqual((self.root/'role-cards/a/boundary.md').read_text(),boundary)

 def test_directory_ownership_keeps_task_write_set_exact(self):
  self.task='narrow';self.plan['taskId']=self.task
  self.put('role-cards/a/boundary.md','# Section 1\n| directory | `src/common/a/` | private |')
  path='src/common/a/selected.py';self.put(path,'value=1')
  self.config['roles']['a']['writeFiles']=[path];self.plan['nodes'][0]['writeSet']=[path]
  self.initialize();assignment=self.dispatch()
  report=self.op('report',{**assignment,'reportId':'outside-task','kind':'complete','summary':'unplanned helper','changedPaths':['src/common/a/extra.py']})
  self.assertFalse(report['accepted'])

 def test_common_and_test_directories_are_supported(self):
  for directory in ['src/common/shared/', 'common/a/', 'test/test-role/', 'tests/project/shared/']:
   with self.subTest(directory=directory):
    self.put('role-cards/a/boundary.md','# Section 1\n| directory | `'+directory+'` | owned |')
    self.config['roles']['a']['writeFiles']=[directory+'nested/new.py']
    roles_valid(self.root,self.config)

 def test_directory_grant_does_not_cover_sibling_or_broad_root(self):
  for directory,path in [('src/common/a/','src/common/ab/file.py'),('src/common/','src/common/a/file.py'),('src/','src/a.py'),('test/','test/a/check.py')]:
   with self.subTest(directory=directory,path=path):
    self.put('role-cards/a/boundary.md','# Section 1\n| directory | `'+directory+'` | owned |')
    self.config['roles']['a']['writeFiles']=[path]
    with self.assertRaises(Rejected):roles_valid(self.root,self.config)

 def test_overlapping_directory_and_file_ownership_is_rejected(self):
  self.put('role-cards/a/boundary.md','# Section 1\n| directory | `src/common/a/` | owned |')
  self.config['roles']['a']['writeFiles']=['src/common/a/one.py']
  for entry,path in [('src/common/a/nested/','src/common/a/nested/two.py'),('src/common/a/two.py','src/common/a/two.py')]:
   with self.subTest(entry=entry):
    self.put('role-cards/b/boundary.md','# Section 1\n| scope | `'+entry+'` | other owner |')
    self.config['roles']['b']['writeFiles']=[path]
    with self.assertRaisesRegex(Rejected,'overlapping'):roles_valid(self.root,self.config)

 def test_directory_scope_rejects_traversal_and_symlinks(self):
  self.put('role-cards/a/boundary.md','# Section 1\n| directory | `src/common/a/` | owned |')
  for path in ['src/common/a/../b/file.py','src/common/a//file.py']:
   with self.subTest(path=path):
    self.config['roles']['a']['writeFiles']=[path]
    with self.assertRaises(Rejected):roles_valid(self.root,self.config)
  (self.root/'src/common').mkdir()
  (self.root/'src/common/a').symlink_to(self.root/'src',target_is_directory=True)
  self.config['roles']['a']['writeFiles']=['src/common/a/a.py']
  with self.assertRaises(Rejected):roles_valid(self.root,self.config)

 def test_init_requires_pinned_separate_acceptance_authority(self):
  self.task='new';self.plan['taskId']='new'
  request={**self.request,'plan':self.plan}
  for extra in [{'acceptanceAuthority':{}},{'acceptanceToken':self.acceptance},{'coordinatorToken':'x'*64},{'schedulerToken':self.acceptance}]:
   with self.subTest(extra=list(extra)):
    with self.assertRaises(Rejected):operate(self.root,self.task,'init',{**request,**extra})
  config=dict(self.config);config.pop('acceptanceAuthority');self.put('.ans/no-authority.json',json.dumps(config))
  with self.assertRaisesRegex(Rejected,'acceptanceAuthority'):
   operate(self.root,self.task,'init',{**request,'configPath':'.ans/no-authority.json','approvedConfigSha256':file_hash(self.root,'.ans/no-authority.json')})
  raw=Store(self.root,'case').document.read_text()
  self.assertNotIn('coordinatorTokenHash',raw);self.assertNotIn('tokenHash',raw)
  self.assertNotIn(self.scheduler,raw);self.assertNotIn(self.acceptance,raw)
 def test_scheduler_and_worker_cannot_accept_plan_or_verify(self):
  assignment=self.dispatch()
  for token in [self.scheduler,assignment['token'],'cloud-project-key','forged']:
   for command in ['accept-plan','verify']:
    with self.subTest(command=command):
     with self.assertRaisesRegex(Rejected,'acceptance credential'):
      operate(self.root,self.task,command,{'acceptanceToken':token,'roleId':'acceptance','scope':'acceptance','nodeId':'a'})
  for command in ['dispatch','revise','recover']:
   with self.assertRaisesRegex(Rejected,'Scheduler credential'):
    operate(self.root,self.task,command,{'schedulerToken':self.acceptance,'nodeId':'b'})
 def test_preflight_is_required_and_stale_requests_do_not_commit(self):
  self.task='unapproved';self.plan['taskId']=self.task;self.initialize(accept=False)
  seq=self.op('status')['state']['stateRevision']
  with self.assertRaisesRegex(Rejected,'accept-plan'):self.dispatch()
  self.accept_plan();a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'})
  self.op('report',{**a,'reportId':'done','kind':'complete','summary':'done'})
  seq=self.op('status')['state']['stateRevision']
  with self.assertRaisesRegex(Rejected,'stateRevision'):self.op('verify',{'nodeId':'a','stateRevision':seq-1})
  with self.assertRaisesRegex(Rejected,'candidate'):self.op('verify',{'nodeId':'a','candidate':'old'})
  with self.assertRaisesRegex(Rejected,'criteria'):self.op('verify',{'nodeId':'a','criteriaVersion':'old'})
  self.assertEqual(self.op('status')['state']['stateRevision'],seq)
 def test_missing_evidence_and_needs_work_keep_reservations(self):
  a=self.dispatch();self.op('report',{**a,'reportId':'claim','kind':'complete','summary':'needs checks'})
  for verdict in ['missing-evidence','needs-work']:
   self.op('verify',{'nodeId':'a','verdict':verdict,'summary':'C1 incomplete','criteriaResults':[{'criterionId':'C1','verdict':verdict,'summary':'check missing','evidence':[]}]})
   self.assertTrue(self.state()['active'])
   self.assertFalse(self.op('status')['state']['taskComplete'])
   with self.assertRaises(Rejected):self.dispatch('b')
   if verdict=='missing-evidence':
    self.assertEqual(self.state()['status'],'awaiting-verification')
   else:
    self.assertEqual(self.state()['status'],'blocked')
  with self.assertRaisesRegex(Rejected,'new authorized attempt'):self.op('run-check',{**a,'checkId':'ok'})
  with self.assertRaises(Rejected):self.op('report',{**a,'reportId':'claim-again','kind':'complete','summary':'same attempt'})
  self.op('stop',{**a,'summary':'confirmed stopped'})
  with self.assertRaisesRegex(Rejected,'Retry'):self.dispatch()
  fresh=self.op('dispatch',{'nodeId':'a','workerId':'replacement','retryReason':'fixed implementation'})['assignment']
  self.op('ack',fresh);self.complete(fresh,'retry-complete')
  self.assertEqual(self.state()['attemptNumber'],2)
  self.assertNotIn('tokenHash',Store(self.root,self.task).document.read_text())
 def test_supplement_missing_evidence_in_same_attempt(self):
  a=self.dispatch();self.op('report',{**a,'reportId':'claim','kind':'complete','summary':'completion awaiting evidence'})
  self.op('verify',{'nodeId':'a','verdict':'missing-evidence','summary':'no run yet','criteriaResults':[{'criterionId':'C1','verdict':'missing-evidence','summary':'run required check','evidence':[]}]})
  self.op('run-check',{**a,'checkId':'ok'});self.op('verify',{'nodeId':'a'})
  self.assertEqual(self.state()['status'],'verified')
  self.assertEqual([a['verdict'] for a in self.state()['acceptanceHistory']],['missing-evidence','pass'])
 def test_actual_producer_environment_and_failure_history(self):
  self.task='history';self.plan['taskId']=self.task
  self.config['roles']['a']['checks']['ok']['argv']=[sys.executable,'-c','from pathlib import Path;raise SystemExit(0 if Path("marker").exists() else 9)']
  self.initialize();a=self.dispatch()
  first=self.op('run-check',{**a,'checkId':'ok','producer':{'roleId':'b'}})
  self.assertEqual(first['evidence']['exitCode'],9)
  self.put('marker','ready');last=self.op('run-check',{**a,'checkId':'ok'})
  evidence=last['evidence'];self.assertEqual(evidence['producer'],{k:a[k] for k in ['roleId','workerId','nodeId','attemptId']})
  self.assertIn('executableHash',evidence['environment']);self.assertTrue(evidence['startedAt']<=evidence['finishedAt'])
  self.op('report',{**a,'reportId':'complete','kind':'complete','summary':'actual retry passed'})
  self.op('verify',{'nodeId':'a'})
  self.assertEqual([e['exitCode'] for e in self.state()['checkHistory']],[9,0])
  with patch.dict('os.environ',{'NODE_OPTIONS':'--new-environment'}):
   self.assertTrue(self.state()['currentAcceptanceValid'])
 def test_changed_candidate_check_and_timeout_fail(self):
  for name,code in [('mutate','from pathlib import Path;Path("src/a.py").write_text("changed")'),('timeout','import time;time.sleep(2)')]:
   with self.subTest(name=name):
    self.task=name;self.plan['taskId']=name;self.config['roles']['a']['checks']['ok']={'argv':[sys.executable,'-c',code],'timeoutSeconds':1};self.initialize();a=self.dispatch()
    result=self.op('run-check',{**a,'checkId':'ok'})
    self.assertEqual(result['status'],'check-failed')
    if name=='timeout':self.assertEqual(result['evidence']['exitCode'],124)
    else:self.assertFalse(result['evidence']['candidateUnchanged'])
 def test_transitive_ancestor_log_loss_invalidates_complete(self):
  a=self.dispatch();self.complete(a);b=self.dispatch('b');self.complete(b,'b-complete')
  self.assertTrue(self.op('status')['state']['taskComplete'])
  evidence=self.state()['checkEvidence']['ok'];(self.root/evidence['path']).unlink()
  self.assertFalse(self.state('b')['currentAcceptanceValid'])
  self.assertFalse(self.op('status')['state']['taskComplete'])
  self.assertEqual(self.state('b')['acceptance']['verdict'],'pass')
 def test_criteria_and_acceptance_role_change_invalidate_pass(self):
  a=self.dispatch();self.complete(a)
  self.put('docs/criteria.md','C2 changed')
  self.assertFalse(self.state()['currentAcceptanceValid'])
  with self.assertRaises(Rejected):self.dispatch('b')
  self.put('docs/criteria.md','C1: current candidate and real check pass')
  self.put('role-cards/acceptance/role-card.md','changed role')
  self.assertFalse(self.state()['currentAcceptanceValid'])
 def test_pass_requires_current_outputs_and_real_evidence_references(self):
  a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'});self.op('report',{**a,'reportId':'done','kind':'complete','summary':'done'})
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'a','criteriaResults':[{'criterionId':'C1','verdict':'pass','evidence':[{'kind':'check','checkId':'ok','sha256':'fake'}]}]})
  (self.root/'src/a.py').unlink()
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'a'})
 def test_status_redacts_current_and_historical_credentials(self):
  a=self.dispatch();self.op('stop',{**a,'summary':'stop'})
  self.op('dispatch',{'nodeId':'a','workerId':'retry','retryReason':'new worker'})
  data=json.dumps(self.op('status'))
  for key in ['credentialHash','CredentialHash','tokenHash','TokenHash',self.scheduler,self.acceptance,a['token']]:self.assertNotIn(key,data)
  raw=Store(self.root,self.task).load()['state']
  self.assertIn('assignmentCredentialHash',raw['nodes'][0]['previousAttempts'][0])
 def test_legacy_markdown_and_json_are_read_only(self):
  original=Store(self.root,self.task).load();legacy=json.loads(json.dumps(original));legacy['plan']['taskId']='old';legacy['state']['taskId']='old';legacy['state']['schemaVersion']=1
  legacy['state']['coordinatorTokenHash']=sha(b'old-token');legacy['state'].pop('schedulerCredentialHash');legacy['state'].pop('acceptanceAuthority');legacy['state'].pop('planAcceptance')
  store=Store(self.root,'old');store.commit(legacy,'initialized','legacy fixture')
  self.assertTrue(operate(self.root,'old','status',{})['state']['legacyReadOnly'])
  for command in ['dispatch','revise','ack','report','stop','run-check','verify','accept-plan','recover']:
   with self.assertRaisesRegex(Rejected,'Legacy task is read-only'):operate(self.root,'old',command,{})
  legacy['plan']['taskId']='json';legacy['state']['taskId']='json'
  self.put('docs/scheduling/json/plan.json',json.dumps(legacy['plan']));self.put('docs/scheduling/json/state.json',json.dumps(legacy['state']))
  self.assertTrue(operate(self.root,'json','status',{})['state']['legacyReadOnly'])
 def test_cross_role_plan_requires_genuine_independent_test_coverage(self):
  store=Store(self.root,self.task);bundle=store.load();request={'acceptanceToken':self.acceptance,'stateRevision':bundle['state']['stateRevision'],'planRevision':1,'criteria':bundle['state']['planAcceptance']['criteria'],'customerApproval':{'source':'operator','reference':'fixture'},'requiredNodes':['a','b'],'independentTests':[]}
  with self.assertRaisesRegex(Rejected,'independent test coverage'):operate(self.root,self.task,'accept-plan',request)
  request['independentTests']=[{'nodeId':'a','covers':['b']}]
  with self.assertRaisesRegex(Rejected,'independent-test role'):operate(self.root,self.task,'accept-plan',request)

 def test_execution_environment_uses_declared_path_and_root_cwd(self):
  self.task='path';self.plan['taskId']=self.task
  executable=self.put('bin/probe','#!/bin/sh\nprintf "actual-declared-path"\n');executable.chmod(0o755)
  self.config['roles']['a']['checks']['ok']={'argv':['probe'],'env':{'PATH':'bin','PYTHONDONTWRITEBYTECODE':'0'}}
  self.initialize();a=self.dispatch();result=self.op('run-check',{**a,'checkId':'ok'})
  self.assertEqual(result['evidence']['exitCode'],0)
  self.assertEqual(result['evidence']['environment']['executable'],str(executable))
  self.assertEqual((self.root/result['evidence']['path']).read_text(),'actual-declared-path')
  self.assertEqual(result['evidence']['environment']['executableHash'],file_hash(self.root,'bin/probe'))
  self.put('bin/probe','#!/bin/sh\nprintf changed\n')
  self.op('report',{**a,'reportId':'path-complete','kind':'complete','summary':'completed'})
  with self.assertRaisesRegex(Rejected,'environment'):self.op('verify',{'nodeId':'a'})
 def test_formal_missing_evidence_can_record_lost_ancestor_logs(self):
  a=self.dispatch();self.complete(a);b=self.dispatch('b')
  self.op('run-check',{**b,'checkId':'ok'});self.op('report',{**b,'reportId':'test-complete','kind':'complete','summary':'test complete'})
  (self.root/self.state()['checkEvidence']['ok']['path']).unlink()
  with self.assertRaises(Rejected):self.op('verify',{'nodeId':'b'})
  result=self.op('verify',{'nodeId':'b','verdict':'missing-evidence','summary':'ancestor log unavailable','criteriaResults':[{'criterionId':'C1','verdict':'missing-evidence','summary':'restore ancestor evidence','evidence':[]}]})
  self.assertEqual(result['status'],'ok');self.assertTrue(self.state('b')['active'])
 def test_nonimpact_revision_is_rechecked_by_new_preflight(self):
  a=self.dispatch();self.complete(a)
  self.put('docs/design.md','D2 changes test reporting only')
  self.op('revise',{'version':'D2','affected':['b'],'reason':'test-only reporting contract','unaffectedReason':'developer interface and checks unchanged'})
  self.assertFalse(self.state()['currentAcceptanceValid'])
  with self.assertRaises(Rejected):self.dispatch('b')
  self.accept_plan();self.assertTrue(self.state()['currentAcceptanceValid'])
  b=self.dispatch('b');self.complete(b,'D2-b')
  self.assertTrue(self.op('status')['state']['taskComplete'])
  seq=self.op('status')['state']['stateRevision'];self.assertEqual(self.accept_plan()['status'],'duplicate')
  self.assertEqual(seq,self.op('status')['state']['stateRevision']);self.assertTrue(self.op('status')['state']['taskComplete'])
 def test_stale_report_event_records_actual_old_producer(self):
  a=self.dispatch();self.op('stop',{**a,'summary':'old worker stopped'})
  self.op('dispatch',{'nodeId':'a','workerId':'fresh','retryReason':'replacement'})
  self.op('report',{**a,'reportId':'late','kind':'complete','summary':'late feedback'})
  event=Store(self.root,self.task).journal()[-1]
  self.assertEqual(event['producer']['workerId'],a['workerId']);self.assertEqual(event['producer']['attemptId'],a['attemptId'])
 def test_three_stage_ancestor_loss_blocks_current_completion(self):
  self.task='chain';self.plan['taskId']=self.task
  self.put('src/c.py','test summary')
  self.put('role-cards/c/role-card.md','# c')
  self.put('role-cards/c/boundary.md','# Section 1\n| file | `src/c.py` | owned |')
  self.config['roles']['c']={**self.config['roles']['b'],'card':'role-cards/c/role-card.md','boundary':'role-cards/c/boundary.md','writeFiles':['src/c.py']}
  self.plan['nodes'].append({'nodeId':'c','roleId':'c','operation':'implement','writeSet':['src/c.py'],'readSet':['src/a.py','src/b.py'],'checks':['ok'],'dependsOn':['b']})
  self.initialize(accept=False)
  state=self.op('status')['state']
  self.op('accept-plan',{'stateRevision':state['stateRevision'],'planRevision':1,'criteria':{'path':'docs/criteria.md','version':'C1','sha256':file_hash(self.root,'docs/criteria.md'),'criterionIds':['C1']},'customerApproval':{'source':'fixture operator','reference':'three-stage dependency fixture'},'requiredNodes':['a','b','c'],'independentTests':[{'nodeId':'b','covers':['a']},{'nodeId':'c','covers':['a']}]})
  a=self.dispatch();self.complete(a);b=self.dispatch('b');self.complete(b,'b-done')
  c=self.dispatch('c');self.complete(c,'c-done')
  self.assertTrue(self.op('status')['state']['taskComplete'])
  unchanged=self.state('b')['currentCandidate'];(self.root/self.state()['checkEvidence']['ok']['path']).unlink()
  self.assertEqual(self.state('b')['currentCandidate'],unchanged)
  self.assertFalse(self.state('c')['currentAcceptanceValid']);self.assertFalse(self.op('status')['state']['taskComplete'])

 def test_legacy_json_final_file_symlink_is_rejected(self):
  for filename in ['plan.json','state.json']:
   with self.subTest(filename=filename):
    task='legacy-'+filename.split('.')[0]
    self.put('docs/scheduling/'+task+'/plan.json','{}')
    self.put('docs/scheduling/'+task+'/state.json','{}')
    with tempfile.TemporaryDirectory() as outside:
     target=Path(outside)/filename;target.write_text('{}')
     path=self.root/'docs/scheduling'/task/filename;path.unlink();path.symlink_to(target)
     with self.assertRaisesRegex(Rejected,'Symlink'):operate(self.root,task,'status',{})

 def registered_config(self, custom_root='role-cards/a'):
  definitions={}
  for role_id in ['a','b','scheduler','acceptance']:
   role_root='role-cards/'+role_id
   if role_id=='a':role_root=custom_root
   card=role_root+'/role-card.md';boundary=role_root+'/boundary.md'
   if role_id in self.config['roles']:
    original=self.config['roles'][role_id]
    text=(self.root/original['boundary']).read_text()
    self.put(card,'# '+role_id);original.update(card=card,boundary=boundary)
   elif (self.root/boundary).exists():text=(self.root/boundary).read_text()
   else:text='# Section 1\n'
   self.put(card,'# '+role_id)
   required=[role_root+'/'+name for name in ['feature-map.md','memo.md','functional-description.md']]
   api='not-applicable'
   if role_id=='a':
    api='required';required.append(role_root+'/api-spec.md')
   for path in required:text+='\n| file | `'+path+'` | owner work |'
   text+='\n| directory | `'+role_root+'/docs/` | owner history |'
   if role_id=='scheduler':
    text+='\n| file | `.ans/project.json` | approved config |\n| directory | `.ans/runtime/` | runtime |\n| directory | `docs/scheduling/` | Store only |'
   self.put(boundary,text)
   reason='Fixture coordination role has no exported interface'
   if api=='required':reason='Fixture has callable code'
   definitions[role_id]={'card':card,'boundary':boundary,'requiredWorkDocuments':required,'apiSpec':api,'apiSpecReason':reason}
  self.config['roleDefinitions']=definitions
  return definitions

 def fresh_registered_task(self):
  self.task='documents';self.plan['taskId']=self.task
  self.initialize()

 def legacy_check_fixture(self):
  """Model a real hash-only old-format check; never migrate a real task."""
  store=Store(self.root,self.task);bundle=store.load()
  state=bundle['state']['nodes'][0]
  legacy=dict(state['checkEvidence']['ok'])
  legacy.pop('environmentVersion');legacy.pop('environmentSnapshot')
  legacy['environment']=environment(self.root,self.config['roles']['a']['checks']['ok'])
  state['checkEvidence']['ok']=legacy
  state['checkHistory'][-1]=legacy
  store.commit(bundle,'legacy-check-fixture','Explicit isolated old-format fixture')

 def test_preflight_cli_is_read_only_without_task_or_store(self):
  self.registered_config();self.put('.ans/preflight.json',json.dumps(self.config))
  def tree():
   entries={}
   for path in self.root.rglob('*'):
    data=None
    if path.is_file():data=path.read_bytes()
    entries[str(path.relative_to(self.root))]=(path.stat().st_mode,data)
   return entries
  before=tree()
  with patch('task_ops.Store',side_effect=AssertionError('Preflight must not construct Store')):
   result=operate(self.root,None,'preflight-role',{'configPath':'.ans/preflight.json'})
  self.assertTrue(result['permissionsComplete']);self.assertEqual(result['status'],'ok')
  self.assertTrue(all(not document['exists'] and document['permissionGranted'] for role in result['roles'] for document in role['documents']))
  script=Path(__file__).parents[1]/'task_ops.py'
  proc=subprocess.run([sys.executable,str(script),'--root',str(self.root),'preflight-role','--request','-'],input=json.dumps({'configPath':'.ans/preflight.json'}),capture_output=True,text=True)
  self.assertEqual(proc.returncode,0,proc.stdout+proc.stderr)
  self.assertTrue(json.loads(proc.stdout)['permissionsComplete']);self.assertEqual(tree(),before)

 def test_preflight_lists_core_and_work_doc_missing_permissions(self):
  definitions=self.registered_config()
  missing='role-cards/a/memo.md';work='role-cards/a/docs/fix/current.md'
  definitions['a']['requiredWorkDocuments'].append(work)
  text=(self.root/definitions['a']['boundary']).read_text()
  self.put(definitions['a']['boundary'],'\n'.join(line for line in text.splitlines() if '`'+missing+'`' not in line and 'role-cards/a/docs/' not in line))
  result=preflight_role(self.root,self.config)
  self.assertFalse(result['permissionsComplete'])
  issues=next(role['issues'] for role in result['roles'] if role['roleId']=='a')
  self.assertEqual({issue['path'] for issue in issues},{missing,work})
  with self.assertRaisesRegex(Rejected,'preflight'):self.fresh_registered_task()
  self.assertFalse((self.root/'docs/scheduling/documents.md').exists())

 def test_preflight_rejects_missing_required_api_and_applicability(self):
  definitions=self.registered_config()
  definitions['a']['requiredWorkDocuments'].remove('role-cards/a/api-spec.md')
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])
  definitions['a']['apiSpec']='not-applicable';definitions['a']['apiSpecReason']=''
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])

 def test_registered_custom_root_and_future_document_real_lifecycle(self):
  self.registered_config('团队/库存存储')
  path='团队/库存存储/docs/change/future.md'
  self.config['roles']['a']['writeFiles']=[path];self.plan['nodes'][0]['writeSet']=[path]
  self.config['roles']['a']['checks']['ok']['argv']=[sys.executable,'-c','from pathlib import Path;assert "approved marker" in Path("'+path+'").read_text()']
  self.fresh_registered_task();a=self.dispatch()
  self.put(path,'approved marker')
  self.op('run-check',{**a,'checkId':'ok'})
  self.op('report',{**a,'reportId':'document-done','kind':'complete','summary':'actual document checked','changedPaths':[path]})
  self.op('verify',{'nodeId':'a'});self.assertTrue(self.state()['currentAcceptanceValid'])
  self.assertNotIn(path,self.config['roleDefinitions']['a']['requiredWorkDocuments'])
  self.assertNotIn('role-cards/a',a['card'])

 def test_registered_roots_bindings_and_governance_are_protected(self):
  definitions=self.registered_config()
  good=json.loads(json.dumps(self.config))
  for path in ['role-cards/a/role-card.md','role-cards/a/boundary.md','role-cards/a/boundary.yaml','role-cards/a/changelog.md','role-cards/a/docs/boundary.md','role-cards/b/memo.md','.ans/project.json','docs/scheduling/new.md']:
   with self.subTest(path=path):
    self.config=json.loads(json.dumps(good));self.config['roles']['a']['writeFiles']=[path]
    boundary=self.config['roles']['a']['boundary'];original=(self.root/boundary).read_text()
    self.put(boundary,original+'\n| file | `'+path+'` | wrongly granted |')
    with self.assertRaises(Rejected):roles_valid(self.root,self.config)
    self.put(boundary,original)
  self.config=json.loads(json.dumps(good));self.config['roleDefinitions'].pop('scheduler')
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])
  self.config=json.loads(json.dumps(good));self.config['roles']['a']['card']=definitions['b']['card']
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])
  self.config=json.loads(json.dumps(good));self.config['roleDefinitions']['a']['boundary']=definitions['b']['boundary']
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])

 def test_preflight_checks_all_boundary_scopes_not_selected_write_files(self):
  definitions=self.registered_config()
  other=definitions['b']['boundary'];original=(self.root/other).read_text()
  for path in ['src/a.py','src/','src','common/','test/','role-cards/a/','role-cards/a/docs/','.ans/project.json']:
   with self.subTest(path=path):
    self.put(other,original+'\n| scope | `'+path+'` | not selected for writeFiles |')
    self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])
  self.put(other,original)
  self.assertTrue(preflight_role(self.root,self.config)['permissionsComplete'])

 def test_preflight_protects_custom_nonexecuting_governance_in_common_and_test(self):
  definitions=self.registered_config()
  for role_id,role_root in [('custom-common','src/common/governed'),('custom-test','test/governed')]:
   required=[role_root+'/'+name for name in ['feature-map.md','memo.md','functional-description.md']]
   card=role_root+'/custom-card.txt';boundary=role_root+'/custom-scope.txt'
   self.put(card,'# custom governance')
   self.put(boundary,'# Section 1\n'+'\n'.join('| file | `'+path+'` | work |' for path in required))
   definitions[role_id]={'card':card,'boundary':boundary,'requiredWorkDocuments':required,'apiSpec':'not-applicable','apiSpecReason':'No callable code in this fixture'}
  self.assertTrue(preflight_role(self.root,self.config)['permissionsComplete'])
  original=(self.root/definitions['a']['boundary']).read_text()
  for path in ['src/common/governed/','test/governed/','src/common/governed/custom-card.txt','test/governed/custom-scope.yaml']:
   with self.subTest(path=path):
    self.put(definitions['a']['boundary'],original+'\n| scope | `'+path+'` | not selected |')
    result=preflight_role(self.root,self.config)
    self.assertFalse(result['permissionsComplete'])
    self.assertIn('protected governance',json.dumps(result))
  self.put(definitions['a']['boundary'],original)

 def test_preflight_scope_column_ignores_purpose_and_keeps_scheduler_management(self):
  definitions=self.registered_config()
  path=definitions['b']['boundary'];self.put(path,(self.root/path).read_text()+'\n| file | `.gitignore` | ignores `.ans/runtime/` |')
  self.assertTrue(preflight_role(self.root,self.config)['permissionsComplete'])
  self.config['roles']['a']['writeFiles']=['.ans/runtime/file.txt']
  with self.assertRaises(Rejected):roles_valid(self.root,self.config)

 def test_registered_directory_governance_and_nested_role_roots_rejected(self):
  definitions=self.registered_config()
  self.put('role-cards/a/docs/hidden/changelog.md','governance')
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])
  (self.root/'role-cards/a/docs/hidden/changelog.md').unlink()
  definitions['extra']={'card':'role-cards/a/docs/hidden/card.md','boundary':'role-cards/a/docs/hidden/scope.md','requiredWorkDocuments':[],'apiSpec':'not-applicable','apiSpecReason':'fixture'}
  self.put(definitions['extra']['card'],'# extra');self.put(definitions['extra']['boundary'],'# Section 1')
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])

 def test_registered_document_canonical_and_symlink_paths_rejected(self):
  definitions=self.registered_config()
  self.put('outside/valid.md','source')
  (self.root/'role-cards/a/docs').mkdir()
  (self.root/'role-cards/a/docs/link').symlink_to(self.root/'outside',target_is_directory=True)
  for path in ['role-cards/a/docs/../memo.md','role-cards/a/docs//new.md','role-cards/a/docs/link/not-created.md','role-cards/a/docs/*.md']:
   with self.subTest(path=path):
    self.config['roles']['a']['writeFiles']=[path]
    with self.assertRaises(Rejected):roles_valid(self.root,self.config)
  definitions['a']['requiredWorkDocuments'].append('role-cards/a/docs/link/valid.md')
  self.assertFalse(preflight_role(self.root,self.config)['permissionsComplete'])

 def test_legacy_config_still_rejects_role_documents(self):
  path='role-cards/a/memo.md';self.config['roles']['a']['writeFiles']=[path]
  boundary=self.config['roles']['a']['boundary'];self.put(boundary,(self.root/boundary).read_text()+'\n| file | `'+path+'` | work |')
  with self.assertRaises(Rejected):roles_valid(self.root,self.config)

 def test_v2_other_query_environment_verify_and_dependency_dispatch(self):
  a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'})
  self.op('report',{**a,'reportId':'done','kind':'complete','summary':'done'})
  with patch.dict('os.environ',{'PATH':'/query-only-path','LANG':'query-LANG','NODE_OPTIONS':'query-options'}):
   self.op('verify',{'nodeId':'a'})
   self.assertTrue(self.state()['currentAcceptanceValid']);b=self.dispatch('b')
  self.assertEqual(b['roleId'],'b')

 def test_v2_private_snapshot_and_no_untracked_environment_capture(self):
  self.task='private';self.plan['taskId']=self.task
  self.config['roles']['a']['checks']['ok']['env']={'SYNTHETIC_TRACKED':'private-tracked-marker','PYTHONDONTWRITEBYTECODE':'0'}
  self.initialize();a=self.dispatch()
  with patch.dict('os.environ',{'SYNTHETIC_UNTRACKED':'private-untracked-marker','NODE_OPTIONS':'private-inherited-marker'}):
   result=self.op('run-check',{**a,'checkId':'ok'})
  evidence=result['evidence'];self.assertEqual(evidence['environmentVersion'],2)
  snapshot=self.root/evidence['environmentSnapshot']['path'];data=json.loads(snapshot.read_text())
  self.assertEqual(data['values']['PYTHONDONTWRITEBYTECODE'],'1')
  self.assertEqual(data['values']['SYNTHETIC_TRACKED'],'private-tracked-marker')
  self.assertNotIn('SYNTHETIC_UNTRACKED',data['values'])
  self.assertEqual(snapshot.stat().st_mode&0o777,0o600);self.assertEqual(snapshot.parent.stat().st_mode&0o777,0o700)
  self.assertNotIn('declaredEnvironment',evidence['environment'])
  public=Store(self.root,self.task).document.read_text()+json.dumps(self.op('status'))
  for marker in ['private-tracked-marker','private-untracked-marker','private-inherited-marker']:self.assertNotIn(marker,public)

 def test_v2_snapshot_missing_or_modified_invalidates_without_legacy_fallback(self):
  a=self.dispatch();self.complete(a)
  reference=self.state()['checkEvidence']['ok']['environmentSnapshot'];path=self.root/reference['path'];original=path.read_bytes()
  path.write_bytes(b'{}')
  self.assertFalse(self.state()['currentAcceptanceValid'])
  path.write_bytes(original);self.assertTrue(self.state()['currentAcceptanceValid'])
  path.unlink();self.assertFalse(self.state()['currentAcceptanceValid'])
  with self.assertRaises(Rejected):self.dispatch('b')

 def test_v2_readset_resource_and_declared_configuration_changes_invalidate(self):
  self.task='resources';self.plan['taskId']=self.task
  path='test/a/approved-resource.txt';self.put(path,'approved resource')
  self.plan['nodes'][0]['readSet']=[path]
  self.config['roles']['a']['checks']['ok']['env']={'DECLARED_MODE':'approved'}
  self.initialize();a=self.dispatch();self.complete(a)
  self.put(path,'changed resource');self.assertFalse(self.state()['currentAcceptanceValid'])
  with self.assertRaises(Rejected):self.dispatch('b')
  self.put(path,'approved resource');self.assertTrue(self.state()['currentAcceptanceValid'])
  self.config['roles']['a']['checks']['ok']['env']['DECLARED_MODE']='changed'
  self.put('.ans/project.json',json.dumps(self.config))
  self.assertFalse(self.op('status')['state']['taskComplete'])
  self.assertIn('configuration changed',self.op('status')['state']['currentValidityReason'])

 def test_v2_executable_symlink_target_and_bytes_are_rechecked(self):
  self.task='executable';self.plan['taskId']=self.task
  original=self.put('bin/first','#!/bin/sh\nprintf first');original.chmod(0o755)
  other=self.put('bin/second','#!/bin/sh\nprintf second');other.chmod(0o755)
  selected=self.root/'bin/selected';selected.symlink_to(original)
  self.config['roles']['a']['checks']['ok']={'argv':['selected'],'env':{'PATH':'bin'}}
  self.initialize();a=self.dispatch();self.complete(a)
  self.assertEqual(self.state()['checkEvidence']['ok']['environment']['executable'],str(original))
  selected.unlink();selected.symlink_to(other);self.assertFalse(self.state()['currentAcceptanceValid'])
  selected.unlink();selected.symlink_to(original);self.assertTrue(self.state()['currentAcceptanceValid'])
  original.write_text('#!/bin/sh\nprintf changed');self.assertFalse(self.state()['currentAcceptanceValid'])

 def test_v2_checks_use_single_capture_and_pinned_program(self):
  self.task='capture';self.plan['taskId']=self.task
  selected=self.put('bin/probe','#!/bin/sh\nprintf captured');selected.chmod(0o755)
  self.config['roles']['a']['checks']['ok']={'argv':['probe'],'env':{'PATH':'bin'}}
  self.initialize();a=self.dispatch()
  from task_ops import execution_environment
  with patch('task_ops.execution_environment',wraps=execution_environment) as capture:
   result=self.op('run-check',{**a,'checkId':'ok'})
  self.assertEqual(capture.call_count,1);self.assertEqual(result['evidence']['exitCode'],0)
  self.assertEqual((self.root/result['evidence']['path']).read_text(),'captured')

 def test_v2_executable_changes_during_check_and_snapshot_write_failure(self):
  self.task='self-change';self.plan['taskId']=self.task
  executable=self.put('bin/mutate','#!/bin/sh\nprintf changed >> "$0"\n');executable.chmod(0o755)
  self.config['roles']['a']['checks']['ok']={'argv':['bin/mutate']}
  self.initialize();a=self.dispatch();result=self.op('run-check',{**a,'checkId':'ok'})
  self.assertEqual(result['status'],'check-failed');self.assertFalse(result['evidence']['environmentUnchanged'])
  with patch('task_ops.atomic',side_effect=OSError('snapshot storage failed')):
   with self.assertRaisesRegex(OSError,'snapshot storage failed'):self.op('run-check',{**a,'checkId':'ok'})
  self.assertEqual(len(self.state()['checkHistory']),1)

 def test_legacy_environment_still_rechecks_query_variables_without_migration(self):
  a=self.dispatch();self.op('run-check',{**a,'checkId':'ok'});self.legacy_check_fixture()
  self.op('report',{**a,'reportId':'old-done','kind':'complete','summary':'legacy fixture'})
  self.op('verify',{'nodeId':'a'});before=Store(self.root,self.task).document.read_bytes()
  with patch.dict('os.environ',{'NODE_OPTIONS':'--new-environment'}):self.assertFalse(self.state()['currentAcceptanceValid'])
  self.assertTrue(self.state()['currentAcceptanceValid']);self.assertEqual(Store(self.root,self.task).document.read_bytes(),before)
  self.assertNotIn('environmentVersion',self.state()['checkEvidence']['ok'])

 def test_unknown_environment_version_or_bad_snapshot_shape_rejected(self):
  from task_ops import check_environment_valid
  a=self.dispatch();result=self.op('run-check',{**a,'checkId':'ok'});evidence=result['evidence']
  bundle=Store(self.root,self.task).load();state=bundle['state']['nodes'][0];check=self.config['roles']['a']['checks']['ok']
  for version in [None,1,3,True]:
   with self.subTest(version=version):
    with self.assertRaisesRegex(Rejected,'version'):check_environment_valid(self.root,bundle,state,'ok',check,{**evidence,'environmentVersion':version})
  path=self.root/evidence['environmentSnapshot']['path'];data=json.loads(path.read_text());data['absentKeys'].append('PATH');path.write_text(json.dumps(data))
  bad={**evidence,'environmentSnapshot':{'path':evidence['environmentSnapshot']['path'],'sha256':file_hash(self.root,evidence['environmentSnapshot']['path'])}}
  with self.assertRaisesRegex(Rejected,'keys/absent'):check_environment_valid(self.root,bundle,state,'ok',check,bad)

if __name__=='__main__':unittest.main()
