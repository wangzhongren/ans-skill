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
from task_ops import operate, roles_valid

class TaskOpsTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve();self.task='case'
  self.put('docs/requirements.md','R1');self.put('docs/design.md','D1');self.put('src/a.py','value=1');self.put('src/b.py','value=2')
  roles={}
  for r in ['a','b']:
   self.put('role-cards/'+r+'/role-card.md','# '+r)
   self.put('role-cards/'+r+'/boundary.md','# Section 1\n| file | `src/'+r+'.py` | owner |')
   roles[r]={'card':'role-cards/'+r+'/role-card.md','boundary':'role-cards/'+r+'/boundary.md','writeFiles':['src/'+r+'.py'],'operations':['implement'],'autoDispatch':True,'checks':{'ok':{'argv':[sys.executable,'-c','assert True']}}}
  self.config={'schemaVersion':1,'roles':roles,'designFiles':['docs/design.md'],'allowDesignRevision':True}
  self.plan={'schemaVersion':1,'taskId':self.task,'requirement':{'path':'docs/requirements.md','version':'R1'},'design':{'path':'docs/design.md','version':'D1'},'nodes':[{'nodeId':r,'roleId':r,'stage':'implementation','operation':'implement','writeSet':['src/'+r+'.py'],'checks':['ok'],'dependsOn':[] if r=='a' else ['a']} for r in ['a','b']]}
  self.initialize()
 def put(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value);return p
 def initialize(self):
  self.put('.ans/project.json',json.dumps(self.config))
  self.request={'configPath':'.ans/project.json','approvedConfigSha256':file_hash(self.root,'.ans/project.json'),'plan':self.plan}
  self.coordinator=self.op('init',self.request)['coordinatorToken']
 def op(self,command,request=None):
  request=dict(request or {})
  if command in {'dispatch','revise','verify','recover'}:request['coordinatorToken']=self.coordinator
  return operate(self.root,self.task,command,request)
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
  with self.assertRaises(Rejected):operate(self.root,self.task,'dispatch',{'nodeId':'b','workerId':'self','coordinatorToken':a['token']})
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
   operate(second_root,self.task,'dispatch',{'nodeId':'b','workerId':'other','coordinatorToken':self.coordinator})

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
  other=operate(second_root,'local-task','dispatch',{'nodeId':'a','workerId':'second','coordinatorToken':self.coordinator})
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
  self.assertEqual(self.op('status')['state']['lastEventSeq'],1)
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

if __name__=='__main__':unittest.main()
