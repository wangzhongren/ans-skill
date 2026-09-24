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
from context_store import ContextStore

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
  store=ContextStore(self.root,'订单');store.init({'title':'订单总览','summary':'订单处理'})
  (self.role/'boundary.md').write_text('# Section 1\n| Type | Path |\n| --- | --- |\n| File | `src/orders.py` |\n')
  store.set_category('flows','按钮启动导出流程',0)
  store.upsert('order-export',{'category':'flows','title':'导出','summary':'导出订单','details':'读取订单','refs':['src/orders.py'],'flow':{'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'读取订单'}]}},0)
  store.set_overview({'title':'订单总览','summary':'订单处理','steps':[{'title':'导出'}]},1)
  context=self.app.snapshot()['roles'][0]['projectContext']
  self.assertEqual(self.app.snapshot()['roles'][0]['boundaryPaths'],['src/orders.py'])
  self.assertEqual(context['overview']['title'],'订单总览')
  self.assertEqual(context['categorySummaries']['flows']['summary'],'按钮启动导出流程')
  self.assertEqual([(row['category'],row['topic_id']) for row in context['topics']],[('flows','order-export')])
  self.assertEqual(self.app.context_topic('订单','order-export')['flow']['triggers'][0]['when'],'用户点击导出按钮')
  self.assertEqual(self.app.context_topic('订单','order-export')['details'],'读取订单')
  store.upsert('order-export',{'category':'flows','title':'导出','summary':'新版导出','details':'生成文件','flow':{'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'生成文件'}]}},1)
  updated={row['topic_id']:row for row in self.app.snapshot()['roles'][0]['projectContext']['topics']}
  self.assertEqual(updated['order-export']['summary'],'新版导出')
  with self.assertRaises(ValueError):self.app.document('project-context/context.sqlite3')
  with self.assertRaises(ValueError):self.app.context_topic('不存在','order-export')
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
  store=ContextStore(self.root,'订单');store.init({'title':'订单总览','summary':'订单处理'})
  store.set_category('data','订单输入字段',0)
  store.upsert('order-record',{'category':'data','title':'订单数据','summary':'只读输入','data':{'owner':'订单角色','fields':[{'name':'orderId','type':'string','required':True}]}},0)
  store.upsert('export-api',{'category':'interfaces','title':'导出接口','summary':'HTTP 接口','interface':{'entry':'orders.export','method':'POST','requestUrl':'/api/orders/export','inputs':[{'name':'status','type':'string'}],'outputs':[{'name':'taskId','type':'string'}]}},0)
  store.upsert('internal-api',{'category':'interfaces','title':'订单内部接口','summary':'内部契约','interface':{'kind':'internal','entry':'OrderService.public.export','inputs':[{'name':'orderId','type':'string'}],'outputs':[{'name':'result','type':'ExportResult'}]}},0)
  store.upsert('order-export',{'category':'flows','title':'导出','summary':'导出订单','details':'读取订单','flow':{'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'读取订单'}]}},0)
  server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(self.app));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   url='http://127.0.0.1:'+str(server.server_port)
   with urlopen(url+'/api/snapshot',timeout=5) as response:
    role=json.load(response)['roles'][0]
    self.assertEqual(role['id'],'订单')
    self.assertEqual(role['projectContext']['overview']['title'],'订单总览')
   from urllib.parse import urlencode
   with urlopen(url+'/api/context?'+urlencode({'role':'订单','topic':'order-export'}),timeout=5) as response:
    self.assertEqual(json.load(response)['details'],'读取订单')
   with urlopen(url+'/api/context?'+urlencode({'role':'订单','category':'data'}),timeout=5) as response:
    self.assertEqual(json.load(response)['topics'][0]['data']['fields'][0]['name'],'orderId')
   with urlopen(url+'/api/context?'+urlencode({'role':'订单','category':'interfaces'}),timeout=5) as response:
    interfaces={topic['topic_id']:topic['interface'] for topic in json.load(response)['topics']}
    self.assertEqual(interfaces['export-api']['requestUrl'],'/api/orders/export')
    self.assertEqual(interfaces['export-api']['kind'],'network')
    self.assertEqual(interfaces['internal-api']['kind'],'internal')
   with urlopen(url+'/role-atlas?embedded=1',timeout=5) as response:
    self.assertIn("frame-ancestors 'self'",response.headers['Content-Security-Policy'])
    self.assertIn('ROLE FLOW EXPLORER',response.read().decode())
   with urlopen(url,timeout=5) as response:self.assertIn("frame-ancestors 'none'",response.headers['Content-Security-Policy'])
   for req,code in [(Request(url,method='POST'),405),(Request(url,headers={'Host':'attacker.invalid'}),403),(Request(url+'/api/document?path=../bad'),400)]:
    with self.assertRaises(HTTPError) as caught:urlopen(req,timeout=5)
    self.assertEqual(caught.exception.code,code);caught.exception.close()
  finally:server.shutdown();server.server_close();thread.join(timeout=2)
