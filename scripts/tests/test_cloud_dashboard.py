import json
from contextlib import closing, redirect_stderr, redirect_stdout
import io
from pathlib import Path
import sys
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.cloud_store import CloudStore, digest, password_digest
from dashboard.paths import normalize_base_path
from dashboard.server import ThreadingHTTPServer, main, make_handler
from dashboard.sync import projection, send


PASSWORD = 'correct-horse-battery-staple-2026'


def sample(project_id, role_id):
    return {'schemaVersion': 1,
            'snapshot': {'projectId': project_id, 'project': project_id,
                         'projectRootUri': 'file:///private/source',
                         'roles': [{'id': role_id, 'name': role_id, 'description': 'Owns '+role_id,
                                    'boundaryPaths': ['src/'+role_id],
                                    'documents': {'boundary.md': 'secret-file.md'},
                                    'projectContext': None}],
                         'tasks': [], 'events': [], 'issues': [], 'sampledAt': '2026-09-24T00:00:00Z'},
            'contexts': {}}


class CloudStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = CloudStore(self.tmp.name)
        self.store.create_user('owner', PASSWORD, 'admin', bootstrap=True)

    def test_project_key_scope_and_projection_redaction(self):
        self.store.add_project('alpha', 'Alpha')
        self.store.add_project('beta', 'Beta')
        alpha = self.store.create_key('alpha', 'laptop')
        self.assertTrue(self.store.key_allows('alpha', alpha['key']))
        self.assertFalse(self.store.key_allows('beta', alpha['key']))
        self.store.ingest('alpha', sample('alpha', 'orders'))
        value = self.store.projection('alpha')['snapshot']
        self.assertNotIn('projectRootUri', value)
        self.assertEqual(value['roles'][0]['documents'], {})
        self.assertEqual(value['roles'][0]['boundaryPaths'], ['src/orders'])
        self.assertEqual(self.store.projection('beta')['snapshot']['roles'], [])
        self.store.revoke_key(alpha['id'])
        self.assertFalse(self.store.key_allows('alpha', alpha['key']))
        with self.assertRaisesRegex(ValueError, 'Project not found'):
            self.store.ingest('ghost', sample('ghost', 'unknown'))
        self.assertFalse((Path(self.tmp.name)/'projects/ghost.sqlite3').exists())

    def test_each_project_owns_a_separate_sqlite_file(self):
        self.store.add_project('alpha', 'Alpha')
        self.store.add_project('beta', 'Beta')
        alpha_value = sample('alpha', 'orders')
        alpha_value['contexts'] = {'orders': {'outline': {'title': 'Order flow'}, 'topics': {}}}
        self.store.ingest('alpha', alpha_value)
        self.store.ingest('beta', sample('beta', 'billing'))
        alpha = Path(self.tmp.name)/'projects/alpha.sqlite3'
        beta = Path(self.tmp.name)/'projects/beta.sqlite3'
        self.assertTrue(alpha.is_file() and beta.is_file())
        with closing(sqlite3.connect(alpha)) as connection:
            stored = json.loads(connection.execute('SELECT snapshot_json FROM projection').fetchone()[0])
            self.assertEqual(stored['roles'][0]['id'], 'orders')
        with closing(sqlite3.connect(beta)) as connection:
            stored = json.loads(connection.execute('SELECT snapshot_json FROM projection').fetchone()[0])
            self.assertEqual(stored['roles'][0]['id'], 'billing')
        with closing(sqlite3.connect(self.store.db)) as connection:
            columns = {row[1] for row in connection.execute('PRAGMA table_info(projects)')}
            self.assertNotIn('snapshot_json', columns)
        reopened = CloudStore(self.tmp.name)
        self.assertEqual(reopened.projection('alpha')['snapshot']['roles'][0]['id'], 'orders')
        self.assertEqual(reopened.projection('alpha')['contexts']['orders']['outline']['title'], 'Order flow')
        self.assertEqual(reopened.projection('beta')['snapshot']['roles'][0]['id'], 'billing')
        self.assertEqual(reopened.projection('beta')['contexts'], {})

    def test_legacy_shared_snapshots_migrate_without_loss(self):
        with tempfile.TemporaryDirectory() as root:
            old_db = Path(root)/'dashboard.sqlite3'
            with closing(sqlite3.connect(old_db)) as connection:
                connection.execute('''CREATE TABLE projects (
                    id TEXT PRIMARY KEY,title TEXT NOT NULL,snapshot_json TEXT,
                    contexts_json TEXT,received_at TEXT,created_at TEXT NOT NULL)''')
                connection.execute('''CREATE TABLE users (
                    id INTEGER PRIMARY KEY,username TEXT NOT NULL UNIQUE,salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL,role TEXT NOT NULL,active INTEGER NOT NULL,
                    failures INTEGER NOT NULL,locked_until REAL NOT NULL,created_at TEXT NOT NULL)''')
                connection.execute('''CREATE TABLE project_keys (
                    id INTEGER PRIMARY KEY,project_id TEXT NOT NULL,label TEXT NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,revoked_at TEXT)''')
                connection.execute('INSERT INTO projects VALUES (?,?,?,?,?,?)',
                                   ('alpha', 'Old Alpha', json.dumps(sample('alpha', 'orders')['snapshot']),
                                    '{}', '2026-09-24T00:00:00Z', '2026-09-24T00:00:00Z'))
                salt = b'legacy-test-salt'
                connection.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)',
                                   (1, 'legacy-admin', salt, password_digest(PASSWORD, salt),
                                    'admin', 1, 0, 0, '2026-09-24T00:00:00Z'))
                connection.execute('INSERT INTO project_keys VALUES (?,?,?,?,?,?)',
                                   (1, 'alpha', 'old collector', digest('ansp_legacy_test'),
                                    '2026-09-24T00:00:00Z', None))
                connection.commit()
            store = CloudStore(root)
            self.assertEqual(store.projection('alpha')['snapshot']['roles'][0]['id'], 'orders')
            self.assertEqual(store.authenticate('legacy-admin', PASSWORD)['role'], 'admin')
            self.assertTrue(store.key_allows('alpha', 'ansp_legacy_test'))
            self.assertTrue((Path(root)/'projects/alpha.sqlite3').is_file())
            with closing(sqlite3.connect(old_db)) as connection:
                record = connection.execute('''SELECT snapshot_json,contexts_json,received_at,last_received_at
                    FROM projects WHERE id='alpha' ''').fetchone()
                self.assertEqual(record, (None, None, None, '2026-09-24T00:00:00Z'))
            self.assertEqual(CloudStore(root).projection('alpha')['snapshot']['roles'][0]['id'], 'orders')

    def test_viewers_see_all_projects_and_last_admin_is_protected(self):
        self.store.add_project('alpha', 'Alpha')
        self.store.create_user('reader', PASSWORD)
        user = self.store.authenticate('reader', PASSWORD)
        self.assertTrue(self.store.can_view(user, 'alpha'))
        with self.assertRaisesRegex(ValueError, 'last active administrator'):
            self.store.disable_user('owner')
        self.store.disable_user('reader')
        self.assertIsNone(self.store.authenticate('reader', PASSWORD))

    def test_sync_reads_metadata_without_uploading_role_document(self):
        root = Path(self.tmp.name)/'project'
        role = root/'角色卡'/'orders'
        role.mkdir(parents=True)
        (role/'role-card.md').write_text('# Orders\nOwns exports.\n', encoding='utf-8')
        (role/'boundary.md').write_text('PRIVATE DOCUMENT BODY\n- `src/orders`\n', encoding='utf-8')
        value = projection(root, 'alpha')
        serialized = json.dumps(value)
        self.assertEqual(value['snapshot']['roles'][0]['id'], 'orders')
        self.assertNotIn('PRIVATE DOCUMENT BODY', serialized)
        self.assertNotIn(str(root), serialized)


