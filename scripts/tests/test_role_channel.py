import json
from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.channel_cli import call, main as channel_main
from dashboard.channel_store import ChannelStore
from dashboard.cloud_store import CloudStore
from dashboard.server import ThreadingHTTPServer, make_handler

PASSWORD = 'correct-horse-battery-staple-2026'


def projection(design='D1'):
    return {'schemaVersion': 1, 'snapshot': {'projectId': 'alpha', 'project': 'Alpha',
        'roles': [{'id': role, 'name': role, 'description': role, 'documents': {},
                   'boundaryPaths': [], 'projectContext': None} for role in ('orders', 'reviewer', 'assembly')],
        'tasks': [{'taskId': 'task-1', 'nodeId': 'node-1', 'roleId': 'orders',
                   'operation': 'implement', 'writeSet': ['src/orders.py'], 'attemptNumber': 0,
                   'assignedRevisions': {'requirement': 'R1', 'design': design, 'boundary': 'B1'}}],
        'sources': [{'taskId': 'task-1', 'planRevision': 1}],
        'events': [], 'issues': [], 'sampledAt': '2026-09-25T00:00:00Z'}, 'contexts': {}}


def permission(client_id='request-1'):
    return {'clientRequestId': client_id, 'taskId': 'task-1', 'nodeId': 'node-1',
            'workerId': 'worker-1', 'operation': 'implement', 'writeSet': ['src/orders.py'],
            'planRevision': 1, 'attemptNumber': 1,
            'requirementRevision': 'R1', 'designRevision': 'D1',
            'boundaryRevision': 'B1', 'reason': 'Need the approved write scope'}


class RoleChannelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = CloudStore(self.temp.name)
        self.store.create_user('admin', PASSWORD, 'admin', bootstrap=True)
        self.store.add_project('alpha', 'Alpha')
        self.channel = ChannelStore(self.store)

    def ready(self):
        self.store.ingest('alpha', projection())
        return self.store.create_role_token('alpha', 'orders', 'agent')['token']

    def test_role_credentials_and_project_scope(self):
        with self.assertRaisesRegex(ValueError, 'Sync this role'):
            self.store.create_role_token('alpha', 'orders', 'agent')
        token = self.ready()
        self.assertEqual(self.store.role_principal('alpha', token)['roleId'], 'orders')
        self.assertIsNone(self.store.role_principal('beta', token))
        self.assertNotIn('token', self.store.role_tokens()[0])
        self.store.revoke_role_token(self.store.role_tokens()[0]['id'])
        self.assertIsNone(self.store.role_principal('alpha', token))

    def test_messages_requests_decisions_and_audit(self):
        self.ready()
        actor = {'kind': 'role', 'id': 'orders'}
        message = {'clientMessageId': 'message-1', 'toRoleId': 'reviewer', 'taskId': 'task-1',
                   'kind': 'issue', 'body': 'Interface changed', 'revision': 'D1'}
        first = self.channel.send_message('alpha', actor, message)
        self.assertFalse(first['duplicate'])
        self.assertTrue(self.channel.send_message('alpha', actor, message)['duplicate'])
        with self.assertRaisesRegex(ValueError, 'reused'):
            self.channel.send_message('alpha', actor, {**message, 'body': 'Different'})
        self.assertEqual(len(self.channel.view('alpha', 'reviewer')['messages']), 1)
        self.assertEqual(self.channel.view('alpha', 'assembly')['messages'], [])
        request = self.channel.request_permission('alpha', 'orders', permission())
        self.assertTrue(self.channel.request_permission('alpha', 'orders', permission())['duplicate'])
        result = self.channel.decide('alpha', request['id'], 'admin',
                                     {'decision': 'approved', 'reason': 'Scope and version reviewed'})
        self.assertFalse(result['executionAuthorized'])
        self.assertIsNotNone(result['expiresAt'])
        with self.assertRaisesRegex(ValueError, 'already decided'):
            self.channel.decide('alpha', request['id'], 'admin', {'decision': 'denied', 'reason': 'Changed mind'})
        view = self.channel.view('alpha')
        self.assertEqual(view['requests'][0]['status'], 'approved')
        self.assertEqual([event['seq'] for event in view['events']], [3, 2, 1])
        self.assertEqual(self.channel.view('alpha', 'reviewer')['requests'], [])
        self.assertEqual(self.channel.view('alpha', 'orders')['requests'][0]['status'], 'approved')

    def test_old_revision_cannot_be_approved(self):
        self.ready()
        request = self.channel.request_permission('alpha', 'orders', permission())
        self.store.ingest('alpha', projection('D2'))
        self.assertEqual(self.channel.view('alpha')['requests'][0]['status'], 'stale')
        with self.assertRaisesRegex(ValueError, 'version changed'):
            self.channel.decide('alpha', request['id'], 'admin',
                                {'decision': 'approved', 'reason': 'Old approval'})
        self.assertEqual(self.channel.decide('alpha', request['id'], 'admin',
                         {'decision': 'denied', 'reason': 'Design changed'})['decision'], 'denied')
        with self.assertRaisesRegex(ValueError, 'version changed'):
            self.channel.request_permission('alpha', 'orders', permission('request-2'))

    def test_request_scope_and_attempt_must_match_snapshot(self):
        self.ready()
        with self.assertRaisesRegex(ValueError, 'project-relative'):
            self.channel.request_permission('alpha', 'orders',
                {**permission('traversal'), 'writeSet': ['../secret']})
        with self.assertRaisesRegex(ValueError, 'version changed'):
            self.channel.request_permission('alpha', 'orders',
                {**permission('wrong-file'), 'writeSet': ['src/other.py']})
        with self.assertRaisesRegex(ValueError, 'version changed'):
            self.channel.request_permission('alpha', 'orders',
                {**permission('wrong-attempt'), 'attemptNumber': 2})
        request = self.channel.request_permission('alpha', 'orders', permission())
        changed = projection()
        changed['snapshot']['tasks'][0]['attemptNumber'] = 1
        self.store.ingest('alpha', changed)
        with self.assertRaisesRegex(ValueError, 'version changed'):
            self.channel.decide('alpha', request['id'], 'admin',
                {'decision': 'approved', 'reason': 'Too late'})


