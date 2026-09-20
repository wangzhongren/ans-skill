import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]))
import sync_atlas as sync
import query_atlas as query

class LayoutTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name).resolve()/'project';self.root.mkdir()
 def put(self,path,text=''):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return p
 def run_sync(self,*args):
  with contextlib.redirect_stdout(io.StringIO()):return sync.main(list(args))
 def sample(self):
  self.put('main.ts',"import './src/interface/app';")
  self.put('src/interface/app.ts',"import '../services/public/index';")
  self.put('src/services/public/index.ts','export const run=1;')
 def test_nested_layers_root_entry_support_and_links(self):
  self.sample();self.put('utils/strings.py','');self.put('resource/data.json','{}')
  d=sync.scan(self.root);ids={f['id'] for f in d['files']}
  self.assertEqual(ids,{'main.ts','src/interface/app.ts','src/services/public/index.ts','utils/strings.py','resource/data.json'})
  self.assertEqual(d['sourceRoots'],['src']);self.assertEqual(d['sourceBaseUri'],self.root.as_uri()+'/')
  self.assertIn(('main.ts','src/interface/app.ts'),{(e['source'],e['target']) for e in d['edges']})
 def test_root_and_legacy_src_commands_share_one_output(self):
  self.sample();self.assertEqual(self.run_sync('--root',str(self.root)),0)
  self.assertEqual(self.run_sync('--root',str(self.root/'src'),'--check'),0)
  self.assertEqual(self.run_sync('--root',str(self.root/'src')),0)
  self.assertTrue((self.root/'doc/architecture/atlas.json').is_file());self.assertFalse((self.root/'src/doc').exists())
  self.assertEqual(self.run_sync('--project-root',str(self.root),'--source-root','src','--check'),0)
 def test_query_ids_are_project_relative_and_entry_changes_stale(self):
  self.sample();self.run_sync('--root',str(self.root))
  buf=io.StringIO()
  with contextlib.redirect_stdout(buf):code=query.main(['--root',str(self.root/'src'),'--from','main.ts','--to','src/services/public/index.ts'])
  result=json.loads(buf.getvalue());self.assertEqual(code,0);self.assertEqual(result['path'],['main.ts','src/interface/app.ts','src/services/public/index.ts'])
  self.put('main.ts','changed')
  with contextlib.redirect_stdout(io.StringIO()):code=query.main(['--root',str(self.root),'--file','main.ts'])
  self.assertEqual(code,3)
 def test_custom_source_and_output_roundtrip(self):
  self.put('lib/services/a.py','');self.put('main.py','from lib.services import a')
  out=self.root/'docs/architecture'
  self.run_sync('--root',str(self.root),'--source-root','lib','--out',str(out))
  d=json.loads((out/'atlas.json').read_text());self.assertEqual(d['sourceRoots'],['lib'])
  self.assertFalse((self.root/'lib/doc').exists());self.assertFalse((self.root/'doc').exists())
  with contextlib.redirect_stdout(io.StringIO()):code=query.main(['--root',str(self.root),'--source-root','lib','--atlas',str(out/'atlas.json'),'--file','main.py'])
  self.assertEqual(code,0)
 def test_python_imports_from_src_and_relative_modules(self):
  self.put('src/models/item.py','');self.put('src/services/helper.py','')
  self.put('src/services/work.py','from models.item import Item\nfrom .helper import run')
  targets={e['target'] for e in sync.scan(self.root)['edges']}
  self.assertEqual(targets,{'src/models/item.py','src/services/helper.py'})
 def test_flat_and_nested_layers_are_distinct_without_duplicates(self):
  self.put('service/a.js','');self.put('src/service/a.js','')
  d=sync.scan(self.root);self.assertEqual(d['sourceRoots'],['.','src']);self.assertEqual(len(d['files']),2)
  self.assertEqual({f['group'] for f in d['files']},{'service/root','src/service/root'})
 def test_source_root_escape_and_symlink_rejected(self):
  outside=Path(self.tmp.name)/'outside';outside.mkdir()
  with self.assertRaises(ValueError):sync.resolve_layout(self.root,outside)
  (self.root/'linked').symlink_to(outside,target_is_directory=True)
  with self.assertRaises(ValueError):sync.resolve_layout(self.root,'linked')
 def test_src_directory_with_own_manifest_is_its_own_project(self):
  self.put('src/pyproject.toml','');self.put('src/service/a.py','')
  project,sources=sync.resolve_layout(self.root/'src')
  self.assertEqual(project,self.root/'src');self.assertEqual(sources,[self.root/'src'])

if __name__=='__main__':unittest.main()
