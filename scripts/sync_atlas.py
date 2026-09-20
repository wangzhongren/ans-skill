#!/usr/bin/env python3
"""Read-only source inventory + best-effort static references; write JSON and offline atlas."""
import argparse, ast, hashlib, json, os, re, tempfile, webbrowser
from datetime import datetime, timezone
from pathlib import Path

LAYERS = {'interface':'interface','interfaces':'interface','pipeline':'pipelines','pipelines':'pipelines','service':'services','services':'services','provider':'providers','providers':'providers','model':'models','models':'models'}
SUPPORT = {'utils','resource','resources'}
SKIP = {'.git','node_modules','vendor','vendors','__pycache__','.venv','venv','dist','build','target','test','tests','doc','docs','coverage','runtime','logs'}
EXTS = {'.js','.mjs','.cjs','.jsx','.ts','.tsx','.py','.go','.rs','.java','.kt','.cs','.c','.h','.cpp','.hpp','.swift','.rb','.php','.html','.css','.json','.vue','.svelte'}
JS = {'.js','.mjs','.cjs','.jsx','.ts','.tsx'}

def digest(data): return hashlib.sha256(data).hexdigest()
def dump(data): return json.dumps(data,ensure_ascii=False,indent=2)+'\n'
def safe_path(value):
    return isinstance(value,str) and bool(value) and not value.startswith('/') and not re.search(r'[\\\x00-\x1f:]',value) and all(x not in {'.','..',''} for x in value.split('/'))
def atomic(path,text):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(dir=path.parent,prefix='.'+path.name)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(text)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)

def cycles(nodes,edges):
    # Iterative Kosaraju: avoid recursion depth limits on large repositories.
    adj={n:[] for n in nodes}; rev={n:[] for n in nodes}
    for e in edges:adj[e['source']].append(e['target']);rev[e['target']].append(e['source'])
    seen=set(); order=[]
    for n in adj:
        if n in seen:continue
        stack=[(n,False)]
        while stack:
            v,done=stack.pop()
            if done:order.append(v);continue
            if v in seen:continue
            seen.add(v);stack.append((v,True));stack.extend((w,False) for w in adj[v] if w not in seen)
    seen=set(); result=[]
    for n in reversed(order):
        if n in seen:continue
        comp=[]; stack=[n];seen.add(n)
        while stack:
            v=stack.pop();comp.append(v)
            for w in rev[v]:
                if w not in seen:seen.add(w);stack.append(w)
        if len(comp)>1 or n in adj[n]:result.append(sorted(comp))
    return sorted(result)

def resolve_layout(root, source_root=None):
    """Keep output/IDs project-relative while selecting layer-containing source roots."""
    project=Path(root).resolve()
    if not project.is_dir():raise ValueError('Project root must be an existing directory')
    markers={'.git','package.json','pyproject.toml','Cargo.toml','go.mod','pom.xml','build.gradle'}
    def has_layers(path):
        return any((path/name).is_dir() and not (path/name).is_symlink() for name in LAYERS)
    # Compatibility with the former --root PROJECT/src examples. An explicit
    # source-root or a src directory owning its own project manifest wins.
    if source_root is None and project.name=='src' and has_layers(project) and not any((project/name).exists() for name in markers):
        project=project.parent
    if source_root is not None:
        chosen=Path(source_root)
        chosen=chosen if chosen.is_absolute() else project/chosen
        if not chosen.resolve().is_relative_to(project):raise ValueError('Source root must stay inside the project')
        if any(part.is_symlink() for part in [chosen,*chosen.parents] if part.is_relative_to(project)):
            raise ValueError('Symlink source roots are not followed')
        if not chosen.is_dir():raise ValueError('Source root must be an existing directory')
        sources=[chosen.resolve()]
    else:
        sources=[]
        if has_layers(project):sources.append(project)
        nested=project/'src'
        if nested.is_dir() and not nested.is_symlink() and has_layers(nested):sources.append(nested)
        if not sources:sources=[project]
    return project,sources


