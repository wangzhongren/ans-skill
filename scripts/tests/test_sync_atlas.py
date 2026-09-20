import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
SPEC=importlib.util.spec_from_file_location('sync_atlas',Path(__file__).parents[1]/'sync_atlas.py')
a=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(a)
class AtlasTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
  self.root=Path(self.temp.name)/'project';self.root.mkdir();self.out=Path(self.temp.name)/'atlas'
 def put(self,path,text):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return p
 def test_real_references_cycles_and_exclusions(self):
  self.put('service/index.js',"export { run } from './impl/run.js';")
  self.put('service/impl/run.js',"import '../../provider/index.js';")
  self.put('provider/index.js',"require('../service/index.js'); require('./missing'); require(name);")
  self.put('provider/vendor/hidden.js','ignore')
  d=a.scan(self.root)
  self.assertEqual(len(d['files']),3);self.assertEqual(len(d['edges']),3)
  self.assertEqual(len(d['cycles']),1);self.assertEqual(len(d['unresolved']),1);self.assertTrue(d['dynamic'])
 def test_python_root_and_relative(self):
  self.put('model/__init__.py','');self.put('model/order.py','class Order: pass')
  self.put('service/logic.py','from model.order import Order\nfrom .helper import work')
  self.put('service/helper.py','def work(): pass')
  d=a.scan(self.root)
  self.assertEqual({e['target'] for e in d['edges']},{'model/order.py','service/helper.py'})
 def test_snapshot_freshness_and_safe_embedding(self):
  self.put('interface/view.js',"console.log('done')")
  self.assertEqual(a.main(['--root',str(self.root),'--out',str(self.out)]),0)
  self.assertEqual(a.main(['--root',str(self.root),'--out',str(self.out),'--check']),0)
  d=json.loads((self.out/'atlas.json').read_text())
  path='interface/view.js';d['annotations']={path:{'sourceHash':d['files'][0]['sha256'],'summary':'</script><script>alert(1)</script>'}}
  (self.out/'atlas.json').write_text(json.dumps(d))
  a.main(['--root',str(self.root),'--out',str(self.out)])
  self.assertNotIn('</script><script>alert(1)',(self.out/'five-layer-code-atlas.html').read_text())
  self.put(path,'changed')
  self.assertEqual(a.main(['--root',str(self.root),'--out',str(self.out),'--check']),1)
  a.main(['--root',str(self.root),'--out',str(self.out)])
  self.assertEqual(json.loads((self.out/'atlas.json').read_text())['annotations'][path]['status'],'stale')
 def test_manual_relation_invalidated_after_change(self):
  self.put('service/a.py','x=1');self.put('provider/b.py','y=2')
  d=a.scan(self.root);hashes={f['id']:f['sha256'] for f in d['files']}
  e={'source':'service/a.py','target':'provider/b.py','line':1,'sourceHash':hashes['service/a.py'],'targetHash':hashes['provider/b.py'],'reason':'checked injected dependency'}
  a.review(d,{'aiRelations':[e]});self.assertEqual(len(d['edges']),1)
  self.put('provider/b.py','y=3');d=a.scan(self.root);a.review(d,{'aiRelations':[e]})
  self.assertEqual(d['edges'],[]);self.assertEqual(d['aiRelations'][0]['status'],'stale')
 def test_parse_errors_unsupported_and_deleted_files(self):
  self.put('model/a.py','bad syntax here!!!');self.put('service/a.go','package service')
  d=a.scan(self.root);self.assertEqual(len(d['parseErrors']),1)
  self.assertIn('service/a.go',d['coverage']['inventoryOnly'])
  (self.root/'service/a.go').unlink();d=a.scan(self.root)
  self.assertNotIn('service/a.go',[f['id'] for f in d['files']])
 def test_symlink_outside_root_not_followed(self):
  external=Path(self.temp.name)/'outside.py';external.write_text('secret=1')
  (self.root/'provider').mkdir();(self.root/'provider/secret.py').symlink_to(external)
  d=a.scan(self.root);self.assertEqual(d['files'],[]);self.assertEqual(len(d['coverage']['skipped']),1)
if __name__=='__main__':unittest.main()
