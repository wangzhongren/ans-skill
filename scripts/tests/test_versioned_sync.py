import json
import io
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.cloud_store import CloudStore
from dashboard.channel_store import ChannelStore
from dashboard.server import ThreadingHTTPServer, make_handler
from dashboard.versioned_sync import LocalReplica, ProjectReplica, capture, fingerprint, synchronize
from dashboard.versioned_sync import main as sync_main
from dashboard.local_config import save_project_config
from dashboard.write_queue import WriteQueue, WriteQueueBusy
from dashboard.sync_runtime import sync_status


def sample(project='alpha', role='orders'):
    return {'schemaVersion': 1, 'snapshot': {'projectId': project, 'project': project,
        'projectRootUri': 'file:///private/source', 'roles': [{'id': role, 'name': role,
        'documents': {'role-card.md': 'private'}}], 'tasks': [], 'events': [], 'issues': []},
        'contexts': {}, 'artifacts': {'docs/design/example.md': '# design'}}


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cloud = CloudStore(self.temp.name)
        self.cloud.add_project('alpha', 'Alpha')
        self.replica = ProjectReplica(self.cloud)

    def test_versions_conflicts_and_existing_snapshot(self):
        self.cloud.ingest('alpha', sample())
        first = self.replica.changes('alpha')
        self.assertEqual(first['headVersion'], 1)
        self.assertEqual(first['changes'][0]['changeId'], 'legacy-initial')
        newer = sample(role='billing')
        result = self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 1,
            'changeId': 'laptop-1', 'data': newer})
        self.assertEqual(result['revision'], 2)
        self.assertEqual(self.replica.publish('alpha', {'schemaVersion': 2,
            'baseRevision': 1, 'changeId': 'laptop-1', 'data': newer})['revision'], 2)
        self.assertEqual(self.replica.changes('alpha', 1)['changes'][0]['revision'], 2)
        history = self.replica.design_history('alpha', 'docs/design/example.md')
        self.assertEqual([item['revision'] for item in history['versions']], [2])
        self.assertEqual(self.replica.design_history('alpha', 'docs/design/example.md', 2)['content'], '# design')
        self.assertNotIn('projectRootUri', self.replica.changes('alpha', 1)['changes'][0]['data']['snapshot'])
        self.assertEqual(self.cloud.projection('alpha')['snapshot']['roles'][0]['documents'], {})
        conflict = self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 1,
            'changeId': 'other-1', 'data': sample(role='different')})
        self.assertTrue(conflict['conflict'])
        self.assertEqual(conflict['headVersion'], 2)
        self.assertEqual(len(self.replica.conflicts('alpha')), 1)
        detail = self.replica.conflict_detail('alpha', self.replica.conflicts('alpha')[0]['id'])
        self.assertTrue(any(item['item'] == 'role:different' for item in detail['differences']))
        self.assertEqual(self.cloud.projection('alpha')['snapshot']['roles'][0]['id'], 'billing')
        self.replica.report_conflict('alpha', {'changeId': 'offline-1', 'baseRevision': 1,
            'headRevision': 2, 'data': sample(role='offline')})
        reported = next(item for item in self.replica.conflicts('alpha') if item['changeId'] == 'offline-1')
        self.assertTrue(self.replica.conflict_detail('alpha', reported['id'])['candidateAvailable'])
        self.assertTrue(self.replica.resolve_conflict('alpha', {'changeId': 'other-1', 'choice': 'cloud'})['resolved'])
        self.assertEqual([item['changeId'] for item in self.replica.conflicts('alpha')], ['offline-1'])
        with self.assertRaisesRegex(ValueError, 'Legacy overwrite is disabled'):
            self.cloud.ingest('alpha', sample())

    def test_new_project_and_pagination(self):
        self.assertEqual(self.replica.changes('alpha')['headVersion'], 0)
        for number in range(3):
            result = self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': number,
                'changeId': 'change-'+str(number), 'data': sample(role='r'+str(number))})
            self.assertEqual(result['revision'], number+1)
        page = self.replica.changes('alpha', 0, 2)
        self.assertEqual([item['revision'] for item in page['changes']], [1, 2])
        self.assertTrue(page['hasMore'])
        self.assertEqual(self.replica.changes('alpha', page['nextVersion'])['changes'][0]['revision'], 3)

    def test_rejects_unsafe_artifact_without_mutating_project(self):
        bad = sample()
        bad['artifacts'] = {'../outside.md': '# wrong'}
        with self.assertRaisesRegex(ValueError, 'Invalid governance artifact'):
            self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 0,
                'changeId': 'unsafe', 'data': bad})
        self.assertEqual(self.replica.changes('alpha')['headVersion'], 0)

    def test_document_history_reads_nested_paths_and_changed_versions(self):
        path = 'kefuAgent/src/platform/docs/dev_docs/方案.md'
        bug_path = 'kefuAgent/src/platform/docs/bug_docs/方案.md'
        first = sample()
        first['artifacts'].update({path: '# First', bug_path: '# Bug', 'docs/design/raw.json': '{}'})
        self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 0,
                            'changeId': 'first', 'data': first})
        second = json.loads(json.dumps(first))
        second['artifacts'][path] = '# Second'
        self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 1,
                            'changeId': 'second', 'data': second})
        history = self.replica.document_history('alpha', path)
        self.assertEqual([item['revision'] for item in history['versions']], [1, 2])
        self.assertEqual(self.replica.document_history('alpha', path, 1)['content'], '# First')
        self.assertEqual(self.replica.document_history('alpha', path, 2)['content'], '# Second')
        self.assertEqual(len(self.replica.document_history('alpha', bug_path)['versions']), 1)
        listed = self.replica.document_history('alpha')['documents']
        self.assertEqual({item['path'] for item in listed}, {path, bug_path, 'docs/design/example.md'})
        self.assertEqual([item['path'] for item in self.replica.design_history('alpha')['documents']],
                         ['docs/design/example.md'])
        with self.assertRaisesRegex(ValueError, '云端没有这份文档'):
            self.replica.document_history('alpha', 'not-uploaded.md')
        with self.assertRaises(ValueError):
            self.replica.document_history('alpha', '../outside.md')

    def test_document_history_does_not_truncate_at_200(self):
        value = sample()
        value['artifacts'] = {'custom/'+str(number)+'.md': '# document' for number in range(228)}
        self.replica.publish('alpha', {'schemaVersion': 2, 'baseRevision': 0,
                            'changeId': 'many-documents', 'data': value})
        self.assertEqual(len(self.replica.document_history('alpha')['documents']), 228)

    def test_channel_cursor_reads_past_recent_100(self):
        channel = ChannelStore(self.cloud)
        with channel.connection('alpha') as db:
            for number in range(105):
                row = db.execute('''INSERT INTO channel_messages
                    (sender_kind,sender_id,to_role_id,task_id,kind,body,revision,client_id,payload_hash,created_at)
                    VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    ('role', 'orders', 'project', 'task-1', 'question', str(number), 'D1',
                     'message-'+str(number), 'hash', '2026-09-26T00:00:00Z'))
                db.execute('''INSERT INTO channel_events
                    (kind,actor_kind,actor_id,record_id,at,summary) VALUES (?,?,?,?,?,?)''',
                    ('message', 'role', 'orders', row.lastrowid, '2026-09-26T00:00:00Z', 'sent'))
        first = channel.changes('alpha', 0, 50)
        second = channel.changes('alpha', first['nextSequence'], 50)
        third = channel.changes('alpha', second['nextSequence'], 50)
        self.assertEqual([len(x['changes']) for x in (first, second, third)], [50, 50, 5])
        self.assertEqual(third['changes'][-1]['record']['body'], '104')


class LocalTests(unittest.TestCase):
    def test_cli_defaults_to_one_manual_cycle(self):
        with tempfile.TemporaryDirectory() as root:
            save_project_config('alpha', root, 'https://example.com', 'ansp_test-key')
            actions = []
            def transport(_url, _project, _key, action, body=None):
                actions.append(action)
                if action.startswith('channel/changes?'):
                    return {'headSequence': 0, 'changes': [], 'hasMore': False}
                if action.startswith('changes?'):
                    return {'headVersion': 0, 'changes': [], 'hasMore': False}
                return {'revision': 1, 'hash': fingerprint(body['data'])}
            with patch('dashboard.versioned_sync.capture', return_value=sample()), \
                 patch('dashboard.versioned_sync.request', side_effect=transport), \
                 patch('dashboard.versioned_sync.time.sleep', side_effect=AssertionError('must not sleep')), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(sync_main(['--root', root]), 0)
            self.assertEqual(actions[-1], 'sync-v2')

    def test_pull_only_never_uploads(self):
        with tempfile.TemporaryDirectory() as root:
            save_project_config('alpha', root, 'https://example.com', 'ansp_test-key')
            actions = []
            def transport(_url, _project, _key, action, _body=None):
                actions.append(action)
                return ({'headSequence': 0, 'changes': [], 'hasMore': False}
                        if action.startswith('channel/') else
                        {'headVersion': 0, 'changes': [], 'hasMore': False})
            with patch('dashboard.versioned_sync.capture', return_value=sample()), \
                 patch('dashboard.versioned_sync.request', side_effect=transport), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(sync_main(['--root', root, '--pull-only']), 0)
            self.assertTrue(actions)
            self.assertTrue(all(action.endswith('limit=20') or action.endswith('limit=50') for action in actions))
            self.assertEqual(LocalReplica(root, 'alpha').state()['pending'], 1)

    def test_changes_are_journaled_and_remote_conflict_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            local = LocalReplica(root, 'alpha')
            initial = sample()
            self.assertTrue(local.observe(initial))
            self.assertFalse(local.observe(initial))
            pending = local.pending()
            local.ack(pending, {'revision': 1, 'hash': pending['hash']})
            self.assertEqual(local.state()['pending'], 0)
            self.assertEqual(local.latest_cloud()['revision'], 1)
            remote = sample(role='remote')
            local.pull({'changes': [{'revision': 2, 'changeId': 'remote',
                'hash': fingerprint(remote), 'data': remote}]})
            self.assertEqual(local.latest_cloud()['data']['snapshot']['roles'][0]['id'], 'remote')
            self.assertTrue(local.observe(sample(role='local-later')))
            self.assertIsNone(local.pending())
            self.assertEqual(local.state()['conflicts'], 1)
            self.assertEqual(len(local.unreported()), 1)
            local.mark_reported(local.unreported()[0]['id'])
            self.assertEqual(local.unreported(), [])
            self.assertEqual(LocalReplica(root, 'alpha').state()['serverVersion'], 2)
            status = sync_status(root)
            self.assertEqual(status['syncMode'], 'versioned')
            self.assertEqual(status['serverVersion'], 2)
            self.assertEqual(status['conflicts'], 1)
            self.assertNotIn('projectKey', json.dumps(status))

    def test_customer_can_rebase_local_after_conflict(self):
        with tempfile.TemporaryDirectory() as root:
            local = LocalReplica(root, 'alpha')
            original = sample()
            local.observe(original)
            first = local.pending()
            local.ack(first, {'revision': 1, 'hash': first['hash']})
            remote = sample(role='remote')
            local.pull({'changes': [{'revision': 2, 'changeId': 'remote',
                'hash': fingerprint(remote), 'data': remote}]})
            local.observe(sample(role='local'))
            change_id = local.unreported()[0]['changeId']
            local.resolve(change_id, 'local')
            self.assertEqual(local.state()['conflicts'], 0)
            self.assertEqual(local.pending()['changeId'], change_id)

    def test_capture_is_stable_and_contains_governance_docs(self):
        with tempfile.TemporaryDirectory() as root:
            folder = Path(root)/'docs/design'
            folder.mkdir(parents=True)
            (folder/'2026-09-26_design_example.md').write_text('# design\n', encoding='utf-8')
            a, b = capture(root, 'alpha'), capture(root, 'alpha')
            self.assertEqual(fingerprint(a), fingerprint(b))
            self.assertEqual(a['artifacts']['docs/design/2026-09-26_design_example.md'], '# design\n')
            self.assertNotIn('sampledAt', a['snapshot'])

    def test_capture_uses_configured_roots_and_keeps_distinct_paths(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root)
            base = 'kefuAgent/src/platform/docs'
            dev, bug = source/base/'dev_docs', source/base/'bug_docs'
            dev.mkdir(parents=True)
            bug.mkdir()
            (dev/'same.md').write_text('# Design', encoding='utf-8')
            (bug/'same.md').write_text('# Fix', encoding='utf-8')
            (dev/'source.py').write_text('print("not uploaded")', encoding='utf-8')
            (dev/'key.txt').write_text('ansp_private-key', encoding='utf-8')
            (source/'unselected').mkdir()
            (source/'unselected/other.md').write_text('# not selected', encoding='utf-8')
            default = source/'docs/design'
            default.mkdir(parents=True)
            (default/'current.md').write_text('# Default', encoding='utf-8')
            save_project_config('alpha', source, 'https://example.com', 'ansp_test-key',
                                document_roots=[base, base+'/dev_docs', 'docs'])
            value = capture(source, 'alpha')
            self.assertEqual(value['artifacts'], {base+'/dev_docs/same.md': '# Design',
                base+'/bug_docs/same.md': '# Fix', 'docs/design/current.md': '# Default'})
            self.assertEqual(fingerprint(value), fingerprint(capture(source, 'alpha')))
            self.assertNotIn('ansp_', json.dumps(value))

    def test_capture_rejects_missing_directories_and_skips_symlinked_files(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            source = Path(root)
            docs = source/'custom'
            docs.mkdir()
            (Path(outside)/'private.md').write_text('# outside', encoding='utf-8')
            (docs/'linked.md').symlink_to(Path(outside)/'private.md')
            (source/'linked').symlink_to(outside, target_is_directory=True)
            self.assertEqual(capture(source, 'alpha', ['custom'])['artifacts'], {})
            for directory in ('missing', 'linked', '../outside'):
                with self.subTest(directory=directory), self.assertRaises(ValueError):
                    capture(source, 'alpha', [directory])

    def test_capture_enforces_document_count_and_size_limits(self):
        with tempfile.TemporaryDirectory() as root:
            docs = Path(root)/'custom'
            docs.mkdir()
            for number in range(300):
                (docs/(str(number)+'.md')).write_text('# document', encoding='utf-8')
            self.assertEqual(len(capture(root, 'alpha', ['custom', 'custom'])['artifacts']), 300)
            (docs/'extra.md').write_text('# extra', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'count exceeds 300'):
                capture(root, 'alpha', ['custom'])
        with tempfile.TemporaryDirectory() as root:
            docs = Path(root)/'custom'
            docs.mkdir()
            oversized = docs/'large.md'
            oversized.write_text('x'*(256*1024+1), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'exceeds 256 KiB.*large.md'):
                capture(root, 'alpha', ['custom'])
            oversized.unlink()
            for number in range(17):
                (docs/(str(number)+'.md')).write_text('x'*(256*1024), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'exceed 4 MiB'):
                capture(root, 'alpha', ['custom'])

    def test_each_recorded_document_change_has_local_sqlite_history(self):
        with tempfile.TemporaryDirectory() as root:
            local = LocalReplica(root, 'alpha')
            first = sample()
            local.observe(first)
            second = sample()
            second['artifacts']['docs/design/example.md'] = '# revised design'
            local.observe(second)
            history = local.entity_history('artifact:docs/design/example.md')
            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]['after'], '# design')
            self.assertEqual(history[1]['after'], '# revised design')
            self.assertEqual(history[0]['afterHash'], history[1]['beforeHash'])

    def test_periodic_cycle_pulls_then_pushes_once(self):
        with tempfile.TemporaryDirectory() as root:
            local = LocalReplica(root, 'alpha')
            value = sample()
            actions = []
            def transport(_url, _project, _key, action, body=None):
                actions.append(action)
                if action.startswith('channel/changes?'):
                    return {'headSequence': 0, 'changes': [], 'hasMore': False}
                if action.startswith('changes?'):
                    return {'headVersion': 0 if len(actions) == 1 else 1,
                            'changes': [], 'hasMore': False}
                return {'revision': 1, 'hash': fingerprint(body['data'])}
            with patch('dashboard.versioned_sync.capture', return_value=value), \
                 patch('dashboard.versioned_sync.request', side_effect=transport):
                self.assertEqual(synchronize(root, 'alpha', 'https://example.com', 'ansp_test', local)['sent'], 1)
                self.assertEqual(synchronize(root, 'alpha', 'https://example.com', 'ansp_test', local)['sent'], 0)
            self.assertEqual(actions, ['changes?after=0&limit=20', 'channel/changes?after=0&limit=50',
                                       'sync-v2', 'changes?after=1&limit=20', 'channel/changes?after=0&limit=50'])


class HTTPTests(unittest.TestCase):
    def test_nested_documents_sync_and_history_cli_under_base_path(self):
        with tempfile.TemporaryDirectory() as state, tempfile.TemporaryDirectory() as project:
            store = CloudStore(state)
            key = store.create_key('alpha', 'local')['key']
            other_key = store.create_key('beta', 'other')['key']
            prefix = '/ans-dashboard'
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(
                cloud_store=store, insecure_local=True, base_path=prefix))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                source = Path(project)
                paths = ['kefuAgent/src/platform/docs/dev_docs/方案.md',
                         'kefuAgent/src/platform/docs/bug_docs/问题.md']
                for path in paths:
                    document = source/path
                    document.parent.mkdir(parents=True, exist_ok=True)
                    document.write_text('# First', encoding='utf-8')
                url = 'http://127.0.0.1:'+str(server.server_port)+prefix
                save_project_config('alpha', source, url, key,
                    document_roots=['kefuAgent/src/platform/docs/dev_docs',
                                    'kefuAgent/src/platform/docs/bug_docs'])
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(sync_main(['--root', project]), 0)
                (source/paths[0]).write_text('# Second', encoding='utf-8')
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(sync_main(['--root', project]), 0)

                def query(*arguments):
                    output = io.StringIO()
                    with redirect_stdout(output):
                        self.assertEqual(sync_main(['--root', project, *arguments]), 0)
                    return json.loads(output.getvalue())

                listed = query('--document-list')['documents']
                self.assertEqual({item['path'] for item in listed}, set(paths))
                history = query('--document-path', paths[0])['versions']
                self.assertEqual([item['revision'] for item in history], [1, 2])
                self.assertEqual(query('--document-path', paths[0], '--document-revision', '1')['content'], '# First')
                self.assertEqual(query('--document-path', paths[0], '--document-revision', '2')['content'], '# Second')
                self.assertEqual(query('--design-list')['documents'], [])
                errors = io.StringIO()
                with redirect_stderr(errors):
                    self.assertEqual(sync_main(['--root', project, '--document-path', 'missing.md']), 2)
                self.assertIn('云端没有这份文档', errors.getvalue())
                with self.assertRaises(HTTPError) as caught:
                    urlopen(Request(url+'/p/alpha/api/document-history',
                                    headers={'Authorization': 'Bearer '+other_key}), timeout=5)
                self.assertEqual(caught.exception.code, 403)
                caught.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_manual_cli_end_to_end_and_no_upload_on_record_or_pull(self):
        with tempfile.TemporaryDirectory() as state, tempfile.TemporaryDirectory() as project:
            store = CloudStore(state)
            key = store.create_key('alpha', 'local')['key']
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(cloud_store=store, insecure_local=True))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                source = Path(project)
                folder = source/'docs/design'
                folder.mkdir(parents=True)
                document = folder/'2026-09-26_design_example.md'
                document.write_text('# First\n', encoding='utf-8')
                save_project_config('alpha', source, 'http://127.0.0.1:'+str(server.server_port), key)
                quiet = io.StringIO()
                with redirect_stdout(quiet):
                    self.assertEqual(sync_main(['--root', project]), 0)
                self.assertEqual(ProjectReplica(store).changes('alpha')['headVersion'], 1)
                document.write_text('# Second\n', encoding='utf-8')
                with redirect_stdout(quiet):
                    self.assertEqual(sync_main(['--root', project, '--record']), 0)
                    self.assertEqual(sync_main(['--root', project, '--pull-only']), 0)
                self.assertEqual(ProjectReplica(store).changes('alpha')['headVersion'], 1)
                with redirect_stdout(quiet):
                    self.assertEqual(sync_main(['--root', project]), 0)
                history = ProjectReplica(store).design_history('alpha',
                    'docs/design/2026-09-26_design_example.md')['versions']
                self.assertEqual(len(history), 2)
                self.assertEqual(LocalReplica(project, 'alpha').state()['serverVersion'], 2)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)

    def test_authenticated_sync_and_customer_conflict_notice(self):
        with tempfile.TemporaryDirectory() as root:
            store = CloudStore(root)
            key = store.create_key('alpha', 'local')['key']
            server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(cloud_store=store, insecure_local=True))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                base = 'http://127.0.0.1:'+str(server.server_port)+'/p/alpha/api/'
                def post(action, body):
                    return Request(base+action, data=json.dumps(body).encode(), method='POST',
                        headers={'Authorization': 'Bearer '+key, 'Content-Type': 'application/json'})
                with urlopen(post('sync-v2', {'schemaVersion': 2, 'baseRevision': 0,
                        'changeId': 'first', 'data': sample()}), timeout=5) as response:
                    self.assertEqual(json.load(response)['revision'], 1)
                with urlopen(Request(base+'changes?after=0',
                        headers={'Authorization': 'Bearer '+key}), timeout=5) as response:
                    self.assertEqual(json.load(response)['changes'][0]['revision'], 1)
                with urlopen(Request(base+'design-docs?path=docs%2Fdesign%2Fexample.md&revision=1',
                        headers={'Authorization': 'Bearer '+key}), timeout=5) as response:
                    self.assertEqual(json.load(response)['content'], '# design')
                with urlopen(Request(base+'channel/changes?after=0',
                        headers={'Authorization': 'Bearer '+key}), timeout=5) as response:
                    self.assertEqual(json.load(response)['headSequence'], 0)
                with self.assertRaises(HTTPError) as caught:
                    urlopen(post('sync-v2', {'schemaVersion': 2, 'baseRevision': 0,
                        'changeId': 'stale', 'data': sample(role='stale')}), timeout=5)
                self.assertEqual(caught.exception.code, 409)
                caught.exception.close()
                with urlopen(Request(base+'snapshot', headers={'Authorization': 'Bearer '+key}), timeout=5) as response:
                    shown = json.load(response)
                    self.assertIn('同步冲突', shown['issues'][0]['message'])
                    self.assertEqual(shown['syncRevision'], 1)
                    self.assertTrue(shown['sampledAt'])
                with urlopen(Request(base+'conflicts/1', headers={'Authorization': 'Bearer '+key}), timeout=5) as response:
                    self.assertTrue(json.load(response)['differences'])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=2)


class QueueTests(unittest.TestCase):
    def test_bounded_queue_serializes_writes(self):
        import time
        entered, release = threading.Event(), threading.Event()
        queue = WriteQueue(capacity=1)
        results = []
        def slow():
            entered.set()
            release.wait(2)
            results.append('first')
        first = threading.Thread(target=lambda: queue.call(slow), daemon=True)
        first.start()
        self.assertTrue(entered.wait(1))
        second = threading.Thread(target=lambda: queue.call(lambda: results.append('second')), daemon=True)
        second.start()
        for _ in range(100):
            if queue.queue.full():
                break
            time.sleep(0.001)
        self.assertTrue(queue.queue.full())
        with self.assertRaises(WriteQueueBusy):
            queue.call(lambda: results.append('third'))
        release.set()
        first.join(2)
        second.join(2)
        self.assertEqual(results, ['first', 'second'])


if __name__ == '__main__':
    unittest.main()
