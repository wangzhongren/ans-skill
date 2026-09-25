import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[2]/'dashboard/auto_update.sh'


def run(*args, cwd=None, env=None, check=True):
    return subprocess.run(args, cwd=cwd, env=env, text=True,
                          capture_output=True, check=check)


class AutoUpdateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.remote = self.root/'remote.git'
        self.seed = self.root/'seed'
        self.checkout = self.root/'checkout'
        run('git', 'init', '--bare', '--initial-branch=main', str(self.remote))
        run('git', 'init', '--initial-branch=main', str(self.seed))
        run('git', 'config', 'user.email', 'test@example.invalid', cwd=self.seed)
        run('git', 'config', 'user.name', 'Test', cwd=self.seed)
        (self.seed/'dashboard').mkdir()
        (self.seed/'dashboard/compose.yaml').write_text('services: {}\n')
        (self.seed/'.gitignore').write_text('/dashboard/.env\n')
        self.commit('initial')
        run('git', 'remote', 'add', 'origin', str(self.remote), cwd=self.seed)
        run('git', 'push', '-u', 'origin', 'main', cwd=self.seed)
        run('git', 'clone', str(self.remote), str(self.checkout))
        (self.checkout/'dashboard/.env').write_text('ANS_DASHBOARD_HOST=example.invalid\n')
        self.bin = self.root/'bin'
        self.bin.mkdir()
        for name, body in {
            'flock': '#!/bin/sh\nexit 0\n',
            'docker': '''#!/bin/sh
echo "$*" >> "$FAKE_DOCKER_LOG"
if [ -n "$FAKE_DOCKER_FAIL_ONCE" ] && [ ! -f "$FAKE_DOCKER_FAIL_ONCE" ]; then
  touch "$FAKE_DOCKER_FAIL_ONCE"
  exit 1
fi
exit 0
''',
        }.items():
            path = self.bin/name
            path.write_text(body)
            path.chmod(0o755)
        self.log = self.root/'docker.log'
        self.env = {**os.environ, 'ANS_SKILL_REPO': str(self.checkout),
                    'ANS_UPDATE_LOCK': str(self.root/'update.lock'),
                    'FAKE_DOCKER_LOG': str(self.log),
                    'FAKE_DOCKER_FAIL_ONCE': '',
                    'PATH': str(self.bin)+os.pathsep+os.environ['PATH']}

    def commit(self, message):
        path = self.seed/'dashboard/version.txt'
        path.write_text(message)
        run('git', 'add', '.', cwd=self.seed)
        run('git', 'commit', '-m', message, cwd=self.seed)

    def update(self):
        return run('bash', str(SCRIPT), env=self.env, check=False)

    def test_only_fast_forward_changes_rebuild(self):
        self.assertEqual(self.update().returncode, 0)
        self.assertFalse(self.log.exists())
        self.commit('next')
        run('git', 'push', 'origin', 'main', cwd=self.seed)
        self.assertEqual(self.update().returncode, 0)
        self.assertEqual(run('git', 'rev-parse', 'HEAD', cwd=self.checkout).stdout.strip(),
                         run('git', 'rev-parse', 'HEAD', cwd=self.seed).stdout.strip())
        self.assertIn('compose up --build --wait', self.log.read_text())
        self.assertEqual(self.update().returncode, 0)
        self.assertEqual(len(self.log.read_text().splitlines()), 1)

    def test_dirty_checkout_stops_and_failed_build_rolls_back(self):
        (self.checkout/'dashboard/version.txt').write_text('local edit')
        self.assertEqual(self.update().returncode, 2)
        run('git', 'checkout', '--', 'dashboard/version.txt', cwd=self.checkout)
        previous = run('git', 'rev-parse', 'HEAD', cwd=self.checkout).stdout.strip()
        self.commit('broken')
        run('git', 'push', 'origin', 'main', cwd=self.seed)
        self.env['FAKE_DOCKER_FAIL_ONCE'] = str(self.root/'fail-once')
        self.assertEqual(self.update().returncode, 1)
        self.assertEqual(run('git', 'rev-parse', 'HEAD', cwd=self.checkout).stdout.strip(), previous)
        self.assertEqual(len(self.log.read_text().splitlines()), 2)


if __name__ == '__main__':
    unittest.main()