class CloudHTTPTests(unittest.TestCase):
    def setUp(self):
        CloudStoreTests.setUp(self)
        self.store.add_project('alpha', 'Alpha')
        self.store.add_project('beta', 'Beta')
        self.alpha_key = self.store.create_key('alpha', 'test')['key']
        self.store.ingest('alpha', sample('alpha', 'orders'))
        self.store.ingest('beta', sample('beta', 'billing'))
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(cloud_store=self.store, insecure_local=True))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.addCleanup(lambda: self.thread.join(timeout=2))
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)

    def request(self, path, method='GET', value=None, cookie=None, csrf=None, key=None):
        headers = {}
        if cookie:
            headers['Cookie'] = cookie
        if csrf:
            headers['X-CSRF-Token'] = csrf
        if key:
            headers['Authorization'] = 'Bearer '+key
        body = None
        if value is not None:
            body = json.dumps(value).encode()
            headers['Content-Type'] = 'application/json'
        request = Request(self.base+path, data=body, headers=headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                data = response.read()
                return response.status, json.loads(data) if response.headers['Content-Type'].startswith('application/json') else data.decode(), response.headers
        except HTTPError as error:
            with error:
                return error.code, json.load(error), error.headers

    def login(self, username='owner', password=PASSWORD):
        status, _, headers = self.request('/api/login', 'POST', {'username': username, 'password': password})
        self.assertEqual(status, 200)
        return headers['Set-Cookie'].split(';', 1)[0]

    def test_auth_admin_and_project_isolation(self):
        self.assertEqual(self.request('/api/projects')[0], 401)
        self.assertEqual(self.request('/p/alpha/api/snapshot')[0], 403)
        cookie = self.login()
        status, me, _ = self.request('/api/me', cookie=cookie)
        self.assertEqual(status, 200)
        self.assertEqual(me['role'], 'admin')
        self.assertEqual(self.request('/api/admin/projects', cookie=cookie)[0], 200)
        manage = self.request('/manage', cookie=cookie)
        self.assertEqual(manage[0], 200)
        self.assertIn('href="/static/manage.css"', manage[1])
        self.assertNotIn('grantForm', manage[1])
        self.assertNotIn('roleTokenForm', manage[1])
        self.assertEqual(self.request('/static/manage.css')[0], 200)
        self.assertEqual(self.request('/api/admin/projects', 'POST', {'id': 'gamma', 'title': 'Gamma'}, cookie=cookie)[0], 403)
        self.assertEqual(self.request('/api/admin/projects', 'POST', {'id': 'gamma', 'title': 'Gamma'}, cookie=cookie, csrf=me['csrfToken'])[0], 200)
        status, created, _ = self.request('/api/admin/users', 'POST',
                                          {'username': 'new-reader', 'password': PASSWORD}, cookie=cookie,
                                          csrf=me['csrfToken'])
        self.assertEqual((status, created['role']), (200, 'viewer'))
        self.assertEqual(self.request('/api/admin/grants', 'POST',
                                      {'username': 'new-reader', 'projectId': 'gamma'},
                                      cookie=cookie, csrf=me['csrfToken'])[0], 404)
        status, issued, _ = self.request('/api/admin/keys', 'POST',
                                         {'projectId': 'gamma', 'label': 'collector'},
                                         cookie=cookie, csrf=me['csrfToken'])
        self.assertEqual(status, 200)
        self.assertTrue(issued['key'].startswith('ansp_'))
        self.assertNotIn('key', self.request('/api/admin/keys', cookie=cookie)[1]['keys'][0])
        self.assertEqual(self.request('/api/admin/keys/revoke', 'POST', {'id': issued['id']},
                                      cookie=cookie, csrf=me['csrfToken'])[0], 200)
        self.assertFalse(self.store.key_allows('gamma', issued['key']))
        self.assertEqual(self.request('/api/login', 'POST', [1, 2])[0], 400)
        self.assertEqual(self.request('/p/alpha/api/snapshot', key=self.alpha_key)[1]['roles'][0]['id'], 'orders')
        self.assertEqual(self.request('/p/beta/api/snapshot', key=self.alpha_key)[0], 403)
        self.assertEqual(self.request('/p/alpha/api/snapshot', cookie=cookie)[1]['roles'][0]['id'], 'orders')
        self.assertEqual(self.request('/p/beta/api/snapshot', cookie=cookie)[1]['roles'][0]['id'], 'billing')
        self.assertIn('src="/static/dashboard.js"', self.request('/p/alpha/', cookie=cookie)[1])
        self.assertEqual(self.request('/api/logout', 'POST', {}, cookie=cookie, csrf=me['csrfToken'])[0], 200)
        self.assertEqual(self.request('/api/me', cookie=cookie)[0], 401)

    def test_key_sync_requires_matching_project(self):
        self.assertEqual(self.request('/p/beta/api/sync', 'POST', sample('beta', 'foreign'), key=self.alpha_key)[0], 403)
        self.assertEqual(self.request('/p/alpha/api/sync', 'POST', sample('beta', 'wrong'), key=self.alpha_key)[0], 400)
        self.assertEqual(self.request('/p/alpha/api/sync', 'POST', sample('alpha', 'new'), key=self.alpha_key)[0], 200)
        self.assertEqual(self.request('/p/alpha/api/snapshot', key=self.alpha_key)[1]['roles'][0]['id'], 'new')

    def test_viewer_sees_all_projects_without_grants(self):
        self.store.create_user('reader', PASSWORD)
        cookie = self.login('reader')
        self.assertEqual([item['id'] for item in self.request('/api/projects', cookie=cookie)[1]['projects']], ['alpha','beta'])
        self.assertEqual(self.request('/p/alpha/api/snapshot', cookie=cookie)[0], 200)
        self.assertEqual(self.request('/p/beta/api/snapshot', cookie=cookie)[0], 200)
        self.assertEqual(self.request('/api/admin/users', cookie=cookie)[0], 403)


class SubpathHTTPTests(unittest.TestCase):
    def setUp(self):
        CloudStoreTests.setUp(self)
        self.store.add_project('alpha', 'Alpha')
        self.key = self.store.create_key('alpha', 'collector')['key']
        self.prefix = '/tools/dashboard'
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
            cloud_store=self.store, insecure_local=True, base_path=self.prefix))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(lambda: (self.server.shutdown(), self.server.server_close(), self.thread.join(timeout=2)))
        self.origin = 'http://127.0.0.1:' + str(self.server.server_port)

    def test_all_routes_and_sync_stay_under_base_path(self):
        self.assertEqual(normalize_base_path('/tools/dashboard/'), self.prefix)
        with self.assertRaises(ValueError):
            normalize_base_path('/tools/../dashboard')
        for outside in ['/login', '/api/projects', '/p/alpha/api/snapshot']:
            with self.assertRaises(HTTPError) as caught:
                urlopen(self.origin+outside, timeout=5)
            self.assertEqual(caught.exception.code, 404)
            caught.exception.close()
        with urlopen(self.origin+self.prefix+'/login', timeout=5) as response:
            page = response.read().decode()
            self.assertIn('src="'+self.prefix+'/static/login.js"', page)
            self.assertIn('content="'+self.prefix+'"', page)
        with urlopen(self.origin+self.prefix, timeout=5) as response:
            self.assertEqual(response.geturl(), self.origin+self.prefix+'/login')
        with urlopen(self.origin+self.prefix+'/static/login.js', timeout=5) as response:
            self.assertIn('basePath', response.read().decode())
        login = Request(self.origin+self.prefix+'/api/login',
                        data=json.dumps({'username': 'owner', 'password': PASSWORD}).encode(),
                        headers={'Content-Type': 'application/json'}, method='POST')
        with urlopen(login, timeout=5) as response:
            cookie = response.headers['Set-Cookie'].split(';', 1)[0]
        with urlopen(Request(self.origin+self.prefix+'/api/projects', headers={'Cookie': cookie}), timeout=5) as response:
            self.assertEqual(json.load(response)['projects'][0]['url'], self.prefix+'/p/alpha/')
        with urlopen(Request(self.origin+self.prefix+'/api/me', headers={'Cookie': cookie}), timeout=5) as response:
            csrf = json.load(response)['csrfToken']
        create = Request(self.origin+self.prefix+'/api/admin/projects',
                         data=json.dumps({'id': 'beta', 'title': 'Beta'}).encode(),
                         headers={'Cookie': cookie, 'X-CSRF-Token': csrf,
                                  'Content-Type': 'application/json'}, method='POST')
        with urlopen(create, timeout=5) as response:
            self.assertEqual(json.load(response)['url'], self.prefix+'/p/beta/')
        with urlopen(Request(self.origin+self.prefix+'/p/alpha/', headers={'Cookie': cookie}), timeout=5) as response:
            page = response.read().decode()
            self.assertIn('src="'+self.prefix+'/static/dashboard.js"', page)
            self.assertIn('href="'+self.prefix+'/manage"', page)
        with urlopen(Request(self.origin+self.prefix+'/manage', headers={'Cookie': cookie}), timeout=5) as response:
            self.assertIn('href="'+self.prefix+'/"', response.read().decode())
        send(self.origin+self.prefix+'/', 'alpha', self.key, sample('alpha', 'orders'))
        with urlopen(Request(self.origin+self.prefix+'/p/alpha/api/snapshot',
                             headers={'Authorization': 'Bearer '+self.key}), timeout=5) as response:
            self.assertEqual(json.load(response)['roles'][0]['id'], 'orders')


