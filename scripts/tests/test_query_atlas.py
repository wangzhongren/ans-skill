import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).parents[1]))
import query_atlas as q
import sync_atlas as s

class QueryTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
  texts={'interface/a.js':"require('../pipeline/b.js');",'pipeline/b.js':"require('../service/c.js');",'service/c.js':"require('../provider/d.js');",'provider/d.js':"require('../service/c.js');",'model/alone.py':'x=1'}
  for path,text in texts.items():
   p=self.root/path;p.parent.mkdir(exist_ok=True);p.write_text(text)
  with contextlib.redirect_stdout(io.StringIO()):s.main(['--root',str(self.root)])
  self.path=self.root/'doc/architecture/atlas.json';self.data=json.loads(self.path.read_text())
 def test_direction_and_line_evidence(self):
  out=q.query(self.data,file='service/c.js');inc=q.query(self.data,file='service/c.js',direction='callers')
  self.assertEqual(out['edges'][0]['target'],'provider/d.js')
  self.assertEqual({e['source'] for e in inc['edges']},{'pipeline/b.js','provider/d.js'})
  self.assertEqual(out['edges'][0]['line'],1);self.assertIn('evidence',out['edges'][0])
 def test_shortest_path_and_cycle(self):
  r=q.query(self.data,start='interface/a.js',target='provider/d.js')
  self.assertEqual(r['path'],['interface/a.js','pipeline/b.js','service/c.js','provider/d.js'])
  self.assertFalse(r['truncated'])
  r=q.query(self.data,start='interface/a.js',target='model/alone.py');self.assertFalse(r['found']);self.assertFalse(r['truncated'])
 def test_impact_transitive_cycle_excludes_origin(self):
  r=q.query(self.data,file='service/c.js',impact=True)
  self.assertEqual({x['file'] for x in r['dependents']},{'interface/a.js','pipeline/b.js','provider/d.js'})
 def test_bounds_are_reported(self):
  self.assertTrue(q.query(self.data,start='interface/a.js',target='provider/d.js',max_depth=1)['truncated'])
  self.assertTrue(q.query(self.data,file='provider/d.js',impact=True,limit=1)['truncated'])
  self.assertTrue(q.query(self.data,start='interface/a.js',target='provider/d.js',max_nodes=1)['truncated'])
 def test_invalid_nodes_and_schema(self):
  with self.assertRaises(ValueError):q.query(self.data,file='../secret')
  self.data['edges'][0]['target']='missing'
  with self.assertRaises(ValueError):q.validate(self.data)
 def test_fresh_stale_and_tampered_json(self):
  self.assertEqual(q.freshness(self.data,self.root),[])
  self.data['edges']=[];self.assertIn('edges',q.freshness(self.data,self.root))
  (self.root/'model/alone.py').write_text('x=2')
  buf=io.StringIO()
  with contextlib.redirect_stdout(buf):code=q.main(['--root',str(self.root),'--file','service/c.js'])
  self.assertEqual(code,3);self.assertEqual(json.loads(buf.getvalue())['status'],'stale')
 def test_cli_read_only_current_json(self):
  before=self.path.read_bytes();buf=io.StringIO()
  with contextlib.redirect_stdout(buf):code=q.main(['--root',str(self.root),'--file','service/c.js','--impact'])
  self.assertEqual(code,0);self.assertEqual(json.loads(buf.getvalue())['status'],'current');self.assertEqual(self.path.read_bytes(),before)
 def test_start_equals_target(self):
  r=q.query(self.data,start='service/c.js',target='service/c.js');self.assertEqual(r['pathLength'],0)
if __name__=='__main__':unittest.main()
