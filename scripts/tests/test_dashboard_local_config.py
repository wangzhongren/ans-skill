import io
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from dashboard.channel_cli import main as channel_main
from dashboard.local_config import config_path, load_project_config, main as config_main, save_project_config
from dashboard.sync import main as sync_main


class LocalConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'business'
        self.root.mkdir()
        self.key = 'ansp_example-project-key'

    def test_private_config_and_cli_clients_share_one_project_key(self):
        with patch('dashboard.local_config.getpass.getpass', return_value=self.key), redirect_stdout(io.StringIO()):
            self.assertEqual(config_main(['init', '--project-id', 'dkds', '--root', str(self.root),
                                          '--server-url', 'https://example.com/ans-dashboard']), 0)
        path = config_path(self.root)
        self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        self.assertEqual(load_project_config(self.root)['projectKey'], self.key)
        shown = io.StringIO()
        with redirect_stdout(shown):
            config_main(['show', '--root', str(self.root)])
        self.assertNotIn(self.key, shown.getvalue())
        self.assertEqual(json.loads(shown.getvalue())['projectId'], 'dkds')

        with patch.dict(os.environ, {'ANS_DASHBOARD_KEY': ''}), \
             patch('dashboard.sync.projection', return_value={'schemaVersion': 1}) as collect, \
             patch('dashboard.sync.send', return_value={'received': True}) as send, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(sync_main(['--root', str(self.root)]), 0)
        collect.assert_called_once_with(self.root, 'dkds', None, None)
        send.assert_called_once_with('https://example.com/ans-dashboard', 'dkds', self.key,
                                     {'schemaVersion': 1})

        with patch.dict(os.environ, {'ANS_DASHBOARD_KEY': ''}), \
             patch('dashboard.channel_cli.call', return_value={'messages': [], 'requests': []}) as call, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(channel_main(['--root', str(self.root), 'list']), 0)
        call.assert_called_once_with('https://example.com/ans-dashboard', 'dkds', self.key,
                                     'channel', None)

    def test_existing_config_requires_explicit_replace_and_rejects_unsafe_file(self):
        path = save_project_config('dkds', self.root, 'https://example.com/ans-dashboard', self.key)
        with self.assertRaisesRegex(ValueError, '--replace'):
            save_project_config('dkds', self.root, 'https://example.com/ans-dashboard', 'ansp_new-key')
        self.assertEqual(load_project_config(self.root)['projectKey'], self.key)
        save_project_config('dkds', self.root, 'https://example.com/ans-dashboard', 'ansp_new-key', replace=True)
        self.assertEqual(load_project_config(self.root)['projectKey'], 'ansp_new-key')
        path.chmod(0o644)
        with self.assertRaisesRegex(ValueError, 'chmod 600'):
            load_project_config(self.root)

    def test_invalid_project_and_server_are_rejected_before_writing(self):
        with self.assertRaisesRegex(ValueError, 'Project id'):
            save_project_config('../wrong', self.root, 'https://example.com', self.key)
        with self.assertRaisesRegex(ValueError, 'HTTPS'):
            save_project_config('dkds', self.root, 'http://example.com', self.key)
        self.assertFalse(config_path(self.root).exists())

    def test_explicit_arguments_and_environment_still_work_without_config(self):
        with patch.dict(os.environ, {'ANS_DASHBOARD_KEY': self.key}), \
             patch('dashboard.sync.projection', return_value={'schemaVersion': 1}), \
             patch('dashboard.sync.send', return_value={'received': True}) as send, \
             redirect_stdout(io.StringIO()):
            self.assertEqual(sync_main(['--root', str(self.root), '--project-id', 'dkds',
                                        '--server-url', 'https://example.com/ans-dashboard']), 0)
        send.assert_called_once_with('https://example.com/ans-dashboard', 'dkds', self.key,
                                     {'schemaVersion': 1})
        self.assertFalse(config_path(self.root).exists())

    def test_git_project_ignores_secret_and_refuses_tracked_file(self):
        subprocess.run(['git', 'init', '-q', self.temp.name], check=True)
        path = save_project_config('dkds', self.root, 'https://example.com', self.key)
        ignored = subprocess.run(['git', '-C', str(self.root), 'check-ignore', '-q',
                                  path.name], check=False)
        self.assertEqual(ignored.returncode, 0)
        temporary_ignored = subprocess.run(['git', '-C', str(self.root), 'check-ignore', '-q',
                                            '.ans-dashboard-example'], check=False)
        self.assertEqual(temporary_ignored.returncode, 0)
        status = subprocess.run(['git', '-C', str(self.root), 'status', '--short'],
                                capture_output=True, text=True, check=True)
        self.assertNotIn(path.name, status.stdout)
        subprocess.run(['git', '-C', str(self.root), 'add', '-f', path.name], check=True)
        with self.assertRaisesRegex(ValueError, 'tracked by Git'):
            save_project_config('dkds', self.root, 'https://example.com', 'ansp_new-key', replace=True)


if __name__ == '__main__':
    unittest.main()