class ContainerBindingTests(unittest.TestCase):
    def test_container_bind_requires_cloud_mode_and_trusted_host(self):
        with tempfile.TemporaryDirectory() as root:
            store = CloudStore(root)
            store.create_user('owner', PASSWORD, 'admin', bootstrap=True)
            quiet = io.StringIO()
            with redirect_stderr(quiet), self.assertRaises(SystemExit):
                main(['--root', root, '--listen-host', '0.0.0.0'])
            with redirect_stderr(quiet), self.assertRaises(SystemExit):
                main(['--cloud-state', root, '--listen-host', '0.0.0.0'])
            with redirect_stderr(quiet), self.assertRaises(SystemExit):
                main(['--cloud-state', root, '--listen-host', '0.0.0.0',
                      '--trusted-host', 'dashboard.example.com', '--insecure-local-preview'])
            fake_server = MagicMock()
            fake_server.server_port = 8765
            with patch('dashboard.server.ThreadingHTTPServer', return_value=fake_server) as create, redirect_stdout(quiet):
                main(['--cloud-state', root, '--listen-host', '0.0.0.0',
                      '--trusted-host', 'dashboard.example.com', '--port', '8765'])
            self.assertEqual(create.call_args.args[0], ('0.0.0.0', 8765))


if __name__ == '__main__':
    unittest.main()
