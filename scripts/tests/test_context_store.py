import json
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
   folder=self.root/'角色卡'/role;folder.mkdir(parents=True);(folder/'role-card.md').write_text('# '+role)

 def test_one_database_role_filters_and_revisions(self):
  orders=ContextStore(self.root,'订单');payments=ContextStore(self.root,'支付')
  orders.init({'title':'订单总览','summary':'订单流程','steps':[{'title':'入口','description':'接收订单'}]})
  payments.init({'title':'支付总览','summary':'支付流程'})
  self.assertEqual(len(list((self.root/'project-context').glob('*.sqlite3'))),1)
  created=orders.upsert('order-export',{'category':'flows','title':'导出','summary':'导出订单','details':'读取订单','refs':['src/orders.py']},0)
  self.assertEqual(created['revision'],1)
  self.assertEqual(payments.list_topics(),[])
  with self.assertRaises(ValueError):payments.get_topic('order-export')
  with self.assertRaises(ValueError):orders.upsert('order-export',{'category':'flows','title':'覆盖','summary':'错误版本'},0)
  self.assertEqual(orders.get_topic('order-export')['title'],'导出')
  self.assertEqual(orders.upsert('order-export',{'category':'flows','title':'导出','summary':'生成文件'},1)['revision'],2)
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
   orders.upsert(topic_id,{'category':category,'title':topic_id,'summary':'可从流程进入'},0)
  linked=['order-created','order-record','order-api']
  orders.upsert('order-export',{'category':'flows','title':'导出','summary':'流程','links':linked},0)
  orders.set_overview({'title':'订单总览','summary':'流程','steps':[{'title':'处理','links':linked}]},1)
  self.assertEqual(orders.get_topic('order-export')['links'],linked)
  self.assertEqual(orders.overview()['steps'][0]['links'],linked)
  payments.upsert('payment-event',{'category':'events','title':'支付事件','summary':'支付专属'},0)
  with self.assertRaises(sqlite3.IntegrityError):orders.upsert('invalid-flow',{'category':'flows','title':'无效关联','summary':'跨角色','links':['payment-event']},0)
  self.assertEqual(orders.list_topics('flows')[0]['topic_id'],'order-export')


if __name__=='__main__':unittest.main()