def inventory(root, sources=None):
    root=Path(root).resolve()
    if sources is None:root,sources=resolve_layout(root)
    rows=[]; contents={}; unread=[]; unknown=[]; skipped=[]
    prefixes=[tuple(path.relative_to(root).parts) for path in sources]
    for base,dirs,names in os.walk(root,followlinks=False):
        dirs[:]=sorted(d for d in dirs if d not in SKIP and not d.startswith('.') and not (Path(base)/d).is_symlink())
        for name in sorted(names):
            p=Path(base)/name; rel=p.relative_to(root).as_posix(); parts=p.relative_to(root).parts
            local=None; prefix=()
            for candidate in sorted(prefixes,key=len,reverse=True):
                if parts[:len(candidate)]==candidate and len(parts)>len(candidate):
                    possible=parts[len(candidate):]
                    if possible[0] in LAYERS or possible[0] in SUPPORT or (len(possible)==1 and p.stem.lower() in {'main','__main__','program'}):
                        local=possible;prefix=candidate;break
            # The project entry and support assets remain in scope even when
            # the five layers live under src/ or an explicit custom root.
            if local is None and (parts[0] in SUPPORT or (len(parts)==1 and p.stem.lower() in {'main','__main__','program'})):
                local=parts
            if local is None:continue
            first=local[0];entry=len(local)==1 and p.stem.lower() in {'main','__main__','program'}
            if p.is_symlink():skipped.append({'path':rel,'reason':'symlink'});continue
            if p.suffix.lower() not in EXTS:continue
            layer=LAYERS.get(first,'interface');group=p.parent.relative_to(root).as_posix()
            if entry:group='/'.join((*prefix,'entry'))
            elif len(local)==2:group='/'.join((*prefix,first,'root'))
            row={'id':rel,'path':rel,'name':name,'layer':layer,'role':'entry' if entry else first if first in SUPPORT else layer,'platform':'common','group':group,'groupTitle':group,'ext':p.suffix.lower()}
            try:
                raw=p.read_bytes();row['sha256']=digest(raw)
                if len(raw)>2*1024*1024:raise ValueError('over 2 MiB: inventory only')
                contents[rel]=raw.decode('utf-8-sig')
            except (OSError,UnicodeError,ValueError) as e:unread.append({'source':rel,'message':str(e)})
            rows.append(row)
            if row['ext'] not in JS|{'.py','.html','.css'}:unknown.append(rel)
    return sorted(rows,key=lambda r:r['id']),contents,unread,unknown,skipped

def normalize(path):return os.path.normpath(path).replace('\\','/')
def resolve(spec,source,ids):
    base=normalize(str(Path(source).parent/spec))
    if base.startswith('../') or base=='..':return None
    candidates=[base]+[base+x for x in sorted(EXTS)]+[base+'/index'+x for x in ['.js','.ts','.mjs','.cjs','.tsx','.jsx']]+[base+'/__init__.py']
    # TS projects may import the emitted .js filename.
    if base.endswith('.js'):candidates.extend([base[:-3]+'.ts',base[:-3]+'.tsx'])
    return next((p for p in candidates if p in ids),None)

