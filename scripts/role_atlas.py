#!/usr/bin/env python3
"""Generate bounded per-role graphs and source-anchored, declarative function walkthroughs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import sync_atlas as atlas

MAX_BYTES=2*1024*1024

def checked(root,relative):
    if not atlas.safe_path(relative):raise ValueError('Invalid project-relative path: '+str(relative))
    path=root/relative
    if not path.resolve().is_relative_to(root) or any(p.is_symlink() for p in [path,*path.parents] if p.is_relative_to(root)):
        raise ValueError('Outside-root or symlink path: '+relative)
    return path

def text(root,relative):
    path=checked(root,relative)
    if path.stat().st_size>MAX_BYTES:raise ValueError('File exceeds 2 MiB: '+relative)
    return path.read_text(encoding='utf-8-sig')

def hash_file(root,relative):
    path=checked(root,relative)
    with path.open('rb') as stream:raw=stream.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('File exceeds 2 MiB: '+relative)
    return hashlib.sha256(raw).hexdigest()

def layer(path):
    return next((atlas.LAYERS[p] for p in Path(path).parts if p in atlas.LAYERS),'support')

def roles(root,role_directory=None):
    base=checked(root,role_directory) if role_directory else next((root/name for name in ['角色卡','role-cards'] if (root/name).is_dir()),root/'角色卡')
    result=[]
    if not base.is_dir():return result
    for folder in sorted(base.iterdir()):
        if not folder.is_dir() or folder.is_symlink() or folder.name.startswith('.'):continue
        card=folder/'role-card.md';boundary=folder/'boundary.md'
        if not card.is_file() or not boundary.is_file():continue
        card_path=card.relative_to(root).as_posix();boundary_path=boundary.relative_to(root).as_posix()
        content=text(root,card_path);lines=content.splitlines()
        name=next((s[2:].strip() for s in lines if s.startswith('# ')),folder.name)
        description=next((s.strip() for s in lines if s.strip() and not s.startswith(('#','-','|','```'))),'')
        files=[];inside=False
        for line in text(root,boundary_path).splitlines():
            if line.lstrip().startswith('#'):
                section='section 1' in line.lower() or '第 1 节' in line or '第1节' in line
                if inside and not section:break
                if section:inside=True
            if inside and line.lstrip().startswith('|'):
                for path in re.findall(r'`([^`]+)`',line):
                    if atlas.safe_path(path) and Path(path).suffix.lower() in atlas.EXTS:
                        checked(root,path)
                        files.append({'path':path,'access':'read-only' if re.search(r'只读|read.only',line,re.I) else 'declared-owner'})
        docs=[]
        for p in sorted(folder.rglob('functional-description.md'),key=lambda p:(len(p.parts),p.as_posix())):
            rel=p.relative_to(root).as_posix();text(root,rel);docs.append(rel)
        result.append({'id':folder.name,'name':name,'description':description,'card':card_path,'boundary':boundary_path,'documents':docs,'declaredFiles':files})
    return result


def build(root,flows_path=None,role_id=None,role_directory=None):
    root=Path(root).resolve();registry=roles(root,role_directory)
    if not registry:raise ValueError('No role cards with boundary documents found')
    selected=[r for r in registry if role_id is None or r['id']==role_id]
    if not selected:raise ValueError('Unknown role: '+str(role_id))
    spec={'schemaVersion':1,'roles':{}}
    if flows_path:
        spec=json.loads(text(root,flows_path))
        if spec.get('schemaVersion')!=1 or not isinstance(spec.get('roles'),dict):raise ValueError('Invalid flow specification')
        unknown=set(spec['roles'])-{r['id'] for r in registry}
        if unknown:raise ValueError('Flow specs reference unknown roles: '+str(sorted(unknown)))
    ownership={};ids=set()
    for role in registry:
        for f in role['declaredFiles']:
            ids.add(f['path'])
            if f['access']=='declared-owner':ownership.setdefault(f['path'],[]).append(role['id'])
    results=[]
    pattern=re.compile(r'''\b(?:require\s*\(|import\s*\()\s*['"]([^'"\n]+)['"]|\b(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?['"]([^'"\n]+)['"]''')
    for role in selected:
        hashes={};warnings=[];nodes={};edges=[]
        def source(path):
            value=text(root,path);hashes[path]=hash_file(root,path);return value
        def add_node(path,access='external'):
            if path not in nodes:
                checked(root,path)
                exists=(root/path).is_file()
                if exists:source(path)
                nodes[path]={'id':path,'path':path,'name':Path(path).name,'layer':layer(path),'access':access,'owners':ownership.get(path,[]),'exists':exists}
                if not exists:warnings.append('文件不存在：'+path)
            return nodes[path]
        source(role['card']);source(role['boundary'])
        for path in role['documents']:source(path)
        if flows_path:source(flows_path)
        for f in role['declaredFiles']:add_node(f['path'],f['access'])
        for f in role['declaredFiles']:
            path=f['path']
            if not (root/path).is_file() or Path(path).suffix not in atlas.JS:continue
            content=source(path)
            for match in pattern.finditer(content):
                specifier=next(v for v in match.groups() if v is not None)
                if not specifier.startswith('.'):continue
                target=atlas.resolve(specifier,path,ids)
                if target:
                    add_node(target)
                    edges.append({'source':path,'target':target,'line':content.count('\n',0,match.start())+1,'kind':'static-reference','label':'字面量引用（启发式）'})
        functions=[];function_ids=set()
        for function in spec['roles'].get(role['id'],[]):
            if not isinstance(function,dict) or not isinstance(function.get('id'),str) or function['id'] in function_ids:raise ValueError('Invalid/duplicate function ID')
            function_ids.add(function['id'])
            if not isinstance(function.get('scenarios'),list) or not function['scenarios']:raise ValueError('Function requires scenarios')
            scenarios=[];scenario_ids=set()
            for scenario in function['scenarios']:
                if not isinstance(scenario,dict) or not isinstance(scenario.get('id'),str) or scenario['id'] in scenario_ids:raise ValueError('Invalid/duplicate scenario ID')
                scenario_ids.add(scenario['id'])
                if not isinstance(scenario.get('initialState'),dict) or not isinstance(scenario.get('steps'),list) or not scenario['steps']:raise ValueError('Scenario requires initialState and steps')
                steps=[];state=json.loads(json.dumps(scenario['initialState']))
                for number,step in enumerate(scenario['steps'],1):
                    path=step.get('file');quote=step.get('quote');occurrence=step.get('occurrence',1)
                    if path not in ids:raise ValueError('Step source is outside declared role files: '+str(path))
                    if not isinstance(quote,str) or not quote or type(occurrence)is not int or occurrence<1:raise ValueError('Step requires source quote/occurrence')
                    content=source(path);matches=[m.start() for m in re.finditer(re.escape(quote),content)]
                    if len(matches)<occurrence:raise ValueError('Source anchor missing for '+role['id']+'/'+function['id']+': '+path+' '+quote[:60])
                    if not isinstance(step.get('set',{}),dict):raise ValueError('Step state patch must be data, not executable code')
                    add_node(path)
                    state.update(step.get('set',{}))
                    steps.append({**step,'index':number,'line':content.count('\n',0,matches[occurrence-1])+1,'layer':layer(path),'owners':ownership.get(path,[]),'external':path not in {f['path'] for f in role['declaredFiles']},'stateAfter':dict(state),'evidence':'source-anchored storyboard; not runtime trace'})
                scenarios.append({**scenario,'steps':steps})
            functions.append({**function,'scenarios':scenarios})
        role_conflicts={p:o for p,o in ownership.items() if len(o)>1 and p in nodes}
        if role_conflicts:warnings.append('存在多角色声明归属，图谱不自动修正权限：'+', '.join(role_conflicts))
        if not functions:warnings.append('尚未编排功能演示；仅提供角色文件总览。')
        results.append({'schemaVersion':1,'project':root.name,'generatedAt':datetime.now(timezone.utc).isoformat(),'role':{k:v for k,v in role.items() if k!='declaredFiles'},'nodes':list(nodes.values()),'edges':edges,'functions':functions,'sourceHashes':hashes,'warnings':warnings,'model':'declarative walkthrough: sample state changes, no application execution'})
    return results


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True);p.add_argument('--flows',help='Project-relative declarative function specifications');p.add_argument('--role');p.add_argument('--roles');p.add_argument('--out',type=Path)
    a=p.parse_args(argv);root=a.root.resolve();out=(a.out or root/'doc/role-atlas').resolve()
    try:
        graphs=build(root,a.flows,a.role,a.roles)
        # Compile every selected role before writing any output.
        out.mkdir(parents=True,exist_ok=True)
        for graph in graphs:
            filename='role-'+hashlib.sha256(graph['role']['id'].encode()).hexdigest()[:16]+'.json'
            atlas.atomic(out/filename,atlas.dump(graph))
        # Merge roles only when updating a single role; untouched files stay intact.
        previous={}
        index=out/'index.json'
        if a.role and index.exists():previous={r['id']:r for r in json.loads(index.read_text()).get('roles',[])}
        for graph in graphs:
            role=graph['role'];filename='role-'+hashlib.sha256(role['id'].encode()).hexdigest()[:16]+'.json'
            previous[role['id']]={'id':role['id'],'name':role['name'],'description':role['description'],'file':filename,'functionCount':len(graph['functions']),'nodeCount':len(graph['nodes'])}
        atlas.atomic(index,atlas.dump({'schemaVersion':1,'project':root.name,'generatedAt':datetime.now(timezone.utc).isoformat(),'roles':sorted(previous.values(),key=lambda r:r['id'])}))
        print(atlas.dump({'output':str(out),'roles':len(graphs),'functions':sum(len(g['functions']) for g in graphs),'steps':sum(len(sc['steps']) for g in graphs for f in g['functions'] for sc in f['scenarios'])}));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        print(atlas.dump({'error':str(exc)}));return 2
if __name__=='__main__':raise SystemExit(main())
