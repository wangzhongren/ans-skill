"""Local liveness lease for one continuous cloud-sync process per project."""
from datetime import datetime, timezone
import getpass
import hashlib
import json
import os
from pathlib import Path
import tempfile

from .local_config import config_path


class SyncAlreadyRunning(RuntimeError):
    """A continuous sync process already owns this project's lease."""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _paths(root):
    project = Path(root).expanduser().resolve()
    if hasattr(os, 'getuid'):
        user_id = str(os.getuid())
    else:
        user_id = hashlib.sha256(getpass.getuser().encode('utf-8')).hexdigest()[:12]
    if os.name == 'nt':
        runtime_root = Path.home()/'.ans-dashboard'/'runtime'
    else:
        runtime_root = Path('/tmp')
    folder = runtime_root/('ans-dashboard-sync-'+user_id)
    if folder.is_symlink() or (folder.exists() and not folder.is_dir()):
        raise ValueError('Sync runtime directory must not be a symlink')
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    if hasattr(os, 'getuid') and folder.stat().st_uid != os.getuid():
        raise ValueError('Sync runtime directory has a different owner')
    os.chmod(folder, 0o700)
    stem = hashlib.sha256(str(project).encode('utf-8')).hexdigest()[:32]
    return folder/(stem+'.lock'), folder/(stem+'.json')


def _lock(handle):
    try:
        if os.name == 'nt':
            import msvcrt
            handle.seek(0)
            if not handle.read(1):
                handle.seek(0)
                handle.write(b'0')
                handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _unlock(handle):
    if os.name == 'nt':
        import msvcrt
        handle.seek(0)
        msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
    else:
        import fcntl
        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _write(path, value):
    descriptor, temporary = tempfile.mkstemp(prefix='.sync-', dir=path.parent)
    try:
        with os.fdopen(descriptor, 'w', encoding='utf-8') as output:
            json.dump(value, output, ensure_ascii=False)
            output.write('\n')
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class SyncLease:
    def __init__(self, root, project_id, interval_seconds):
        self.lock_path, self.status_path = _paths(root)
        self.project_id = project_id
        self.interval_seconds = interval_seconds
        self.handle = None
        self.state = None

    def __enter__(self):
        if self.lock_path.is_symlink() or self.status_path.is_symlink():
            raise ValueError('Sync runtime files must not be symlinks')
        self.handle = self.lock_path.open('a+b')
        os.chmod(self.lock_path, 0o600)
        if not _lock(self.handle):
            self.handle.close()
            self.handle = None
            raise SyncAlreadyRunning('Continuous sync is already running for this project')
        try:
            self.state = {'projectId': self.project_id, 'pid': os.getpid(),
                          'intervalSeconds': self.interval_seconds, 'startedAt': _now(),
                          'lastSuccessAt': None, 'lastError': None, 'stoppedAt': None}
            _write(self.status_path, self.state)
            return self
        except Exception:
            _unlock(self.handle)
            self.handle.close()
            self.handle = None
            raise

    def success(self):
        self.state['lastSuccessAt'] = _now()
        self.state['lastError'] = None
        _write(self.status_path, self.state)

    def failure(self, error):
        code = getattr(error, 'code', None)
        if isinstance(code, int):
            self.state['lastError'] = 'HTTP '+str(code)
        else:
            self.state['lastError'] = type(error).__name__
        _write(self.status_path, self.state)

    def __exit__(self, *_):
        if self.handle is None:
            return
        try:
            self.state['stoppedAt'] = _now()
            _write(self.status_path, self.state)
        finally:
            _unlock(self.handle)
            self.handle.close()
            self.handle = None


def sync_status(root):
    lock_path, status_path = _paths(root)
    configured = config_path(root).is_file()
    if lock_path.is_symlink() or status_path.is_symlink():
        raise ValueError('Sync runtime files must not be symlinks')
    with lock_path.open('a+b') as handle:
        os.chmod(lock_path, 0o600)
        acquired = _lock(handle)
        if acquired:
            _unlock(handle)
    state = {}
    if status_path.is_file():
        try:
            state = json.loads(status_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            state = {}
    return {'configured': configured, 'running': not acquired,
            'projectId': state.get('projectId'), 'intervalSeconds': state.get('intervalSeconds'),
            'lastSuccessAt': state.get('lastSuccessAt'), 'lastError': state.get('lastError'),
            'stoppedAt': state.get('stoppedAt')}
