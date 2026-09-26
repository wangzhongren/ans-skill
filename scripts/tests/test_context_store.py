import json
from contextlib import closing
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).parents[1]))
from context_store import ContextStore


def explained(flow,purpose,success):
 return {**flow,'intent':{'purpose':purpose,'success':success}}


class ContextStoreTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
  for role in ('订单','支付'):
   folder=self.root/'角色卡'/role;folder.mkdir(parents=True);(folder/'role-card.md').write_text('# '+role+'\n\n负责'+role+'流程。\n')
   (folder/'boundary.md').write_text('# Section 1\n\n| Type | Path |\n| --- | --- |\n| File | `src/'+role+'.py` |\n')

 def test_one_database_role_filters_and_revisions(self):
  orders=ContextStore(self.root,'订单');payments=ContextStore(self.root,'支付')
  orders.init({'title':'订单总览','summary':'订单流程','steps':[{'title':'入口','description':'接收订单'}]})
  payments.init({'title':'支付总览','summary':'支付流程'})
  self.assertEqual(len(list((self.root/'project-context').glob('*.sqlite3'))),1)
  self.assertEqual(orders.outline()['role']['boundaryPaths'],['src/订单.py'])
  created=orders.upsert('order-export',{'category':'flows','title':'导出','summary':'导出订单','details':'读取订单','refs':['src/orders.py'],'flow':explained({'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'读取订单'}]},'用户下载订单数据，系统准备可保存的文件。','浏览器得到订单文件。')},0)
  self.assertEqual(created['revision'],1)
  self.assertEqual(payments.list_topics(),[])
  with self.assertRaises(ValueError):payments.get_topic('order-export')
  with self.assertRaises(ValueError):orders.upsert('order-export',{'category':'flows','title':'覆盖','summary':'错误版本','flow':explained({'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'读取'}]},'用户导出订单时，系统读取订单。','订单文件已生成。')},0)
  self.assertEqual(orders.get_topic('order-export')['title'],'导出')
  self.assertEqual(orders.upsert('order-export',{'category':'flows','title':'导出','summary':'生成文件','flow':explained({'triggers':[{'when':'用户点击导出按钮'}],'steps':[{'title':'写文件'}]},'用户导出订单时，系统生成最新订单文件。','浏览器得到最新文件。')},1)['revision'],2)
  self.assertEqual(orders.search('生成')[0]['topic_id'],'order-export')
  self.assertIsNotNone(orders.delete('order-export',2)['deleted_at'])
  self.assertEqual(orders.list_topics(),[])
  self.assertIsNone(orders.delete('order-export',3,restore=True)['deleted_at'])
  self.assertEqual(orders.set_overview({'title':'订单总览','summary':'已更新'},1)['revision'],2)
  self.assertEqual(payments.overview()['summary'],'支付流程')
  self.assertTrue(orders.validate()['valid'])

 def test_cli_requires_matching_actor_for_writes(self):
  source=Path(__file__).parents[1]/'context_store.py'
  input_file=self.root/'overview.json';input_file.write_text(json.dumps({'title':'总览','summary':'订单流程'}))
  base=[sys.executable,str(source),'--root',str(self.root),'--role','订单']
  rejected=subprocess.run(base+['--actor-role','支付','init','--input',str(input_file)],capture_output=True,text=True)
  self.assertEqual(rejected.returncode,2)
  self.assertFalse((self.root/'project-context/context.sqlite3').exists())
  accepted=subprocess.run(base+['--actor-role','订单','init','--input',str(input_file)],capture_output=True,text=True)
  self.assertEqual(accepted.returncode,0,accepted.stderr)
  self.assertEqual(json.loads(accepted.stdout)['revision'],1)
  read=subprocess.run(base+['outline'],capture_output=True,text=True)
  self.assertEqual(json.loads(read.stdout)['overview']['title'],'总览')
  category_file=self.root/'category.json';category_file.write_text(json.dumps({'summary':'订单事件汇总'},ensure_ascii=False))
  updated=subprocess.run(base+['--actor-role','订单','set-category','events','--input',str(category_file),'--expect-revision','0'],capture_output=True,text=True)
  self.assertEqual(updated.returncode,0,updated.stderr)
  self.assertEqual(json.loads(updated.stdout)['summary'],'订单事件汇总')
  category=subprocess.run(base+['get-category','events'],capture_output=True,text=True)
  self.assertEqual(json.loads(category.stdout)['revision'],1)

 def test_category_summaries_and_flow_links_stay_in_role(self):
  orders=ContextStore(self.root,'订单');payments=ContextStore(self.root,'支付')
  orders.init({'title':'订单总览','summary':'订单流程'})
  payments.init({'title':'支付总览','summary':'支付流程'})
  orders.set_category('events','订单事件说明',0)
  orders.set_category('data','订单数据说明',0)
  orders.set_category('interfaces','订单接口说明',0)
  self.assertEqual(orders.outline()['categorySummaries']['events']['summary'],'订单事件说明')
  with self.assertRaises(ValueError):payments.get_category('events')
  for topic_id,category in [('order-created','events'),('order-record','data'),('order-api','interfaces')]:
   value={'category':category,'title':topic_id,'summary':'可从流程进入'}
   if category=='events':value['event']={'occurrence':'订单创建'}
   if category=='data':value['data']={'owner':'订单角色','fields':[{'name':'orderId','type':'string','description':'订单编号','required':True}]}
   if category=='interfaces':value['interface']={'entry':'orders.export','method':'POST','requestUrl':'/api/orders/export','inputs':[{'name':'orderId','type':'string','required':True}],'outputs':[{'name':'exportId','type':'string'}]}
   orders.upsert(topic_id,value,0)
  linked=['order-created','order-record','order-api']
  flow=explained({'steps':[{'title':'处理订单'}],'triggeredBy':['order-created'],'inputs':['order-record'],'outputs':['order-record'],'interfaces':['order-api']},'订单创建后，系统读取记录并准备导出。','用户得到订单导出结果。')
  orders.upsert('order-export',{'category':'flows','title':'导出','summary':'流程','links':linked,'flow':flow},0)
  orders.set_overview({'title':'订单总览','summary':'流程','steps':[{'title':'处理','links':linked}]},1)
  self.assertEqual(orders.get_topic('order-export')['links'],linked)
  self.assertEqual(orders.get_topic('order-export')['flow']['triggeredBy'],['order-created'])
  self.assertEqual(orders.get_topic('order-created')['event']['occurrence'],'订单创建')
  self.assertEqual(orders.get_topic('order-created')['triggeredFlows'],['order-export'])
  self.assertEqual(orders.get_topic('order-record')['data']['fields'][0]['name'],'orderId')
  self.assertEqual(orders.get_topic('order-api')['interface']['requestUrl'],'/api/orders/export')
  self.assertEqual(orders.get_topic('order-api')['interface']['outputs'][0]['name'],'exportId')
  self.assertEqual(orders.get_topic('order-api')['interface']['method'],'POST')
  self.assertEqual(orders.get_topic('order-api')['interface']['kind'],'network')
  orders.upsert('order-service',{'category':'interfaces','title':'订单服务接口','summary':'内部公共契约','interface':{'kind':'internal','entry':'OrderService.public.export','inputs':[{'name':'orderId','type':'string'}],'outputs':[{'name':'result','type':'ExportResult'}]}},0)
  self.assertEqual(orders.get_topic('order-service')['interface']['kind'],'internal')
  with self.assertRaises(ValueError):orders.upsert('bad-api',{'category':'interfaces','title':'缺少方法','summary':'错误','interface':{'kind':'network','protocol':'HTTP','entry':'orders.export','requestUrl':'/api/orders/export','inputs':[{'name':'orderId','type':'string'}],'outputs':[]}},0)
  self.assertEqual(orders.overview()['steps'][0]['links'],linked)
  payments.upsert('payment-event',{'category':'events','title':'支付事件','summary':'支付专属','event':{'occurrence':'支付成功'}},0)
  self.assertTrue(payments.validate()['valid'])
  payments.upsert('payment-flow',{'category':'flows','title':'支付完成处理','summary':'处理支付结果','flow':explained({'steps':[{'title':'更新状态'}],'triggeredBy':['payment-event']},'支付成功后，系统把订单标记为已支付。','订单状态显示已支付。')},0)
  self.assertTrue(payments.validate()['valid'])
  with self.assertRaises(ValueError):orders.upsert('invalid-flow',{'category':'flows','title':'无效关联','summary':'跨角色','flow':explained({'steps':[{'title':'处理'}],'triggeredBy':['payment-event']},'收到付款后更新订单。','订单状态已更新。')},0)
  with self.assertRaises(ValueError):orders.upsert('wrong-input',{'category':'flows','title':'输入类型错误','summary':'错误','flow':explained({'steps':[{'title':'处理'}],'inputs':['order-created']},'用户提交订单后系统读取输入。','订单已处理。')},0)
  self.assertEqual(orders.list_topics('flows')[0]['topic_id'],'order-export')

 def test_migration_preserves_version_one_overview(self):
  database=self.root/'project-context/context.sqlite3';database.parent.mkdir()
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript('''
    CREATE TABLE meta(schema_version INTEGER NOT NULL);
    CREATE TABLE overview(role_id TEXT PRIMARY KEY,title TEXT,summary TEXT,revision INTEGER,updated_at TEXT);
    CREATE TABLE overview_steps(role_id TEXT,position INTEGER,title TEXT,description TEXT,ref TEXT);
    CREATE TABLE overview_step_links(role_id TEXT,step_position INTEGER,position INTEGER,target_topic_id TEXT);
    CREATE TABLE category_summaries(role_id TEXT,category TEXT,summary TEXT,revision INTEGER,updated_at TEXT);
    CREATE TABLE topics(role_id TEXT,topic_id TEXT,category TEXT,title TEXT,summary TEXT,details TEXT,revision INTEGER,updated_at TEXT,deleted_at TEXT,PRIMARY KEY(role_id,topic_id));
    CREATE TABLE topic_refs(role_id TEXT,topic_id TEXT,position INTEGER,ref TEXT);
    CREATE TABLE topic_links(role_id TEXT,source_topic_id TEXT,position INTEGER,target_topic_id TEXT);
    INSERT INTO meta VALUES(1);
    INSERT INTO overview VALUES('订单','旧总览','保留内容',1,'2026-09-24');
   ''')
   connection.commit()
  orders=ContextStore(self.root,'订单')
  with self.assertRaises(ValueError):orders.overview()
  self.assertTrue(orders.migrate()['changed'])
  self.assertFalse(orders.migrate()['changed'])
  self.assertEqual(orders.migrate()['schemaVersion'],7)
  self.assertEqual(orders.overview()['summary'],'保留内容')
  self.assertEqual(orders.list_topics(),[])

 def test_migration_preserves_version_two_rows(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'版本二内容'})
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript('DROP TABLE flow_trigger_conditions; DROP TABLE event_definitions; DROP TABLE topic_fields; DROP TABLE interface_specs; DROP TABLE data_schemas; CREATE TABLE event_triggers(role_id TEXT,topic_id TEXT,when_text TEXT,action_text TEXT); CREATE TABLE event_trigger_consumers(role_id TEXT,topic_id TEXT,position INTEGER,consumer TEXT); UPDATE meta SET schema_version=2;')
   connection.commit()
  with self.assertRaises(ValueError):orders.overview()
  self.assertTrue(orders.migrate()['changed'])
  self.assertEqual(orders.overview()['summary'],'版本二内容')

 def test_migration_preserves_event_occurrence_from_version_three(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'版本三内容'})
  orders.upsert('export-click',{'category':'events','title':'点击导出','summary':'按钮事件','event':{'occurrence':'用户点击导出按钮'}},0)
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript("DROP TABLE flow_trigger_conditions; CREATE TABLE event_triggers(role_id TEXT,topic_id TEXT,when_text TEXT,action_text TEXT); INSERT INTO event_triggers SELECT role_id,topic_id,occurrence,'旧动作' FROM event_definitions; DROP TABLE event_definitions; DROP TABLE interface_specs; CREATE TABLE interface_specs(role_id TEXT,topic_id TEXT,entry TEXT,method TEXT,request_url TEXT); UPDATE meta SET schema_version=3;")
   connection.commit()
  self.assertTrue(orders.migrate()['changed'])
  self.assertEqual(orders.get_topic('export-click')['event']['occurrence'],'用户点击导出按钮')

 def test_direct_flow_triggers_and_upstream_flow(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'流程'})
  orders.upsert('export-flow',{'category':'flows','title':'导出流程','summary':'生成文件','flow':explained({'triggers':[{'when':'用户点击导出按钮','ref':'src/interface/export_button.py'}],'steps':[{'title':'写文件'}]},'用户点击导出后，系统生成订单文件。','用户得到订单文件。')},0)
  orders.upsert('notify-flow',{'category':'flows','title':'通知流程','summary':'通知用户','flow':explained({'triggers':[{'when':'导出流程完成','sourceFlow':'export-flow'}],'steps':[{'title':'发送通知'}]},'订单文件生成后，系统通知用户。','用户收到导出完成通知。')},0)
  self.assertEqual(orders.get_topic('export-flow')['flow']['triggers'][0]['when'],'用户点击导出按钮')
  self.assertEqual(orders.get_topic('notify-flow')['flow']['triggers'][0]['sourceFlow'],'export-flow')
  self.assertTrue(orders.validate()['valid'])
  orders.upsert('pending-flow',{'category':'flows','title':'待补充触发','summary':'未完成','flow':explained({'steps':[{'title':'等待'}]},'系统等待一个尚未记录的入口。','入口补齐后再处理。')},0)
  self.assertEqual(orders.validate()['flowsWithoutTriggers'],['pending-flow'])
  with self.assertRaises(ValueError):orders.upsert('bad-flow',{'category':'flows','title':'无效来源','summary':'错误','flow':explained({'triggers':[{'when':'错误','sourceFlow':'missing'}],'steps':[{'title':'停止'}]},'上游失败时，系统停止处理。','用户看到失败提示。')},0)

 def test_migration_from_version_four_adds_flow_triggers(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'版本四内容'})
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript('DROP TABLE flow_trigger_conditions; DROP TABLE interface_specs; CREATE TABLE interface_specs(role_id TEXT,topic_id TEXT,entry TEXT,method TEXT,request_url TEXT); UPDATE meta SET schema_version=4;')
   connection.commit()
  self.assertTrue(orders.migrate()['changed'])
  self.assertEqual(orders.overview()['summary'],'版本四内容')

 def test_migration_classifies_existing_network_interface(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'版本五内容'})
  orders.upsert('export-api',{'category':'interfaces','title':'导出接口','summary':'HTTP','interface':{'entry':'orders.export','method':'POST','requestUrl':'/api/orders/export','inputs':[{'name':'status','type':'string'}],'outputs':[]}},0)
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript('CREATE TABLE interface_specs_old AS SELECT role_id,topic_id,entry,method,request_url FROM interface_specs; DROP TABLE interface_specs; ALTER TABLE interface_specs_old RENAME TO interface_specs; UPDATE meta SET schema_version=5;')
   connection.commit()
  self.assertTrue(orders.migrate()['changed'])
  self.assertEqual(orders.get_topic('export-api')['interface']['kind'],'network')
  self.assertEqual(orders.get_topic('export-api')['interface']['protocol'],'HTTP')

 def test_branch_graph_round_trip_and_invalid_paths(self):
  from copy import deepcopy
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'订单流程'})
  graph={'nodes':[
   {'id':'start','kind':'start','title':'收到请求'},
   {'id':'valid','kind':'decision','title':'参数合法？','ref':'src/interface/orders.py'},
   {'id':'save','kind':'action','title':'保存订单','ref':'src/providers/orders.py'},
   {'id':'done','kind':'end','title':'返回成功','description':'订单已保存，页面显示订单编号。'},
   {'id':'bad','kind':'error','title':'返回 400','description':'订单没有保存，页面提示必填字段错误。','ref':'src/interface/orders.py','checks':['检查必填字段和请求体']}
  ],'edges':[
   {'from':'start','to':'valid'},
   {'from':'valid','to':'save','condition':'if 参数合法'},
   {'from':'valid','to':'bad','condition':'else 参数无效'},
   {'from':'save','to':'done'}]}
  value={'category':'flows','title':'创建订单','summary':'含验证分支',
         'flow':{'triggers':[{'when':'收到 POST /orders'}],'graph':graph,
                 'intent':{'purpose':'用户提交订单，系统校验并保存可用的订单。',
                           'success':'页面显示新订单编号。',
                           'failure':'参数不完整时不保存，页面提示缺少的字段。'}}}
  with self.assertRaisesRegex(ValueError,'purpose'):
   orders.upsert('missing-purpose',{**value,'flow':{'triggers':[{'when':'收到 POST /orders'}],'graph':graph}},0)
  saved=orders.upsert('create-order',value,0)
  self.assertEqual(saved['summary'],value['flow']['intent']['purpose'])
  self.assertEqual(saved['flow']['intent']['success'],'页面显示新订单编号。')
  self.assertTrue(orders.list_topics('flows')[0]['hasIntent'])
  self.assertEqual(saved['flow']['steps'],[])
  self.assertEqual(saved['flow']['graph']['edges'][2]['condition'],'else 参数无效')
  self.assertEqual(saved['flow']['graph']['nodes'][4]['checks'],['检查必填字段和请求体'])
  self.assertTrue(orders.validate()['valid'])
  with self.assertRaisesRegex(ValueError,'新流程必须写'):
   orders.upsert('no-purpose',{'category':'flows','title':'空说明','summary':'入口到结果',
                                 'flow':{'steps':[{'title':'处理'}]}},0)
  with self.assertRaisesRegex(ValueError,'不能只重复标题'):
   orders.upsert('repeated-title',{**value,'flow':{**value['flow'],'intent':{'purpose':'创建订单','success':'页面显示订单编号。'}}},0)
  cases=[]
  missing_ref=deepcopy(graph);missing_ref['nodes'][1].pop('ref');cases.append(missing_ref)
  missing_check=deepcopy(graph);missing_check['nodes'][4]['checks']=[];cases.append(missing_check)
  missing_result=deepcopy(graph);missing_result['nodes'][3].pop('description');cases.append(missing_result)
  unlabeled=deepcopy(graph);unlabeled['edges'][2].pop('condition');cases.append(unlabeled)
  disconnected=deepcopy(graph);disconnected['edges'].pop();cases.append(disconnected)
  implicit_branch=deepcopy(graph);implicit_branch['edges'].append({'from':'save','to':'bad'});cases.append(implicit_branch)
  for index,candidate in enumerate(cases):
   with self.subTest(case=index),self.assertRaises(ValueError):
    orders.upsert('create-order',{**value,'flow':{**value['flow'],'graph':candidate}},1)
  self.assertEqual(orders.get_topic('create-order')['revision'],1)
  with self.assertRaisesRegex(ValueError,'flow.intent.success'):
   orders.upsert('create-order',{**value,'flow':{**value['flow'],'intent':{'purpose':'用户提交订单'}}},1)
  with self.assertRaisesRegex(ValueError,'保留 flow.intent'):
   orders.upsert('create-order',{**value,'flow':{'triggers':[{'when':'收到 POST /orders'}],'steps':[{'title':'保存订单'}]}},1)

 def test_version_six_stays_readable_until_explicit_graph_migration(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'旧流程'})
  value={'category':'flows','title':'查询订单','summary':'旧线性步骤',
         'flow':explained({'triggers':[{'when':'收到 GET /orders'}],'steps':[{'title':'读取订单'}]},'用户查看订单时，系统返回已有订单。','页面显示订单列表。')}
  orders.upsert('query-order',value,0)
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.execute('DROP TABLE flow_graphs')
   connection.execute('DROP TABLE flow_intents')
   connection.execute('UPDATE meta SET schema_version=6')
   connection.commit()
  self.assertIsNone(orders.get_topic('query-order')['flow']['graph'])
  self.assertIsNone(orders.get_topic('query-order')['flow']['intent'])
  self.assertEqual(orders.get_topic('query-order')['flow']['steps'][0]['title'],'读取订单')
  self.assertFalse(orders.list_topics('flows')[0]['hasIntent'])
  self.assertEqual(orders.validate()['flowsWithoutPurpose'],['query-order'])
  legacy={**value,'flow':{'triggers':[{'when':'收到 GET /orders'}],'steps':[{'title':'再次读取订单'}]}}
  self.assertEqual(orders.upsert('query-order',legacy,1)['revision'],2)
  graph={'nodes':[{'id':'start','kind':'start','title':'开始'},
                  {'id':'done','kind':'end','title':'完成','description':'订单列表已返回。'}],
         'edges':[{'from':'start','to':'done'}]}
  updated={**value,'flow':{**value['flow'],'graph':graph,
                          'intent':{'purpose':'用户查看订单，系统返回最新订单列表。',
                                    'success':'页面显示订单列表。'}}}
  with self.assertRaisesRegex(ValueError,'migrate'):
   orders.upsert('query-order',updated,2)
  self.assertEqual(orders.migrate()['schemaVersion'],7)
  self.assertEqual(orders.upsert('query-order',updated,2)['flow']['graph'],
                   {'nodes':[{'id':'start','kind':'start','title':'开始','description':'','ref':'','checks':[]},
                             {'id':'done','kind':'end','title':'完成','description':'订单列表已返回。','ref':'','checks':[]}],
                    'edges':[{'from':'start','to':'done','condition':''}]})
  self.assertTrue(orders.list_topics('flows')[0]['hasIntent'])
  self.assertTrue(orders.validate()['valid'])


if __name__=='__main__':unittest.main()
