"""Crash-recoverable, single-writer coordination records (standard library only)."""
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import quote


class Rejected(ValueError):
    pass


def now():
    return datetime.now(timezone.utc).isoformat()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def safe(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise Rejected('Expected a project-relative path')
    path = Path(relative)
    if path.is_absolute() or any(part in {'.', '..'} for part in relative.split('/')):
        raise Rejected('Path traversal is forbidden: '+relative)
    resolved = root/path
    if any(parent.is_symlink() for parent in [resolved, *resolved.parents] if parent != root.parent and parent.is_relative_to(root)):
        raise Rejected('Symlink path is forbidden: '+relative)
    if not resolved.resolve().is_relative_to(root):
        raise Rejected('Path escapes project')
    return resolved


def file_hash(root, relative):
    path = safe(root, relative)
    if not path.exists():
        return None
    if not path.is_file():
        raise Rejected('Expected a file: '+relative)
    return sha(path.read_bytes())


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.'+path.name)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(value); stream.flush(); os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Store:
    def __init__(self, root, task):
        self.root = Path(root).resolve()
        if not task or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in task):
            raise Rejected('Task ID must use letters, digits, hyphens or underscores')
        self.task = task
        self.folder = safe(self.root, 'docs/scheduling/'+task)

    @contextmanager
    def locked(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        lock_path = safe(self.root, (self.folder/'.lock').relative_to(self.root).as_posix())
        with lock_path.open('a+b') as handle:
            try:
                if os.name == 'nt':
                    import msvcrt
                    if handle.tell() == 0:
                        handle.write(b'0'); handle.flush()
                    handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise Rejected('Another coordinator operation is active') from exc
            try:
                yield self
            finally:
                if os.name == 'nt':
                    handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def journal(self):
        path = safe(self.root, (self.folder/'events.jsonl').relative_to(self.root).as_posix())
        if not path.exists():
            return []
        raw = path.read_bytes()
        if raw and not raw.endswith(b'\n'):
            raise Rejected('Partial journal tail: preserve it and repair explicitly; no automatic truncation')
        events = []
        previous = None
        for line in raw.splitlines():
            event = json.loads(line)
            signature = event.pop('hash', None)
            if event.get('seq') != len(events)+1 or event.get('taskId') != self.task or event.get('previousHash') != previous or sha(encoded(event)) != signature:
                raise Rejected('Invalid journal sequence or hash chain')
            event['hash'] = signature; events.append(event); previous = signature
        return events

    def load(self, recover=False):
        events = self.journal()
        if not events:
            raise Rejected('Task not initialized')
        bundle = events[-1]['after']
        for name in ['plan', 'state']:
            path = safe(self.root,(self.folder/(name+'.json')).relative_to(self.root).as_posix())
            try:
                actual = json.loads(path.read_text())
            except (OSError, ValueError):
                actual = None
            if actual != bundle[name] and not recover:
                raise Rejected('Projection mismatch: use recover before any mutation')
        if recover:
            self.materialize(bundle)
        # Work on a copy, never mutate a previous journal snapshot.
        return json.loads(json.dumps(bundle))

    def materialize(self, bundle):
        for name in ['plan', 'state']:
            atomic(self.folder/(name+'.json'), json.dumps(bundle[name], ensure_ascii=False, indent=2).encode()+b'\n')
        state = bundle['state']
        def cell(value):
            return str(value).replace('|', '\\|').replace('\n', ' ').replace('<', '&lt;').replace('>', '&gt;')
        rows = ['# Task coordination: '+self.task, '', f"stateRevision: {state['stateRevision']} · lastEventSeq: {state['lastEventSeq']}", '',
                '| Node | Role | Status | Requirement / Design | Feedback | Next action | Evidence |', '| --- | --- | --- | --- | --- | --- | --- |']
        for node in state['nodes']:
            versions = node['assignedRevisions']
            values = [node['nodeId'], node['roleId'], node['status'], versions['requirement']+' / '+versions['design'], node.get('latestReport', {}).get('summary', ''), node.get('nextAction', {}).get('summary', '')]
            links=[]
            for check,evidence in node.get('checkEvidence',{}).items():
                target=safe(self.root,evidence['path'])
                relative=os.path.relpath(target,self.folder).replace('\\','/')
                links.append('['+cell(check)+']('+quote(relative,safe='/._-')+')')
            rows.append('| '+' | '.join(cell(v) for v in values)+' | '+' '.join(links)+' |')
        atomic(self.folder/'board.md', ('\n'.join(rows)+'\n').encode())

    def commit(self, bundle, kind, summary, node=None, extra=None):
        events = self.journal(); seq = len(events)+1
        state = bundle['state']; state['stateRevision'] = seq; state['lastEventSeq'] = seq; state['updatedAt'] = now()
        state['planRevision'] = bundle['plan']['planRevision']
        event = {'seq': seq, 'eventId': self.task+'-'+str(seq), 'taskId': self.task, 'kind': kind,
                 'summary': summary, 'receivedAt': now(), 'previousHash': events[-1]['hash'] if events else None, 'after': bundle}
        if node is not None:
            event['nodeId'] = node
        if extra:
            event['detail'] = extra
        event['hash'] = sha(encoded(event))
        log_path = safe(self.root, (self.folder/'events.jsonl').relative_to(self.root).as_posix())
        with log_path.open('ab') as stream:
            stream.write(encoded(event)+b'\n'); stream.flush(); os.fsync(stream.fileno())
        self.materialize(bundle)
        return {'status': 'ok', 'stateRevision': seq, 'eventId': event['eventId']}
