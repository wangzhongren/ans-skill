import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]))
import role_atlas as graph
from serve_dashboard import Dashboard

class RoleAtlasTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name).resolve()
  self.put('role-cards/a/role-card.md','# Role A\n\nIncrement a counter.\n')
  self.put('role-cards/a/boundary.md','# Section 1\n| file | `src/services/a.ts` | owner |\n')
  self.put('role-cards/a/docs/functional-description.md','# Counter\n\nIncrement, then save.\n')
  self.put('role-cards/b/role-card.md','# Role B\n\nStorage.\n')
  self.put('role-cards/b/boundary.md','# Section 1\n| file | `src/providers/b.ts` | owner |\n| file | `src/providers/unrelated.ts` | owner |\n')
  self.put('src/services/a.ts',"import '../providers/b';\ncount += 1;\nsave(count);\n")
  self.put('src/providers/b.ts','store.set(value);\n');self.put('src/providers/unrelated.ts','unrelated();')
  self.spec={'schemaVersion':1,'roles':{'a':[{'id':'increment','name':'Increment','scenarios':[{'id':'normal','name':'Normal','initialState':{'count':0},'steps':[{'title':'Add','file':'src/services/a.ts','quote':'count += 1;','set':{'count':1}},{'title':'Save','file':'src/providers/b.ts','quote':'store.set(value);','set':{'saved':True}}]}]}]}}
  self.put('doc/design/flows.json',json.dumps(self.spec))
 def put(self,path,content):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content);return p
 def build(self):return graph.build(self.root,'doc/design/flows.json',role_id='a')[0]
 def generate(self,role=None):
  args=['--root',str(self.root),'--flows','doc/design/flows.json']
  if role:args+=['--role',role]
  with contextlib.redirect_stdout(io.StringIO()):return graph.main(args)
 def test_scoped_nodes_and_one_hop_external(self):
  result=self.build();self.assertEqual({n['id'] for n in result['nodes']},{'src/services/a.ts','src/providers/b.ts'})
  self.assertNotIn('src/providers/unrelated.ts',result['sourceHashes'])
  self.assertEqual(result['edges'][0]['kind'],'static-reference')
  self.assertEqual(result['role']['documents'],['role-cards/a/docs/functional-description.md'])
 def test_source_lines_and_state_snapshots(self):
  result=self.build();sc=result['functions'][0]['scenarios'][0]
  self.assertEqual(sc['initialState'],{'count':0});self.assertEqual(sc['steps'][0]['line'],2)
  self.assertEqual(sc['steps'][0]['stateAfter'],{'count':1});self.assertEqual(sc['steps'][1]['stateAfter'],{'count':1,'saved':True})
  self.assertTrue(sc['steps'][1]['external'])
 def test_missing_anchor_refuses_output_overwrite(self):
  self.generate();p=self.root/'doc/role-atlas/index.json';before=p.read_bytes()
  self.put('src/services/a.ts','anchor changed')
  self.assertEqual(self.generate(),2);self.assertEqual(p.read_bytes(),before)
 def test_freshness_and_source_context(self):
  self.generate();server=Dashboard(self.root);self.assertTrue(server.role_atlas('a')['freshness']['current'])
  self.assertIn('count += 1;',server.role_source('a','src/services/a.ts',2)['text'])
  self.put('src/services/a.ts','new source')
  self.assertFalse(server.role_atlas('a')['freshness']['current'])
 def test_no_functions_is_honest_overview(self):
  result=graph.build(self.root,role_id='a')[0];self.assertEqual(result['functions'],[]);self.assertTrue(result['warnings'])
 def test_traversal_and_undeclared_step_rejected(self):
  self.spec['roles']['a'][0]['scenarios'][0]['steps'][0]['file']='../secret'
  self.put('doc/design/flows.json',json.dumps(self.spec))
  with self.assertRaises(ValueError):self.build()
  with self.assertRaises(ValueError):graph.checked(self.root,'../secret')
 def test_scoped_source_api_rejects_other_files(self):
  self.generate();server=Dashboard(self.root)
  with self.assertRaises(ValueError):server.role_source('a','src/providers/unrelated.ts',1)
  with self.assertRaises(ValueError):server.role_source('a','../secret',1)
 def test_readonly_boundary_and_duplicate_function(self):
  self.put('role-cards/a/boundary.md','# Section 1\n| file | `src/services/a.ts` | 只读引用 |')
  result=self.build();self.assertEqual(result['nodes'][0]['access'],'read-only')
  self.spec['roles']['a'].append(self.spec['roles']['a'][0]);self.put('doc/design/flows.json',json.dumps(self.spec))
  with self.assertRaises(ValueError):self.build()
 def test_single_role_update_preserves_other_index_entries(self):
  self.generate();self.assertEqual(self.generate('a'),0)
  self.assertEqual({r['id'] for r in json.loads((self.root/'doc/role-atlas/index.json').read_text())['roles']},{'a','b'})
 def test_steps_are_data_not_executed(self):
  self.spec['roles']['a'][0]['name']='<script>alert(1)</script>'
  self.spec['roles']['a'][0]['scenarios'][0]['steps'][0]['set']={'value':'process.exit()'}
  self.put('doc/design/flows.json',json.dumps(self.spec));result=self.build()
  self.assertEqual(result['functions'][0]['scenarios'][0]['steps'][0]['stateAfter']['value'],'process.exit()')

if __name__=='__main__':unittest.main()
