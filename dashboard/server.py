#!/usr/bin/env python3
"""Local read-only or authenticated shared Dashboard for project snapshots."""
import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from http.cookies import SimpleCookie
import hmac
import json
from pathlib import Path
import re
import sqlite3
import threading
from urllib.parse import urlparse, parse_qs
from .cloud_store import CloudStore, MAX_PROJECTION_BYTES
from .context_store import ContextStore

STATUSES = {'pending', 'ready', 'running', 'awaiting-verification', 'verified', 'failed', 'blocked', 'cancelled'}
MAX_BYTES = 2 * 1024 * 1024
DOC_NAMES = {'role-card.md', 'boundary.md', 'api-spec.md', 'functional-description.md', 'changelog.md'}
HOST_NAME = re.compile(r'^[A-Za-z0-9.-]+(?::[0-9]{1,5})?$')
PROJECT_PATH = re.compile(r'^/p/([a-z0-9]+(?:-[a-z0-9]+)*)/(.*)$')


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
        if not direct:
            raise ValueError('Document must be an allowed file in a direct role folder')
        return self.text(path)

    def context_outline(self, role_id):
        try:
            return ContextStore(self.root, role_id, self.roles).outline()
        except ValueError as exc:
            if str(exc) == 'This role has no project overview':
                return None
            raise

    def context_topic(self, role_id, topic_id):
        return ContextStore(self.root, role_id, self.roles).get_topic(topic_id)

    def context_category(self, role_id, category):
        store = ContextStore(self.root, role_id, self.roles)
        try:
            summary = store.get_category(category)
        except ValueError as exc:
            if str(exc) != 'Category summary not found for this role':
                raise
            summary = None
        topics = [store.get_topic(row['topic_id']) for row in store.list_topics(category)]
        return {'roleId': role_id, 'category': category, 'summary': summary, 'topics': topics}

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
                        role_meta = ContextStore(self.root, folder.name, self.roles).role_metadata()
                        context = None
                        db_path = self.root/'project-context/context.sqlite3'
                        if db_path.exists():
                            try:
                                context = self.context_outline(folder.name)
                                if context and context.get('flowsWithoutTriggers'):
                                    issue(db_path, 'Flows without a trigger for '+folder.name+': '+', '.join(context['flowsWithoutTriggers']))
                            except (OSError, ValueError, sqlite3.Error) as exc:
                                issue(db_path, exc)
                        result['roles'].append({'id': folder.name, 'name': title, 'description': description,
                                                'path': self.relative(folder), 'documents': docs,
                                                'boundaryPaths': role_meta['boundaryPaths'], 'projectContext': context})
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


