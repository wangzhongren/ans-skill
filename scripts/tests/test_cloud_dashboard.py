import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.cloud_store import CloudStore
from dashboard.server import ThreadingHTTPServer, make_handler
from dashboard.sync import projection


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

    def test_membership_and_last_admin(self):
        self.store.add_project('alpha', 'Alpha')
        self.store.create_user('reader', PASSWORD)
        user = self.store.authenticate('reader', PASSWORD)
        self.assertFalse(self.store.can_view(user, 'alpha'))
        self.store.grant('reader', 'alpha')
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
        self.assertEqual(self.request('/api/admin/projects', 'POST', {'id': 'gamma', 'title': 'Gamma'}, cookie=cookie)[0], 403)
        self.assertEqual(self.request('/api/admin/projects', 'POST', {'id': 'gamma', 'title': 'Gamma'}, cookie=cookie, csrf=me['csrfToken'])[0], 200)
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

    def test_viewer_sees_only_granted_project(self):
        self.store.create_user('reader', PASSWORD)
        self.store.grant('reader', 'alpha')
        cookie = self.login('reader')
        self.assertEqual([item['id'] for item in self.request('/api/projects', cookie=cookie)[1]['projects']], ['alpha'])
        self.assertEqual(self.request('/p/alpha/api/snapshot', cookie=cookie)[0], 200)
        self.assertEqual(self.request('/p/beta/api/snapshot', cookie=cookie)[0], 403)
        self.assertEqual(self.request('/api/admin/users', cookie=cookie)[0], 403)


if __name__ == '__main__':
    unittest.main()