def scan(root, source_root=None):
    root,sources=resolve_layout(root,source_root)
    files,texts,errors,unsupported,skipped=inventory(root,sources); ids={r['id'] for r in files}; edges=[]; missing=[]; dynamic=[];external=[]
    def add(src,spec,line,kind):
        target=resolve(spec,src,ids)
        if target:edges.append({'source':src,'target':target,'line':line,'kind':kind,'evidence':'static-heuristic' if Path(src).suffix in JS|{'.html','.css'} else 'static-ast'})
        else:missing.append({'source':src,'spec':spec,'line':line,'kind':kind})
    pattern=re.compile(r'''\b(?:require\s*\(|import\s*\()\s*['"]([^'"\n]+)['"]|\b(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?['"]([^'"\n]+)['"]''')
    for src,text in texts.items():
        ext=Path(src).suffix.lower()
        if ext in JS:
            # Deliberately heuristic; comments and aliases can require manual review.
            for m in pattern.finditer(text):
                spec=next(g for g in m.groups() if g is not None);line=text.count('\n',0,m.start())+1
                if spec.startswith('.'):add(src,spec,line,'JS/TS 字面量引用（启发式）')
                else:external.append({'source':src,'spec':spec,'line':line,'kind':'外部包或未配置别名'})
            for m in re.finditer(r'\b(?:require|import)\s*\(\s*(?![\s\'"])\S',text):dynamic.append({'source':src,'line':text.count('\n',0,m.start())+1,'kind':'动态导入'})
        elif ext=='.py':
            try:tree=ast.parse(text)
            except SyntaxError as e:errors.append({'source':src,'message':str(e)});continue
            for node in ast.walk(tree):
                if not isinstance(node,(ast.Import,ast.ImportFrom)):continue
                if isinstance(node,ast.Import):mods=[x.name for x in node.names];level=0
                else:mods=[node.module or ''];level=node.level
                for mod in mods:
                    if level:
                        base=Path(src).parent
                        for _ in range(level-1):base=base.parent
                        bases=[base]
                    else:
                        bases=[Path('.')]+[source.relative_to(root) for source in sources if source!=root]
                    found=[]
                    for base in bases:
                        key=normalize(str(base/mod.replace('.','/')))
                        candidates=[key+'.py',key+'/__init__.py']
                        if isinstance(node,ast.ImportFrom):candidates += [key+'/'+x.name+'.py' for x in node.names]+[key+'/'+x.name+'/__init__.py' for x in node.names]
                        matches=[p for p in candidates if p in ids]
                        if matches:
                            found=matches;break
                    for dest in sorted(set(found)):edges.append({'source':src,'target':dest,'line':node.lineno,'kind':'Python import（AST）','evidence':'static-ast'})
                    if not found:
                        entry={'source':src,'spec':'.'*level+mod,'line':node.lineno,'kind':'Python 相对引用' if level else 'Python 外部包或未配置路径'}
                        (missing if level else external).append(entry)
        elif ext in {'.html','.css'}:
            for m in re.finditer(r'''(?:src|href)\s*=\s*['"]([^'"]+)['"]|url\(\s*['"]?([^\s)'";]+)''',text,re.I):
                spec=next(g for g in m.groups() if g);spec=spec.split('#')[0].split('?')[0]
                if not spec or spec.startswith(('/', 'data:')) or '://' in spec:continue
                add(src,spec if spec.startswith('.') else './'+spec,text.count('\n',0,m.start())+1,'静态资源引用（启发式）')
    edges=sorted({(e['source'],e['target'],e['line'],e['kind']):e for e in edges}.values(),key=lambda e:(e['source'],e['line'],e['target']))
    fp=digest(json.dumps([(f['id'],f.get('sha256')) for f in files],ensure_ascii=False).encode())
    return {'schemaVersion':1,'project':root.name,'date':datetime.now().astimezone().date().isoformat(),'generatedAt':datetime.now(timezone.utc).isoformat(),'sourceBaseUri':root.as_uri()+'/','sourceRoots':[source.relative_to(root).as_posix() for source in sources],'sourceFingerprint':fp,'files':files,'edges':edges,'unresolved':missing,'dynamic':dynamic,'external':external,'externalCount':len(external),'parseErrors':errors,'coverage':{'mode':'static references; not runtime call graph','extractors':['Python AST (root/relative resolution)','JS/TS literal imports (heuristic)','HTML/CSS references (heuristic)'],'inventoryOnly':unsupported,'skipped':skipped,'excludedDirectories':sorted(SKIP),'limitations':['JS/TS comments may cause false positives; aliases and dynamic imports require review','Unsupported languages are inventoried only; no runtime execution','Resources outside the inventory may appear unresolved','Nonstandard source layouts require --source-root; file IDs remain project-relative']},'cycles':cycles(ids,edges),'layerCounts':{k:sum(f['layer']==k for f in files) for k in set(LAYERS.values())}}

