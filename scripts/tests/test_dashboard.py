import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).parents[1]))
from serve_dashboard import Dashboard, make_handler, ThreadingHTTPServer

class DashboardTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
  self.role=self.root/'角色卡/订单';self.role.mkdir(parents=True)
  (self.role/'role-card.md').write_text('# 订单\n\n订单能力。\n');(self.role/'boundary.md').write_text('# 边界\n订单文件')
  self.folder=self.root/'docs/scheduling/task-1';self.folder.mkdir(parents=True)
  self.app=Dashboard(self.root)
 def records(self,status='running'):
  p={'schemaVersion':1,'taskId':'task-1','planRevision':1,'nodes':[{'nodeId':'order','roleId':'订单','title':'订单查询','stage':'implementation'}]}
  s={'schemaVersion':1,'taskId':'task-1','planRevision':1,'stateRevision':1,'lastEventSeq':1,'updatedAt':'2026-09-20T10:00:00+08:00','nodes':[{'nodeId':'order','roleId':'订单','status':status}]}
  e={'eventId':'e1','taskId':'task-1','nodeId':'order','seq':1,'kind':'started','summary':'开始执行','receivedAt':'2026-09-20T10:00:00+08:00'}
  for name,obj in [('plan.json',p),('state.json',s)]: (self.folder/name).write_text(json.dumps(obj))
  (self.folder/'events.jsonl').write_text(json.dumps(e)+'\n')
  return p,s,e
 def test_real_roles_without_fake_execution(self):
  d=self.app.snapshot();self.assertEqual(d['roles'][0]['name'],'订单');self.assertEqual(d['projectRootUri'],self.root.as_uri());self.assertEqual(d['tasks'],[]);self.assertEqual(d['events'],[])
 def test_role_context_live_listing_and_read_boundary(self):
  context=self.role/'project-context';(context/'flows').mkdir(parents=True);(context/'interfaces').mkdir()
  (context/'README.md').write_text('# 订单项目纵览\n')
  (context/'flows/order-export.md').write_text('# 导出流程\n')
  (context/'interfaces/order-api.md').write_text('# 对外接口\n')
  (context/'private.json').write_text('secret')
  documents=self.app.snapshot()['roles'][0]['projectContext']
  self.assertEqual([(d['category'],d['name']) for d in documents],[('overview','README.md'),('flows','order-export.md'),('interfaces','order-api.md')])
  self.assertEqual(self.app.document(documents[1]['path']),'# 导出流程\n')
  (context/'events').mkdir();(context/'events/created.md').write_text('# 创建事件\n')
  self.assertIn('events',[d['category'] for d in self.app.snapshot()['roles'][0]['projectContext']])
  for path in ['角色卡/订单/project-context/private.json','角色卡/订单/project-context/docs/hidden.md','角色卡/订单/project-context/flows/nested/hidden.md']:
   with self.assertRaises(ValueError):self.app.document(path)
  (context/'data').symlink_to(context/'flows',target_is_directory=True)
  self.assertNotIn('data',[d['category'] for d in self.app.snapshot()['roles'][0]['projectContext']])
  with self.assertRaises(ValueError):self.app.document('角色卡/订单/project-context/data/order-export.md')
 def test_live_re_read_and_no_mutation(self):
  _,s,_=self.records();before=(self.folder/'plan.json').read_bytes()
  self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'running')
  s['nodes'][0]['status']='awaiting-verification';(self.folder/'state.json').write_text(json.dumps(s))
  self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'awaiting-verification')
  self.assertEqual(before,(self.folder/'plan.json').read_bytes())
 def test_state_revision_mismatch_not_verified(self):
  _,s,_=self.records('verified');s['planRevision']=2;(self.folder/'state.json').write_text(json.dumps(s))
  d=self.app.snapshot();self.assertEqual(d['tasks'][0]['status'],'inconsistent');self.assertEqual(d['tasks'][0]['reportedStatus'],'verified');self.assertTrue(d['issues'])
 def test_log_ahead_and_partial_record(self):
  self.records('verified');(self.folder/'events.jsonl').write_text('{broken')
  d=self.app.snapshot();self.assertEqual(d['tasks'][0]['status'],'inconsistent');self.assertTrue(d['issues'])
 def test_missing_state_unreported(self):
  self.records();(self.folder/'state.json').unlink();d=self.app.snapshot();self.assertEqual(d['tasks'][0]['status'],'unreported');self.assertTrue(d['issues'])
 def test_design_revision_not_acknowledged(self):
  _,s,_=self.records('verified');s['nodes'][0]['assignedRevisions']={'design':'D3'};s['nodes'][0]['acknowledgedRevisions']={'design':'D2'}
  (self.folder/'state.json').write_text(json.dumps(s));self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'inconsistent')
 def test_unknown_role_not_accepted(self):
  p,_,_=self.records('verified');p['nodes'][0]['roleId']='missing';(self.folder/'plan.json').write_text(json.dumps(p))
  self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'inconsistent')
 def test_object_node_map(self):
  p,s,_=self.records();p['nodes']={'order':p['nodes'][0]};s['nodes']={'order':s['nodes'][0]}
  (self.folder/'plan.json').write_text(json.dumps(p));(self.folder/'state.json').write_text(json.dumps(s));self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'running')
 def test_traversal_and_symlinks(self):
  with self.assertRaises(ValueError):self.app.document('../outside.md')
  with self.assertRaises(ValueError):self.app.document('docs/private.md')
  outside=Path(self.tmp.name).parent/'dashboard-outside-test.txt'
  # A nonexistent outside target is sufficient to check resolution before reading.
  (self.role/'api-spec.md').symlink_to(outside)
  with self.assertRaises(ValueError):self.app.document('角色卡/订单/api-spec.md')
  with self.assertRaises(ValueError):Dashboard(self.root,roles='../outside')
 def test_bad_role_content_safe_data(self):
  (self.role/'role-card.md').write_text('# <script>alert(1)</script>\n\nraw')
  self.assertIn('<script>',self.app.snapshot()['roles'][0]['name'])
 def test_event_sequence_gap(self):
  _,s,e=self.records('verified');e['seq']=3;s['lastEventSeq']=3
  (self.folder/'state.json').write_text(json.dumps(s));(self.folder/'events.jsonl').write_text(json.dumps(e))
  self.assertEqual(self.app.snapshot()['tasks'][0]['status'],'inconsistent')

