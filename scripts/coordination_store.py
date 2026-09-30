"""Single-writer, Git-readable task records with a verifiable event history."""
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


def task_id_valid(task):
    return isinstance(task, str) and bool(task) and all(c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in task)


def display(value):
    return str(value).replace('|', '\\|').replace('\n', ' ').replace('\r', ' ').replace('<', '&lt;').replace('>', '&gt;')


MARKER = b'\n<!-- ANS-TASK-EVENTS-V1\n'
END_MARKER = b'\nANS-TASK-EVENTS-END -->\n'


def task_page(bundle, events):
    plan = bundle['plan']; state = bundle['state']; task = plan['taskId']
    rows = [
        '# 任务：'+display(task), '',
        '任务记录由 `task_ops` 生成。修改需求、设计或权限后，使用对应命令更新；不要手工改状态。', '',
        '需求：`'+display(plan['requirement']['path'])+'`（'+display(plan['requirement']['version'])+'）',
        '设计：`'+display(plan['design']['path'])+'`（'+display(plan['design']['version'])+'）',
        '状态版本：'+str(state['stateRevision'])+' · 最新事件：'+str(state['lastEventSeq']), '',
        '## 步骤', '',
        '| 步骤 | 负责角色 | 当前状态 | 前置步骤 | 最近反馈 |',
        '| --- | --- | --- | --- | --- |',
    ]
    for planned, current in zip(plan['nodes'], state['nodes']):
        dependencies = ', '.join(planned.get('dependsOn', [])) or '无'
        report = current.get('latestReport', {}).get('summary', '')
        rows.append('| '+' | '.join(display(value) for value in [
            planned['nodeId'], planned['roleId'], current['status'], dependencies, report,
        ])+' |')
    rows.extend(['', '## 变化记录', '', '| 序号 | 时间 | 变化 | 说明 |', '| --- | --- | --- | --- |'])
    for event in events:
        rows.append('| '+' | '.join(display(value) for value in [
            event['seq'], event['receivedAt'], event['kind'], event['summary'],
        ])+' |')
    rows.extend(['', '机器记录保存在下面的固定区块，供程序核对事件顺序和版本。', ''])
    visible = '\n'.join(rows).encode()
    payload = b'\n'.join(encoded(event).replace(b'-->', b'--\\u003e') for event in events)
    return visible+MARKER+payload+END_MARKER


def read_task_page(path, expected_task=None):
    # Git may check out text as CRLF on Windows; the event hashes cover data, not line endings.
    raw = path.read_bytes().replace(b'\r\n', b'\n')
    if raw.count(MARKER) != 1 or not raw.endswith(END_MARKER):
        raise Rejected('Task record is incomplete or has merge conflicts: '+str(path))
    _, encoded_events = raw.split(MARKER, 1)
    encoded_events = encoded_events[:-len(END_MARKER)]
    if not encoded_events:
        raise Rejected('Task record has no events')
    events = []; previous = None
    try:
        for line in encoded_events.split(b'\n'):
            event = json.loads(line)
            signature = event.pop('hash', None)
            if (not isinstance(event, dict) or event.get('seq') != len(events)+1
                    or (expected_task is not None and event.get('taskId') != expected_task)
                    or event.get('previousHash') != previous or sha(encoded(event)) != signature):
                raise Rejected('Invalid task event sequence or hash chain')
            event['hash'] = signature; events.append(event); previous = signature
    except (UnicodeError, ValueError, TypeError, AttributeError) as exc:
        raise Rejected('Invalid task event: '+str(path)) from exc
    bundle = events[-1].get('after')
    if not isinstance(bundle, dict) or not isinstance(bundle.get('plan'), dict) or not isinstance(bundle.get('state'), dict):
        raise Rejected('Task record has no current plan and state')
    if (bundle['plan'].get('taskId') != events[-1].get('taskId')
            or bundle['state'].get('taskId') != events[-1].get('taskId')
            or bundle['state'].get('lastEventSeq') != len(events)):
        raise Rejected('Task record and event history disagree')
    if raw != task_page(bundle, events):
        raise Rejected('Task record was edited outside task_ops or has merge conflicts: '+str(path))
    return bundle, events


class Store:
    def __init__(self, root, task):
        self.root = Path(root).resolve()
        if not task_id_valid(task):
            raise Rejected('Task ID must use letters, digits, hyphens or underscores')
        self.task = task
        self.folder = safe(self.root, '.ans/runtime/'+task)
        self.document = safe(self.root, 'docs/scheduling/'+task+'.md')

    @contextmanager
    def locked(self):
        self.folder.mkdir(parents=True, exist_ok=True)
        ignore_path = safe(self.root, '.ans/runtime/.gitignore')
        if not ignore_path.exists():
            atomic(ignore_path, b'*\n')
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
        safe(self.root, self.document.relative_to(self.root).as_posix())
        if not self.document.exists():
            return []
        _, events = read_task_page(self.document, self.task)
        return events

    def load(self, recover=False):
        safe(self.root, self.document.relative_to(self.root).as_posix())
        if not self.document.exists():
            raise Rejected('Task not initialized; older JSON task directories are read-only')
        bundle, _ = read_task_page(self.document, self.task)
        return json.loads(json.dumps(bundle))

    def materialize(self, bundle, events=None):
        if events is None:
            events = self.journal()
        atomic(self.document, task_page(bundle, events))

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
        events.append(event)
        self.materialize(bundle, events)
        return {'status': 'ok', 'stateRevision': seq, 'eventId': event['eventId']}