class RoleChannelHTTPTests(unittest.TestCase):
    def setUp(self):
        RoleChannelTests.setUp(self)
        self.store.ingest('alpha', projection())
        self.role_token = self.store.create_role_token('alpha', 'orders', 'agent')['token']
        self.project_key = self.store.create_key('alpha', 'sync')['key']
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
            cloud_store=self.store, insecure_local=True, base_path='/ans-dashboard'))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(lambda: (self.server.shutdown(), self.server.server_close(), self.thread.join(timeout=2)))
        self.base = 'http://127.0.0.1:'+str(self.server.server_port)+'/ans-dashboard'

    def request(self, path, method='GET', payload=None, cookie=None, token=None, csrf=None):
        headers = {}
        if cookie: headers['Cookie'] = cookie
        if token: headers['Authorization'] = 'Bearer '+token
        if csrf: headers['X-CSRF-Token'] = csrf
        data = None if payload is None else json.dumps(payload).encode()
        if data is not None: headers['Content-Type'] = 'application/json'
        req = Request(self.base+path, data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.load(response), response.headers
        except HTTPError as error:
            with error:
                return error.code, json.load(error), error.headers

    def test_agent_and_admin_permissions(self):
        channel_path = '/p/alpha/api/channel'
        self.assertEqual(self.request(channel_path, token=self.project_key)[0], 403)
        self.assertEqual(self.request(channel_path, token=self.role_token)[0], 200)
        message = {'clientMessageId': 'http-message', 'toRoleId': 'reviewer',
                   'taskId': 'task-1', 'kind': 'question', 'body': 'Please review', 'revision': 'D1'}
        self.assertEqual(self.request('/p/alpha/api/messages', 'POST', message, token=self.project_key)[0], 403)
        self.assertEqual(self.request('/p/alpha/api/messages', 'POST', message, token=self.role_token)[0], 200)
        self.assertEqual(call(self.base, 'alpha', self.role_token, 'channel')['messages'][0]['body'], 'Please review')
        requested = self.request('/p/alpha/api/permission-requests', 'POST', permission(), token=self.role_token)[1]
        login = self.request('/api/login', 'POST', {'username': 'admin', 'password': PASSWORD})
        cookie = login[2]['Set-Cookie'].split(';', 1)[0]
        me = self.request('/api/me', cookie=cookie)[1]
        url = '/p/alpha/api/permission-requests/'+str(requested['id'])+'/decision'
        choice = {'decision': 'approved', 'reason': 'Reviewed exact task'}
        self.assertEqual(self.request(url, 'POST', choice, token=self.role_token)[0], 403)
        self.assertEqual(self.request(url, 'POST', choice, cookie=cookie)[0], 403)
        self.assertEqual(self.request(url, 'POST', choice, cookie=cookie, csrf=me['csrfToken'])[0], 200)
        self.assertFalse(self.request(channel_path, cookie=cookie)[1]['requests'][0]['executionAuthorized'])

    def test_role_cli_send_request_and_list(self):
        with tempfile.TemporaryDirectory() as folder:
            message_file = Path(folder)/'message.json'
            message_file.write_text(json.dumps({'clientMessageId': 'cli-message',
                'toRoleId': 'reviewer', 'taskId': 'task-1', 'kind': 'handoff',
                'body': 'Ready for review', 'revision': 'D1'}), encoding='utf-8')
            request_file = Path(folder)/'permission.json'
            request_file.write_text(json.dumps(permission('cli-request')), encoding='utf-8')
            prefix = ['--server-url', self.base, '--project-id', 'alpha']
            with patch.dict(os.environ, {'ANS_ROLE_TOKEN': self.role_token}), redirect_stdout(io.StringIO()) as output:
                self.assertEqual(channel_main(prefix+['send', '--input', str(message_file)]), 0)
                self.assertEqual(channel_main(prefix+['request', '--input', str(request_file)]), 0)
                self.assertEqual(channel_main(prefix+['list']), 0)
            self.assertIn('Ready for review', output.getvalue())
            self.assertNotIn(self.role_token, output.getvalue())


if __name__ == '__main__':
    unittest.main()