class HTTPTests(unittest.TestCase):
 setUp=DashboardTests.setUp
 def test_http_read_only_and_loopback_host(self):
  context=self.role/'project-context';context.mkdir();(context/'README.md').write_text('# 项目纵览\n')
  server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.app));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   url='http://127.0.0.1:'+str(server.server_port)
   with urlopen(url+'/api/snapshot',timeout=5) as response:
    role=json.load(response)['roles'][0]
    self.assertEqual(role['id'],'订单')
    self.assertEqual(role['projectContext'][0]['name'],'README.md')
   from urllib.parse import quote
   with urlopen(url+'/api/document?path='+quote(role['projectContext'][0]['path']),timeout=5) as response:
    self.assertEqual(json.load(response)['text'],'# 项目纵览\n')
   with urlopen(url+'/role-atlas?embedded=1',timeout=5) as response:
    self.assertIn("frame-ancestors 'self'",response.headers['Content-Security-Policy'])
    self.assertIn('ROLE FLOW EXPLORER',response.read().decode())
   with urlopen(url,timeout=5) as response:self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])
   for req,code in [(Request(url,method='POST'),405),(Request(url,headers={'Host':'attacker.invalid'}),403),(Request(url+'/api/document?path=../bad'),400)]:
    with self.assertRaises(HTTPError) as caught:urlopen(req,timeout=5)
    self.assertEqual(caught.exception.code,code);caught.exception.close()
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