def make_handler(dashboard=None, cloud_store=None, trusted_hosts=(), insecure_local=False):
    if (dashboard is None) == (cloud_store is None):
        raise ValueError('Choose one local Dashboard or one cloud store')
    for host in trusted_hosts:
        if not HOST_NAME.fullmatch(host):
            raise ValueError('Trusted Host must be a hostname with optional port')
    static = {'/static/dashboard.css': ('style.css', 'text/css; charset=utf-8'),
              '/static/dashboard.js': ('app.js', 'text/javascript; charset=utf-8'),
              '/static/auth.css': ('auth.css', 'text/css; charset=utf-8'),
              '/static/login.js': ('login.js', 'text/javascript; charset=utf-8'),
              '/static/manage.js': ('manage.js', 'text/javascript; charset=utf-8')}
    assets = Path(__file__).resolve().parent
    trusted = set(trusted_hosts)
    cookie_name = 'anssid' if insecure_local else '__Host-anssid'

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status, data, mime='application/json; charset=utf-8', headers=()):
            self.send_response(status)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            legacy_atlas = cloud_store is None and urlparse(self.path).path == '/role-atlas'
            ancestor = "'self'" if legacy_atlas else "'none'"
            inline = " 'unsafe-inline'" if legacy_atlas else ''
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'" + inline + "; style-src 'self'" + inline + "; img-src 'self' data:; connect-src 'self'; frame-ancestors " + ancestor + "; base-uri 'none'; form-action 'self'")
            for name, value in headers:
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(data)

        def json_response(self, status, value, headers=()):
            self.respond(status, json.dumps(value, ensure_ascii=False).encode('utf-8'), headers=headers)

        def redirect(self, path):
            self.send_response(303)
            self.send_header('Location', path)
            self.send_header('Content-Length', '0')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()

        def host_allowed(self):
            allowed = {'127.0.0.1:' + str(self.server.server_port),
                       'localhost:' + str(self.server.server_port)} | trusted
            return self.headers.get('Host') in allowed

        def session_token(self):
            cookies = SimpleCookie()
            try:
                cookies.load(self.headers.get('Cookie', ''))
            except Exception:
                return None
            item = cookies.get(cookie_name)
            return item.value if item is not None else None

        def session_user(self):
            token = self.session_token()
            return cloud_store.session(token) if cloud_store is not None and token else None

        def bearer_token(self):
            value = self.headers.get('Authorization', '')
            return value[7:].strip() if value.startswith('Bearer ') else None

        def project_allowed(self, project_id):
            user = self.session_user()
            if user is not None and cloud_store.can_view(user, project_id):
                return True
            token = self.bearer_token()
            return bool(token and cloud_store.key_allows(project_id, token))

        def require_admin(self):
            user = self.session_user()
            if user is None or user['role'] != 'admin':
                self.json_response(403, {'error': 'Administrator access required'})
                return None
            return user

        def require_csrf(self, user):
            supplied = self.headers.get('X-CSRF-Token', '')
            if not supplied or not hmac.compare_digest(supplied, user['csrf_token']):
                self.json_response(403, {'error': 'CSRF token required'})
                return False
            return True

        def request_json(self, limit=65536):
            if self.headers.get('Content-Type', '').split(';', 1)[0].strip() != 'application/json':
                raise ValueError('Content-Type must be application/json')
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > limit:
                raise ValueError('Invalid or oversized JSON body')
            value = json.loads(self.rfile.read(length))
            if not isinstance(value, dict):
                raise ValueError('JSON body must be an object')
            return value

        def local_get(self, parsed):
            if parsed.path == '/':
                self.respond(200, (assets/'index.html').read_bytes(), 'text/html; charset=utf-8')
            elif parsed.path == '/role-atlas':
                page = assets.parent/'assets/role-atlas/index.html'
                self.respond(200, page.read_bytes(), 'text/html; charset=utf-8')
            elif parsed.path == '/api/role-atlas':
                role = parse_qs(parsed.query).get('role', [None])[0]
                self.json_response(200, dashboard.role_atlas(role))
            elif parsed.path == '/api/role-source':
                query = parse_qs(parsed.query)
                content = dashboard.role_source(query.get('role', [''])[0], query.get('file', [''])[0],
                                                int(query.get('line', ['1'])[0]))
                self.json_response(200, content)
            elif parsed.path == '/api/snapshot':
                self.json_response(200, dashboard.snapshot())
            elif parsed.path == '/api/document':
                path = parse_qs(parsed.query).get('path', [''])[0]
                self.json_response(200, {'path': path, 'text': dashboard.document(path)})
            elif parsed.path == '/api/context':
                query = parse_qs(parsed.query)
                role = query.get('role', [''])[0]
                topic, category = query.get('topic', [None])[0], query.get('category', [None])[0]
                if topic and category:
                    raise ValueError('Choose topic or category, not both')
                if topic:
                    content = dashboard.context_topic(role, topic)
                elif category:
                    content = dashboard.context_category(role, category)
                else:
                    content = dashboard.context_outline(role)
                if content is None:
                    raise ValueError('This role has no project overview')
                self.json_response(200, content)
            else:
                self.json_response(404, {'error': 'not found'})

        def cloud_get(self, parsed):
            path = parsed.path
            if path == '/login':
                self.respond(200, (assets/'login.html').read_bytes(), 'text/html; charset=utf-8')
                return
            if path == '/api/me':
                user = self.session_user()
                if user is None:
                    self.json_response(401, {'error': 'Login required'})
                else:
                    self.json_response(200, {'username': user['username'], 'role': user['role'],
                                             'csrfToken': user['csrf_token']})
                return
            if path == '/api/projects':
                user = self.session_user()
                if user is None:
                    self.json_response(401, {'error': 'Login required'})
                else:
                    self.json_response(200, {'projects': cloud_store.projects_for(user)})
                return
            if path == '/manage' or path.startswith('/api/admin/'):
                user = self.require_admin()
                if user is None:
                    return
                if path == '/manage':
                    self.respond(200, (assets/'manage.html').read_bytes(), 'text/html; charset=utf-8')
                elif path == '/api/admin/users':
                    self.json_response(200, {'users': cloud_store.users()})
                elif path == '/api/admin/projects':
                    self.json_response(200, {'projects': cloud_store.projects_for(user)})
                elif path == '/api/admin/keys':
                    self.json_response(200, {'keys': cloud_store.keys()})
                else:
                    self.json_response(404, {'error': 'not found'})
                return
            if path == '/':
                user = self.session_user()
                if user is None:
                    self.redirect('/login')
                else:
                    projects = cloud_store.projects_for(user)
                    self.redirect(projects[0]['url'] if projects else '/manage' if user['role'] == 'admin' else '/login')
                return
            if re.fullmatch(r'/p/[a-z0-9]+(?:-[a-z0-9]+)*', path):
                self.redirect(path + '/')
                return
            match = PROJECT_PATH.fullmatch(path)
            if match is None:
                self.json_response(404, {'error': 'not found'})
                return
            project_id, subpath = match.group(1), '/' + match.group(2)
            if subpath == '/':
                user = self.session_user()
                if user is None:
                    self.redirect('/login?next=/p/' + project_id + '/')
                elif not cloud_store.can_view(user, project_id):
                    self.json_response(403, {'error': 'Project access denied'})
                else:
                    self.respond(200, (assets/'index.html').read_bytes(), 'text/html; charset=utf-8')
                return
            if not self.project_allowed(project_id):
                self.json_response(403, {'error': 'Project access denied'})
                return
            value = cloud_store.projection(project_id)
            if subpath == '/api/snapshot':
                self.json_response(200, value['snapshot'])
            elif subpath == '/api/context':
                query = parse_qs(parsed.query)
                role_id = query.get('role', [''])[0]
                entry = value['contexts'].get(role_id)
                if entry is None:
                    self.json_response(404, {'error': 'Role context not found'})
                    return
                topic, category = query.get('topic', [None])[0], query.get('category', [None])[0]
                if topic and category:
                    raise ValueError('Choose topic or category, not both')
                if topic:
                    result = entry['topics'].get(topic)
                    if result is None:
                        self.json_response(404, {'error': 'Topic not found'})
                        return
                elif category:
                    topics = [item for item in entry['topics'].values() if item.get('category') == category]
                    result = {'roleId': role_id, 'category': category,
                              'summary': entry['outline'].get('categorySummaries', {}).get(category),
                              'topics': topics}
                else:
                    result = entry['outline']
                self.json_response(200, result)
            else:
                self.json_response(404, {'error': 'not found'})

        def do_GET(self):
            if not self.host_allowed():
                self.json_response(403, {'error': 'Host not allowed'})
                return
            parsed = urlparse(self.path)
            if parsed.path in static:
                file_name, mime = static[parsed.path]
                self.respond(200, (assets/file_name).read_bytes(), mime)
                return
            try:
                if cloud_store is None:
                    self.local_get(parsed)
                else:
                    self.cloud_get(parsed)
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                self.json_response(400, {'error': str(exc)})
            except sqlite3.IntegrityError:
                self.json_response(409, {'error': 'Record already exists'})
            except (OSError, sqlite3.Error):
                self.json_response(500, {'error': 'Dashboard storage error'})

        def cloud_post(self, parsed):
            path = parsed.path
            if path == '/api/login':
                value = self.request_json()
                user = cloud_store.authenticate(value.get('username'), value.get('password'))
                if user is None:
                    self.json_response(401, {'error': 'Invalid credentials'})
                    return
                token, _ = cloud_store.create_session(user['id'])
                flags = '; Path=/; HttpOnly; SameSite=Strict' + ('' if insecure_local else '; Secure')
                self.json_response(200, {'username': user['username'], 'role': user['role']},
                                   headers=[('Set-Cookie', cookie_name + '=' + token + flags)])
                return
            if path == '/api/logout':
                user = self.session_user()
                if user is None or not self.require_csrf(user):
                    return
                cloud_store.revoke_session(self.session_token())
                flags = '; Max-Age=0; Path=/; HttpOnly; SameSite=Strict' + ('' if insecure_local else '; Secure')
                self.json_response(200, {'loggedOut': True}, headers=[('Set-Cookie', cookie_name + '=' + flags)])
                return
            match = PROJECT_PATH.fullmatch(path)
            if match is not None and match.group(2) == 'api/sync':
                project_id = match.group(1)
                token = self.bearer_token()
                if not token or not cloud_store.key_allows(project_id, token):
                    self.json_response(403, {'error': 'Project Key required'})
                    return
                result = cloud_store.ingest(project_id, self.request_json(MAX_PROJECTION_BYTES))
                self.json_response(200, result)
                return
            if not path.startswith('/api/admin/'):
                self.json_response(404, {'error': 'not found'})
                return
            user = self.require_admin()
            if user is None or not self.require_csrf(user):
                return
            value = self.request_json()
            if path == '/api/admin/users':
                result = cloud_store.create_user(value.get('username'), value.get('password'), value.get('role', 'viewer'))
            elif path == '/api/admin/projects':
                result = cloud_store.add_project(value.get('id'), value.get('title'))
            elif path == '/api/admin/grants':
                result = cloud_store.grant(value.get('username'), value.get('projectId'))
            elif path == '/api/admin/keys':
                result = cloud_store.create_key(value.get('projectId'), value.get('label'))
            elif path == '/api/admin/keys/revoke':
                result = cloud_store.revoke_key(value.get('id'))
            elif path == '/api/admin/users/disable':
                if value.get('username') == user['username']:
                    raise ValueError('Cannot disable the current administrator')
                result = cloud_store.disable_user(value.get('username'))
            else:
                self.json_response(404, {'error': 'not found'})
                return
            self.json_response(200, result)

        def do_POST(self):
            if not self.host_allowed():
                self.json_response(403, {'error': 'Host not allowed'})
                return
            if cloud_store is None:
                self.json_response(405, {'error': 'read-only dashboard'})
                return
            try:
                self.cloud_post(urlparse(self.path))
            except (ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
                self.json_response(400, {'error': str(exc)})
            except sqlite3.IntegrityError:
                self.json_response(409, {'error': 'Record already exists'})
            except (OSError, sqlite3.Error):
                self.json_response(500, {'error': 'Dashboard storage error'})

        def do_PUT(self):
            self.json_response(405, {'error': 'Method not allowed'})
        do_PATCH = do_DELETE = do_PUT

        def log_message(self, *_):
            pass

    return Handler


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--root', type=Path, help='One local project root')
    source.add_argument('--cloud-state', type=Path, help='Cloud Dashboard user/project state directory')
    parser.add_argument('--roles', help='Local role directory override')
    parser.add_argument('--scheduling', help='Local scheduling directory override')
    parser.add_argument('--trusted-host', action='append', default=[], help='Proxy Host header to accept')
    parser.add_argument('--insecure-local-preview', action='store_true', help='Allow session cookies over loopback HTTP for testing')
    parser.add_argument('--listen-host', choices=('127.0.0.1', '0.0.0.0'), default='127.0.0.1',
                        help='Bind address; 0.0.0.0 is for cloud mode inside a container')
    parser.add_argument('--port', type=int, default=8765, help='Listening port; 0 chooses a free port')
    args = parser.parse_args(argv)
    try:
        if args.root is not None:
            if not args.root.is_dir():
                parser.error('Project root does not exist')
            if args.insecure_local_preview:
                parser.error('--insecure-local-preview is for cloud mode only')
            if args.listen_host != '127.0.0.1':
                parser.error('Local project mode only listens on 127.0.0.1')
            dashboard = Dashboard(args.root, args.roles, args.scheduling)
            handler = make_handler(dashboard=dashboard, trusted_hosts=args.trusted_host)
            mode = 'local-read-only'
        else:
            if args.roles or args.scheduling:
                parser.error('--roles and --scheduling are only for one local project')
            if args.listen_host == '0.0.0.0' and not args.trusted_host:
                parser.error('--trusted-host is required when listening on 0.0.0.0')
            if args.listen_host == '0.0.0.0' and args.insecure_local_preview:
                parser.error('--insecure-local-preview requires loopback listening')
            store = CloudStore(args.cloud_state)
            if not store.has_users():
                parser.error('Create the initial admin with: python3 -m dashboard.admin --state-dir ... --username ...')
            handler = make_handler(cloud_store=store, trusted_hosts=args.trusted_host,
                                   insecure_local=args.insecure_local_preview)
            mode = 'cloud-projection'
        server = ThreadingHTTPServer((args.listen_host, args.port), handler)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    result = {'url': 'http://127.0.0.1:' + str(server.server_port),
              'listenHost': args.listen_host, 'mode': mode}
    if args.root is not None:
        result['project'] = dashboard.root.name
        result['projectRootUri'] = dashboard.root.as_uri()
    print(json.dumps(result, ensure_ascii=False), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
