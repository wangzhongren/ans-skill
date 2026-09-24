#!/usr/bin/env python3
"""Read-only, loopback dashboard for project role cards and coordination records."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading
from urllib.parse import urlparse, parse_qs

STATUSES = {'pending', 'ready', 'running', 'awaiting-verification', 'verified', 'failed', 'blocked', 'cancelled'}
MAX_BYTES = 2 * 1024 * 1024
DOC_NAMES = {'role-card.md', 'boundary.md', 'api-spec.md', 'functional-description.md', 'changelog.md'}
CONTEXT_CATEGORIES = ('flows', 'definitions', 'events', 'interfaces', 'data')


def utcnow():
    return datetime.now(timezone.utc).isoformat()


class Dashboard:
    def __init__(self, root, roles=None, scheduling=None):
        self.root = Path(root).resolve()
        self.roles = self.within(roles) if roles else next((self.root/n for n in ['角色卡', 'role-cards'] if (self.root/n).is_dir()), self.root/'角色卡')
        self.scheduling = [self.within(scheduling)] if scheduling else [self.root/'docs/scheduling', self.root/'doc/scheduling']
        self.lock = threading.Lock()

    def within(self, path):
        path = Path(path)
        resolved = (path if path.is_absolute() else self.root/path).resolve()
        if not resolved.is_relative_to(self.root):
            raise ValueError('Record directories must remain inside project root')
        return resolved

    def text(self, path):
        path = Path(path)
        if path.is_symlink() or not path.resolve().is_relative_to(self.root):
            raise ValueError('Symlink or outside-root file is not readable')
        with path.open('rb') as stream:
            raw = stream.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError('Record exceeds 2 MiB limit')
        return raw.decode('utf-8-sig')

    def relative(self, path):
        return path.relative_to(self.root).as_posix()

    def document(self, relative):
        source = Path(relative)
        if source.is_absolute() or '..' in source.parts:
            raise ValueError('Only project-relative role documentation is exposed')
        candidate = self.root/source
        while candidate != self.root:
            if candidate.is_symlink():
                raise ValueError('Symlinked role documentation is not readable')
            candidate = candidate.parent
        path = self.within(relative)
        if not path.is_relative_to(self.roles.resolve()):
            raise ValueError('Only role documentation is exposed')
        parts = path.relative_to(self.roles.resolve()).parts
        direct = len(parts) == 2 and parts[1] in DOC_NAMES
        overview = len(parts) == 3 and parts[1:] == ('project-context', 'README.md')
        topic = len(parts) == 4 and parts[1] == 'project-context' and parts[2] in CONTEXT_CATEGORIES and path.suffix == '.md'
        if not (direct or overview or topic):
            raise ValueError('Document must be an allowed file in a direct role folder')
        return self.text(path)

    def context_documents(self, folder):
        base = folder/'project-context'
        if base.is_symlink() or not base.is_dir():
            return []
        found = []
        overview = base/'README.md'
        if overview.is_file() and not overview.is_symlink():
            found.append({'category': 'overview', 'name': 'README.md', 'path': self.relative(overview)})
        for category in CONTEXT_CATEGORIES:
            directory = base/category
            if directory.is_symlink() or not directory.is_dir():
                continue
            for path in sorted(directory.iterdir()):
                if path.is_file() and not path.is_symlink() and path.suffix == '.md':
                    found.append({'category': category, 'name': path.name, 'path': self.relative(path)})
        return found

    def role_atlas(self, role_id=None):
        import role_atlas as graphs
        base=self.root/'doc/role-atlas'
        index=json.loads(self.text(base/'index.json'))
        if index.get('schemaVersion')!=1 or not isinstance(index.get('roles'),list):
            raise ValueError('Invalid role atlas index')
        if role_id is None:
            return index
        entry=next((row for row in index['roles'] if row.get('id')==role_id),None)
        if entry is None:raise ValueError('Unknown role atlas')
        name=entry.get('file','')
        if Path(name).name!=name or not name.startswith('role-') or not name.endswith('.json'):
            raise ValueError('Invalid role graph filename')
        graph=json.loads(self.text(base/name))
        if graph.get('schemaVersion')!=1 or graph.get('role',{}).get('id')!=role_id:
            raise ValueError('Role graph identity mismatch')
        hashes=graph.get('sourceHashes')
        if not isinstance(hashes,dict) or not hashes:raise ValueError('Role graph requires source hashes')
        changed=[]
        for path,digest in hashes.items():
            try:
                if graphs.hash_file(self.root,path)!=digest:changed.append(path)
            except (OSError,ValueError):changed.append(path)
        graph['freshness']={'current':not changed,'changed':changed}
        return graph

    def role_source(self, role_id, path, line):
        graph=self.role_atlas(role_id)
        allowed={n['path'] for n in graph['nodes']} | set(graph['role'].get('documents',[]))
        if path not in allowed:raise ValueError('File is not in this role graph')
        import role_atlas as graphs
        content=graphs.text(self.root,path).splitlines()
        if line<1 or line>max(1,len(content)):raise ValueError('Invalid source line')
        start=max(1,line-4);end=min(len(content),line+12)
        if path in graph['role'].get('documents',[]):start=1;end=len(content)
        return {'path':path,'line':line,'startLine':start,'text':'\n'.join(str(i)+': '+content[i-1] for i in range(start,end+1)), 'current':graph['freshness']['current']}

    def snapshot(self):
        with self.lock:
            return self._snapshot()

    def _snapshot(self):
        result = {'project': self.root.name, 'projectRootUri': self.root.as_uri(), 'sampledAt': utcnow(), 'refreshSeconds': 2,
                  'roles': [], 'tasks': [], 'events': [], 'issues': [], 'sources': [],
                  'limitations': ['实时刷新磁盘记录，不代表代理进程在线，也不自动验证任务完成。']}
        def issue(path, message):
            result['issues'].append({'path': self.relative(path), 'message': str(message)})
        def read_json(path):
            value = json.loads(self.text(path))
            if not isinstance(value, dict) or value.get('schemaVersion') != 1:
                raise ValueError('Expected an object with schemaVersion: 1')
            return value
        def node_map(value, key):
            if isinstance(value, dict):
                rows = [{**v, key: v.get(key, k)} for k, v in value.items() if isinstance(v, dict)]
                if len(rows) != len(value):
                    raise ValueError('Node map values must be objects')
            elif isinstance(value, list):
                rows = value
            else:
                raise ValueError('nodes must be an array or an object keyed by node ID')
            mapped = {}
            for row in rows:
                if not isinstance(row, dict):
                    raise ValueError('Node must be an object')
                node_id = row.get(key, row.get('id'))
                if not isinstance(node_id, str) or not node_id or node_id in mapped:
                    raise ValueError('Missing or duplicate node ID')
                mapped[node_id] = row
            return mapped
        try:
            if self.roles.is_dir() and self.roles.resolve().is_relative_to(self.root):
                for folder in sorted(self.roles.iterdir()):
                    if not folder.is_dir() or folder.is_symlink():
                        continue
                    card = folder/'role-card.md'
                    if not card.is_file():
                        continue
                    try:
                        content = self.text(card)
                        lines = [line.strip() for line in content.splitlines() if line.strip()]
                        title = next((line.lstrip('# ').strip() for line in lines if line.startswith('# ')), folder.name)
                        description = next((line for line in lines if not line.startswith(('#', '-', '|', '```'))), '')
                        docs = {name: self.relative(folder/name) for name in sorted(DOC_NAMES) if (folder/name).is_file() and not (folder/name).is_symlink()}
                        result['roles'].append({'id': folder.name, 'name': title, 'description': description,
                                                'path': self.relative(folder), 'documents': docs,
                                                'projectContext': self.context_documents(folder)})
                    except (OSError, UnicodeError, ValueError) as exc:
                        issue(card, exc)
        except OSError as exc:
            issue(self.roles, exc)
        role_ids = {role['id'] for role in result['roles']}
        seen_tasks = set()
        for base in self.scheduling:
            if not base.is_dir() or base.is_symlink() or not base.resolve().is_relative_to(self.root):
                continue
            for folder in sorted(base.iterdir()):
                if not folder.is_dir() or folder.is_symlink():
                    continue
                plan_path, state_path, log_path = folder/'plan.json', folder/'state.json', folder/'events.jsonl'
                if not any(p.exists() for p in [plan_path, state_path, log_path]):
                    continue
                start_issues = len(result['issues'])
                plan = state = None
                try:
                    plan = read_json(plan_path)
                    plans = node_map(plan.get('nodes'), 'nodeId')
                    task_id = plan.get('taskId')
                    if not isinstance(task_id, str) or not task_id or task_id in seen_tasks:
                        raise ValueError('Missing or duplicate taskId across task directories')
                    seen_tasks.add(task_id)
                except (OSError, UnicodeError, ValueError) as exc:
                    issue(plan_path, exc)
                    continue
                states = {}
                try:
                    state = read_json(state_path)
                    states = node_map(state.get('nodes'), 'nodeId')
                    if state.get('taskId') != task_id or state.get('planRevision') != plan.get('planRevision'):
                        raise ValueError('Task or plan revision mismatch')
                    for key in ['stateRevision', 'lastEventSeq']:
                        if type(state.get(key)) is not int or state[key] < 0:
                            raise ValueError(key+' must be a nonnegative integer')
                    for node in states:
                        if node not in plans:
                            issue(state_path, 'State node not found in plan: '+node)
                except (OSError, UnicodeError, ValueError) as exc:
                    issue(state_path, exc)
                events = []
                try:
                    text = self.text(log_path)
                    seqs, ids = [], set()
                    for number, line in enumerate(text.splitlines(), 1):
                        if not line.strip():
                            continue
                        event = json.loads(line)
                        if not isinstance(event, dict) or event.get('taskId') != task_id or type(event.get('seq')) is not int:
                            raise ValueError('Invalid event on line '+str(number))
                        event_id = event.get('eventId')
                        if not isinstance(event_id, str) or not event_id or event_id in ids:
                            raise ValueError('Missing or duplicate eventId')
                        if event.get('nodeId') is not None and event['nodeId'] not in plans:
                            raise ValueError('Unknown event nodeId')
                        if event['seq'] != (seqs[-1]+1 if seqs else 1):
                            raise ValueError('Event sequence must start at 1 and be contiguous')
                        seqs.append(event['seq']); ids.add(event_id)
                        events.append(event)
                    if state and state.get('lastEventSeq') != (seqs[-1] if seqs else 0):
                        issue(log_path, 'Event history and state.lastEventSeq disagree')
                except (OSError, UnicodeError, ValueError) as exc:
                    issue(log_path, exc)
                consistent = len(result['issues']) == start_issues
                rows = []
                for node_id, planned in plans.items():
                    reported = states.get(node_id, {})
                    status = reported.get('status', 'unreported')
                    role_id = planned.get('roleId')
                    good = consistent
                    if not isinstance(role_id, str) or role_id not in role_ids:
                        issue(plan_path, 'Unknown roleId for '+node_id); good = False
                    if reported.get('roleId', role_id) != role_id:
                        issue(state_path, 'Role mismatch for '+node_id); good = False
                    if not isinstance(status, str) or (status != 'unreported' and status not in STATUSES):
                        issue(state_path, 'Unknown status for '+node_id); good = False
                    if 'status' not in reported:
                        good = False
                    assigned = reported.get('assignedRevisions', {})
                    acknowledged = reported.get('acknowledgedRevisions', {})
                    if status in {'running', 'awaiting-verification', 'verified'} and isinstance(assigned, dict) and isinstance(acknowledged, dict) and assigned and acknowledged and assigned != acknowledged:
                        issue(state_path, 'Assigned and acknowledged revisions differ for '+node_id); good = False
                    deps = planned.get('dependsOn', [])
                    if not isinstance(deps, list):
                        issue(plan_path, 'dependsOn must be an array'); deps = []; good = False
                    if any((d if isinstance(d, str) else d.get('nodeId') if isinstance(d, dict) else None) not in plans for d in deps):
                        issue(plan_path, 'Unknown prerequisite for '+node_id); good = False
                    rows.append({'key': task_id+'/'+node_id, 'taskId': task_id, 'nodeId': node_id,
                                 'title': planned.get('title') or planned.get('objective') or node_id,
                                 'stage': planned.get('stage', ''), 'roleId': role_id,
                                 'reportedStatus': status, 'status': status if good else 'unreported' if not reported else 'inconsistent',
                                 'reason': reported.get('reason', ''), 'attemptId': reported.get('attemptId'),
                                 'assignedRevisions': reported.get('assignedRevisions', {}),
                                 'acknowledgedRevisions': reported.get('acknowledgedRevisions', {}),
                                 'latestReport': reported.get('latestReport', {}), 'nextAction': reported.get('nextAction', {}),
                                 'updatedAt': reported.get('updatedAt') or (state or {}).get('updatedAt'),
                                 'stateRevision': (state or {}).get('stateRevision'), 'lastEventSeq': (state or {}).get('lastEventSeq'),
                                 'dependsOn': deps, 'source': self.relative(folder)})
                consistent = len(result['issues']) == start_issues
                if not consistent:
                    for row in rows:
                        if row['status'] != 'unreported':
                            row['status'] = 'inconsistent'
                result['tasks'].extend(rows)
                for event in events[-100:]:
                    result['events'].append({'taskId': task_id, 'nodeId': event.get('nodeId'), 'seq': event['seq'],
                                             'kind': event.get('kind', event.get('type', 'event')), 'summary': event.get('summary', ''),
                                             'roleId': event.get('roleId', event.get('reportingRole', '')),
                                             'at': event.get('receivedAt') or event.get('reportedAt') or '', 'consistent': consistent})
                result['sources'].append({'taskId': task_id, 'path': self.relative(folder), 'consistent': consistent,
                                           'planRevision': plan.get('planRevision'), 'stateRevision': (state or {}).get('stateRevision')})
        result['events'].sort(key=lambda e: (str(e['at']), e['taskId'], e['seq']), reverse=True)
        result['events'] = result['events'][:100]
        return result


def make_handler(dashboard):
    asset = Path(__file__).resolve().parents[1]/'assets/role-dashboard/index.html'
    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data, mime='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            ancestor="'self'" if urlparse(self.path).path=='/role-atlas' else "'none'"
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; frame-ancestors "+ancestor+"; base-uri 'none'")
            self.end_headers(); self.wfile.write(data)
        def do_GET(self):
            allowed = {'127.0.0.1:'+str(self.server.server_port), 'localhost:'+str(self.server.server_port)}
            if self.headers.get('Host') not in allowed:
                self.respond(403, b'{"error":"loopback host required"}'); return
            parsed = urlparse(self.path)
            try:
                if parsed.path == '/':
                    self.respond(200, asset.read_bytes(), 'text/html; charset=utf-8')
                elif parsed.path == '/role-atlas':
                    page=Path(__file__).resolve().parents[1]/'assets/role-atlas/index.html'
                    self.respond(200,page.read_bytes(),'text/html; charset=utf-8')
                elif parsed.path == '/api/role-atlas':
                    role=parse_qs(parsed.query).get('role',[None])[0]
                    self.respond(200,json.dumps(dashboard.role_atlas(role),ensure_ascii=False).encode())
                elif parsed.path == '/api/role-source':
                    query=parse_qs(parsed.query)
                    content=dashboard.role_source(query.get('role',[''])[0],query.get('file',[''])[0],int(query.get('line',['1'])[0]))
                    self.respond(200,json.dumps(content,ensure_ascii=False).encode())
                elif parsed.path == '/api/snapshot':
                    self.respond(200, json.dumps(dashboard.snapshot(), ensure_ascii=False).encode())
                elif parsed.path == '/api/document':
                    path = parse_qs(parsed.query).get('path', [''])[0]
                    self.respond(200, json.dumps({'path': path, 'text': dashboard.document(path)}, ensure_ascii=False).encode())
                else:
                    self.respond(404, b'{"error":"not found"}')
            except (OSError, UnicodeError, ValueError, TypeError) as exc:
                self.respond(400, json.dumps({'error': str(exc)}, ensure_ascii=False).encode())
        def do_POST(self):
            self.respond(405, b'{"error":"read-only dashboard"}')
        do_PUT = do_PATCH = do_DELETE = do_POST
        def log_message(self, *_):
            pass
    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True, help='Project root, not its src/ directory')
    parser.add_argument('--roles', help='Role directory inside project; autodetects 角色卡 or role-cards')
    parser.add_argument('--scheduling', help='Scheduling directory inside project; default docs/scheduling and doc/scheduling')
    parser.add_argument('--port', type=int, default=8765, help='Loopback port; 0 chooses a free port')
    args = parser.parse_args(argv)
    if not args.root.is_dir():
        parser.error('Project root does not exist')
    try:
        dashboard = Dashboard(args.root, args.roles, args.scheduling)
        server = ThreadingHTTPServer(('127.0.0.1', args.port), make_handler(dashboard))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({'url': 'http://127.0.0.1:'+str(server.server_port), 'project': dashboard.root.name, 'projectRootUri': dashboard.root.as_uri(), 'mode': 'read-only'}), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
