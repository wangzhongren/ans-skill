import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.local_config import save_project_config
from dashboard.sync import main as sync_main
from dashboard.sync_runtime import SyncAlreadyRunning, SyncLease, sync_status


class SyncRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'project'
        self.root.mkdir()
        runtime_dir = patch('dashboard.sync_runtime.tempfile.gettempdir', return_value=self.temp.name)
        runtime_dir.start()
        self.addCleanup(runtime_dir.stop)

    def test_lease_reports_liveness_and_prevents_duplicate(self):
        self.assertEqual(sync_status(self.root)['running'], False)
        with SyncLease(self.root, 'alpha', 10) as lease:
            status = sync_status(self.root)
            self.assertTrue(status['running'])
            self.assertEqual(status['intervalSeconds'], 10)
            self.assertNotIn('projectKey', json.dumps(status))
            with self.assertRaises(SyncAlreadyRunning):
                with SyncLease(self.root, 'alpha', 10):
                    self.fail('duplicate should not enter')
            lease.success()
            self.assertIsNotNone(sync_status(self.root)['lastSuccessAt'])
        stopped = sync_status(self.root)
        self.assertFalse(stopped['running'])
        self.assertIsNotNone(stopped['stoppedAt'])

    def test_cli_status_does_not_need_key_and_detects_configuration(self):
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(sync_main(['--root', str(self.root), '--status']), 0)
        self.assertEqual(json.loads(output.getvalue())['configured'], False)
        save_project_config('alpha', self.root, 'https://example.com', 'ansp_example-key')
        output = io.StringIO()
        with redirect_stdout(output):
            sync_main(['--root', str(self.root), '--status'])
        self.assertEqual(json.loads(output.getvalue())['configured'], True)
        self.assertFalse(json.loads(output.getvalue())['running'])

    def test_continuous_cli_marks_success_and_exits_without_stale_running_flag(self):
        observed = []

        def send(*_args):
            observed.append(sync_status(self.root)['running'])
            return {'received': True}

        with patch.dict(os.environ, {'ANS_DASHBOARD_KEY': 'ansp_example-key'}), \
             patch('dashboard.sync.projection', return_value={'schemaVersion': 1}), \
             patch('dashboard.sync.send', side_effect=send), \
             patch('dashboard.sync.time.sleep', side_effect=KeyboardInterrupt), \
             redirect_stdout(io.StringIO()):
            self.assertEqual(sync_main(['--root', str(self.root), '--project-id', 'alpha',
                                        '--server-url', 'https://example.com', '--interval', '10']), 0)
        self.assertEqual(observed, [True])
        self.assertFalse(sync_status(self.root)['running'])
        self.assertIsNotNone(sync_status(self.root)['lastSuccessAt'])

    def test_duplicate_cli_does_not_send(self):
        with SyncLease(self.root, 'alpha', 10), \
             patch.dict(os.environ, {'ANS_DASHBOARD_KEY': 'ansp_example-key'}), \
             patch('dashboard.sync.send') as send, \
             redirect_stderr(io.StringIO()) as errors:
            result = sync_main(['--root', str(self.root), '--project-id', 'alpha',
                                '--server-url', 'https://example.com', '--interval', '10'])
        self.assertEqual(result, 2)
        self.assertIn('already running', errors.getvalue())
        send.assert_not_called()

    def test_role_preflight_script_detects_running_process(self):
        script = Path(__file__).resolve().parents[1]/'check_dashboard_sync.py'
        environment = {**os.environ, 'TMPDIR': self.temp.name}
        with SyncLease(self.root, 'alpha', 10):
            result = subprocess.run([sys.executable, str(script), '--root', str(self.root)],
                                    capture_output=True, text=True, env=environment, check=True)
            state = json.loads(result.stdout)
            self.assertTrue(state['running'])
            self.assertFalse(state['configured'])
            self.assertNotIn('projectKey', result.stdout)


if __name__ == '__main__':
    unittest.main()
