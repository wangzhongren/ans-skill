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
  created=orders.upsert('order-export',{'category':'flows','title':'导出','summary':'导出订单','details':'读取订单','refs':['src/orders.py'],'flow':{'steps':[{'title':'读取订单'}]}},0)
  self.assertEqual(created['revision'],1)
  self.assertEqual(payments.list_topics(),[])
  with self.assertRaises(ValueError):payments.get_topic('order-export')
  with self.assertRaises(ValueError):orders.upsert('order-export',{'category':'flows','title':'覆盖','summary':'错误版本','flow':{'steps':[{'title':'读取'}]}},0)
  self.assertEqual(orders.get_topic('order-export')['title'],'导出')
  self.assertEqual(orders.upsert('order-export',{'category':'flows','title':'导出','summary':'生成文件','flow':{'steps':[{'title':'写文件'}]}},1)['revision'],2)
  self.assertEqual(orders.search('生成')[0]['topic_id'],'order-export')
  self.assertIsNotNone(orders.delete('order-export',2)['deleted_at'])
  self.assertEqual(orders.list_topics(),[])
  self.assertIsNone(orders.delete('order-export',3,restore=True)['deleted_at'])
  self.assertEqual(orders.set_overview({'title':'订单总览','summary':'已更新'},1)['revision'],2)
  self.assertEqual(payments.overview()['summary'],'支付流程')

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
   if category=='events':value['trigger']={'when':'订单创建','action':'启动导出','consumers':['导出流程']}
   if category=='data':value['data']={'owner':'订单角色','fields':[{'name':'orderId','type':'string','description':'订单编号','required':True}]}
   if category=='interfaces':value['interface']={'entry':'orders.export','method':'POST','requestUrl':'/api/orders/export','inputs':[{'name':'orderId','type':'string','required':True}],'outputs':[{'name':'exportId','type':'string'}]}
   orders.upsert(topic_id,value,0)
  linked=['order-created','order-record','order-api']
  flow={'steps':[{'title':'处理订单'}],'triggeredBy':['order-created'],'inputs':['order-record'],'outputs':['order-record'],'interfaces':['order-api']}
  orders.upsert('order-export',{'category':'flows','title':'导出','summary':'流程','links':linked,'flow':flow},0)
  orders.set_overview({'title':'订单总览','summary':'流程','steps':[{'title':'处理','links':linked}]},1)
  self.assertEqual(orders.get_topic('order-export')['links'],linked)
  self.assertEqual(orders.get_topic('order-export')['flow']['triggeredBy'],['order-created'])
  self.assertEqual(orders.get_topic('order-created')['trigger']['when'],'订单创建')
  self.assertEqual(orders.get_topic('order-record')['data']['fields'][0]['name'],'orderId')
  self.assertEqual(orders.get_topic('order-api')['interface']['requestUrl'],'/api/orders/export')
  self.assertEqual(orders.get_topic('order-api')['interface']['outputs'][0]['name'],'exportId')
  self.assertEqual(orders.get_topic('order-api')['interface']['method'],'POST')
  with self.assertRaises(ValueError):orders.upsert('bad-api',{'category':'interfaces','title':'缺少方法','summary':'错误','interface':{'entry':'orders.export','requestUrl':'/api/orders/export','inputs':[{'name':'orderId','type':'string'}],'outputs':[]}},0)
  self.assertEqual(orders.overview()['steps'][0]['links'],linked)
  payments.upsert('payment-event',{'category':'events','title':'支付事件','summary':'支付专属','trigger':{'when':'支付成功','action':'更新支付状态'}},0)
  with self.assertRaises(ValueError):orders.upsert('invalid-flow',{'category':'flows','title':'无效关联','summary':'跨角色','flow':{'steps':[{'title':'处理'}],'triggeredBy':['payment-event']}},0)
  with self.assertRaises(ValueError):orders.upsert('wrong-input',{'category':'flows','title':'输入类型错误','summary':'错误','flow':{'steps':[{'title':'处理'}],'inputs':['order-created']}},0)
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
  self.assertEqual(orders.migrate()['schemaVersion'],3)
  self.assertEqual(orders.overview()['summary'],'保留内容')
  self.assertEqual(orders.list_topics(),[])

 def test_migration_preserves_version_two_rows(self):
  orders=ContextStore(self.root,'订单');orders.init({'title':'订单总览','summary':'版本二内容'})
  database=self.root/'project-context/context.sqlite3'
  with closing(sqlite3.connect(database)) as connection:
   connection.executescript('DROP TABLE topic_fields; DROP TABLE interface_specs; DROP TABLE data_schemas; UPDATE meta SET schema_version=2;')
   connection.commit()
  with self.assertRaises(ValueError):orders.overview()
  self.assertTrue(orders.migrate()['changed'])
  self.assertEqual(orders.overview()['summary'],'版本二内容')


if __name__=='__main__':unittest.main()
