import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parents[1]))
from coordination_store import Store, Rejected, file_hash
from task_ops import operate

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
 def test_journal_recovery_after_projection_failure(self):
  a=self.dispatch()
  with patch.object(Store,'materialize',side_effect=OSError('simulated interrupted replacement')):
   with self.assertRaises(OSError):self.op('report',{**a,'reportId':'r','kind':'progress','summary':'saved in log'})
  with self.assertRaises(Rejected):self.op('status')
  recovered=self.op('recover');self.assertEqual(recovered['state']['nodes'][0]['latestReport']['summary'],'saved in log')
 def test_tamper_partial_log_and_lock(self):
  store=Store(self.root,self.task)
  with store.locked():
   with self.assertRaises(Rejected):
    with Store(self.root,self.task).locked():pass
  with (store.folder/'events.jsonl').open('ab') as f:f.write(b'{partial')
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
 def test_generated_log_symlink_rejected(self):
  store=Store(self.root,self.task);log=store.folder/'events.jsonl';saved=log.read_bytes();log.unlink()
  outside=Path(self.tmp.name).parent/'not-an-existing-ans-log'
  log.symlink_to(outside)
  with self.assertRaises(Rejected):self.op('recover')
  log.unlink();log.write_bytes(saved)
 def test_board_and_dashboard_agree(self):
  from serve_dashboard import Dashboard
  a=self.dispatch();self.complete(a)
  snapshot=Dashboard(self.root).snapshot();self.assertEqual(snapshot['issues'],[])
  self.assertEqual(next(n for n in snapshot['tasks'] if n['nodeId']=='a')['status'],'verified')
  self.assertIn('| a | a | verified |',(Store(self.root,self.task).folder/'board.md').read_text())

if __name__=='__main__':unittest.main()