def review(data,previous):
    annotations=previous.get('annotations',{}); manual=previous.get('aiRelations',[])
    if not isinstance(annotations,dict) or not isinstance(manual,list):raise ValueError('annotations must be an object; aiRelations must be an array')
    rows={f['id']:f for f in data['files']}; kept={};warn=[]
    for path,note in annotations.items():
        if not isinstance(note,dict):raise ValueError('annotation must be an object')
        if path in rows:kept[path]={**note,'status':'current' if note.get('sourceHash')==rows[path].get('sha256') else 'stale'}
        else:
            kept[path]={**note,'status':'orphaned'}
            warn.append({'path':path,'reason':'annotation target removed','annotation':note})
    reviewed=[]
    for e in manual:
        if not isinstance(e,dict):raise ValueError('aiRelations entry must be an object')
        valid=e.get('source') in rows and e.get('target') in rows
        valid=valid and isinstance(e.get('line'),int) and e['line']>0 and isinstance(e.get('reason'),str) and bool(e['reason'])
        valid=valid and bool(e.get('sourceHash')) and bool(e.get('targetHash')) and e['sourceHash']==rows[e['source']].get('sha256') and e['targetHash']==rows[e['target']].get('sha256')
        item={**e,'status':'current' if valid else 'stale'};reviewed.append(item)
        if valid:data['edges'].append({'source':e['source'],'target':e['target'],'line':e['line'],'kind':'人工核实文件级调用 · '+e['reason'],'evidence':'reviewed'})
        else:warn.append({'relation':item,'reason':'missing endpoint, evidence, or changed hash; excluded from graph'})
    data.update(annotations=kept,aiRelations=reviewed,reviewWarnings=warn)
    data['cycles']=cycles(rows,data['edges'])

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root','--project-root',dest='root',type=Path,required=True,help='project root; detects root-level and src/ layer folders')
    parser.add_argument('--source-root',type=Path,help='optional layer source directory relative to project root (or an absolute directory inside it)')
    parser.add_argument('--out',type=Path,help='default: PROJECT/doc/architecture, independent of source root')
    parser.add_argument('--check',action='store_true',help='read-only freshness check')
    parser.add_argument('--open',action='store_true',help='open generated local HTML after successful sync')
    args=parser.parse_args(argv)
    try:root,sources=resolve_layout(args.root,args.source_root)
    except ValueError as exc:parser.error(str(exc))
    out=(args.out or root/'doc/architecture').resolve()
    json_path=out/'atlas.json';html_path=out/'five-layer-code-atlas.html'
    previous=json.loads(json_path.read_text()) if json_path.exists() else {}
    data=scan(root,args.source_root);review(data,previous)
    template=Path(__file__).resolve().parents[1]/'assets/code-atlas/viewer.html'
    text=template.read_text();data['templateHash']=digest(text.encode());data['scannerHash']=digest(Path(__file__).read_bytes())
    payload=json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    if args.check:
        same=all(previous.get(k)==data.get(k) for k in ['sourceFingerprint','sourceBaseUri','sourceRoots','templateHash','scannerHash'])
        if not html_path.exists():same=False
        else:
            m=re.search(r'<script id="graph-data"[^>]*>(.*?)</script>',html_path.read_text(),re.S)
            same=same and bool(m) and json.loads(m.group(1))==previous
        print('CURRENT' if same else 'STALE: run sync without --check')
        return 0 if same else 1
    rendered=re.sub(r'(<script id="graph-data"[^>]*>).*?(</script>)',lambda m:m[1]+payload+m[2],text,flags=re.S)
    atomic(json_path,dump(data));atomic(html_path,rendered)
    print(dump({'json':str(json_path),'html':str(html_path),'files':len(data['files']),'edges':len(data['edges']),'unresolved':len(data['unresolved']),'inventoryOnly':len(data['coverage']['inventoryOnly']),'parseErrors':len(data['parseErrors']),'reviewWarnings':len(data['reviewWarnings'])}))
    if args.open:
        if not webbrowser.open(html_path.as_uri()):print('Viewer was generated but browser opening was not confirmed.')
    return 0
if __name__=='__main__':raise SystemExit(main())
