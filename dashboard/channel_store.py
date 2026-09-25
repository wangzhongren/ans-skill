"""Per-project role messages, permission requests, decisions, and audit events."""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import json
import sqlite3

from .cloud_store import utcnow

MESSAGE_KINDS = {'question', 'issue', 'design-change', 'feedback', 'handoff'}


def required(value, name, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(name + ' must be 1–' + str(limit) + ' characters')
    return value.strip()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


class ChannelStore:
    def __init__(self, cloud_store):
        self.cloud = cloud_store

    @contextmanager
    def connection(self, project_id):
        path = self.cloud.ensure_project_db(project_id)
        connection = sqlite3.connect(path, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA busy_timeout=5000')
            connection.execute('PRAGMA foreign_keys=ON')
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS channel_messages (
                    id INTEGER PRIMARY KEY, sender_kind TEXT NOT NULL,
                    sender_id TEXT NOT NULL, to_role_id TEXT NOT NULL,
                    task_id TEXT NOT NULL, kind TEXT NOT NULL, body TEXT NOT NULL,
                    revision TEXT NOT NULL, client_id TEXT NOT NULL,
                    payload_hash TEXT NOT NULL, created_at TEXT NOT NULL,
                    UNIQUE(sender_kind,sender_id,client_id));
                CREATE TABLE IF NOT EXISTS permission_requests (
                    id INTEGER PRIMARY KEY, requester_role_id TEXT NOT NULL,
                    client_id TEXT NOT NULL, task_id TEXT NOT NULL,
                    node_id TEXT NOT NULL, worker_id TEXT NOT NULL,
                    operation TEXT NOT NULL, write_set_json TEXT NOT NULL,
                    plan_revision INTEGER NOT NULL, attempt_number INTEGER NOT NULL,
                    requirement_revision TEXT NOT NULL, design_revision TEXT NOT NULL,
                    boundary_revision TEXT NOT NULL,
                    reason TEXT NOT NULL, payload_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(requester_role_id,client_id));
                CREATE TABLE IF NOT EXISTS permission_decisions (
                    request_id INTEGER PRIMARY KEY REFERENCES permission_requests(id),
                    decision TEXT NOT NULL CHECK(decision IN ('approved','denied')),
                    decided_by TEXT NOT NULL, reason TEXT NOT NULL,
                    decided_at TEXT NOT NULL, expires_at TEXT);
                CREATE TABLE IF NOT EXISTS channel_events (
                    seq INTEGER PRIMARY KEY, kind TEXT NOT NULL,
                    actor_kind TEXT NOT NULL, actor_id TEXT NOT NULL,
                    record_id INTEGER NOT NULL, at TEXT NOT NULL,
                    summary TEXT NOT NULL);
            ''')
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def append_event(self, connection, kind, actor, record_id, summary):
        connection.execute('''INSERT INTO channel_events
            (kind,actor_kind,actor_id,record_id,at,summary) VALUES (?,?,?,?,?,?)''',
            (kind, actor['kind'], actor['id'], record_id, utcnow(), summary))

    def task_is_current(self, snapshot, role_id, payload):
        task = next((item for item in snapshot.get('tasks', [])
                     if item.get('taskId') == payload['taskId'] and item.get('nodeId') == payload['nodeId']), None)
        source = next((item for item in snapshot.get('sources', [])
                       if item.get('taskId') == payload['taskId']), None)
        revisions = task.get('assignedRevisions', {}) if task else {}
        return (task is not None and source is not None and task.get('roleId') == role_id and
                source.get('planRevision') == payload['planRevision'] and
                task.get('operation') == payload['operation'] and
                task.get('writeSet') == payload['writeSet'] and
                type(task.get('attemptNumber', 0)) is int and
                task.get('attemptNumber', 0) + 1 == payload['attemptNumber'] and
                revisions.get('requirement') == payload['requirementRevision'] and
                revisions.get('design') == payload['designRevision'] and
                revisions.get('boundary') == payload['boundaryRevision'])

    def require_current_task(self, connection, role_id, payload):
        row = connection.execute('SELECT snapshot_json FROM projection WHERE singleton=1').fetchone()
        if row is None:
            raise ValueError('Sync the current task before requesting approval')
        if not self.task_is_current(json.loads(row['snapshot_json']), role_id, payload):
            raise ValueError('Task role or version changed; sync and submit a new request')

    def send_message(self, project_id, actor, value):
        to_role = required(value.get('toRoleId'), 'toRoleId', 120)
        if not self.cloud.role_exists(project_id, to_role):
            raise ValueError('Recipient role is not in the current project snapshot')
        payload = {'toRoleId': to_role,
                   'taskId': required(value.get('taskId'), 'taskId', 120),
                   'kind': value.get('kind'),
                   'body': required(value.get('body'), 'body', 4000),
                   'revision': required(value.get('revision'), 'revision', 120)}
        if payload['kind'] not in MESSAGE_KINDS:
            raise ValueError('Unknown message kind')
        client_id = required(value.get('clientMessageId'), 'clientMessageId', 120)
        signature = fingerprint(payload)
        with self.connection(project_id) as connection:
            existing = connection.execute('''SELECT id,payload_hash FROM channel_messages
                WHERE sender_kind=? AND sender_id=? AND client_id=?''',
                (actor['kind'], actor['id'], client_id)).fetchone()
            if existing:
                if existing['payload_hash'] != signature:
                    raise ValueError('Client message id was reused with different content')
                return {'id': existing['id'], 'duplicate': True}
            cursor = connection.execute('''INSERT INTO channel_messages
                (sender_kind,sender_id,to_role_id,task_id,kind,body,revision,client_id,payload_hash,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?)''',
                (actor['kind'], actor['id'], to_role, payload['taskId'], payload['kind'],
                 payload['body'], payload['revision'], client_id, signature, utcnow()))
            self.append_event(connection, 'message', actor, cursor.lastrowid,
                              payload['kind'] + ' → ' + to_role)
            return {'id': cursor.lastrowid, 'duplicate': False}

    def request_permission(self, project_id, role_id, value):
        write_set = value.get('writeSet')
        if not isinstance(write_set, list) or not write_set or len(write_set) > 100:
            raise ValueError('writeSet must contain 1–100 paths')
        for path in write_set:
            if (not isinstance(path, str) or not path or len(path) > 500 or
                    '\\' in path or ':' in path.split('/')[0] or
                    any(part in ('', '.', '..') for part in path.split('/'))):
                raise ValueError('writeSet must contain project-relative file paths')
        if len(set(write_set)) != len(write_set):
            raise ValueError('writeSet contains duplicate paths')
        payload = {name: required(value.get(name), name, 120) for name in
                   ('taskId', 'nodeId', 'workerId', 'operation', 'requirementRevision',
                    'designRevision', 'boundaryRevision')}
        payload['writeSet'] = write_set
        for name in ('planRevision', 'attemptNumber'):
            number = value.get(name)
            if type(number) is not int or number < 1:
                raise ValueError(name + ' must be a positive integer')
            payload[name] = number
        payload['reason'] = required(value.get('reason'), 'reason', 4000)
        client_id = required(value.get('clientRequestId'), 'clientRequestId', 120)
        signature = fingerprint(payload)
        with self.connection(project_id) as connection:
            connection.execute('BEGIN IMMEDIATE')
            self.require_current_task(connection, role_id, payload)
            existing = connection.execute('''SELECT id,payload_hash FROM permission_requests
                WHERE requester_role_id=? AND client_id=?''', (role_id, client_id)).fetchone()
            if existing:
                if existing['payload_hash'] != signature:
                    raise ValueError('Client request id was reused with different content')
                return {'id': existing['id'], 'duplicate': True}
            cursor = connection.execute('''INSERT INTO permission_requests
                (requester_role_id,client_id,task_id,node_id,worker_id,operation,write_set_json,
                 plan_revision,attempt_number,requirement_revision,design_revision,boundary_revision,
                 reason,payload_hash,created_at)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                (role_id, client_id, payload['taskId'], payload['nodeId'], payload['workerId'],
                 payload['operation'], json.dumps(write_set, ensure_ascii=False),
                 payload['planRevision'], payload['attemptNumber'], payload['requirementRevision'],
                 payload['designRevision'], payload['boundaryRevision'], payload['reason'], signature, utcnow()))
            self.append_event(connection, 'permission-requested', {'kind': 'role', 'id': role_id},
                              cursor.lastrowid, payload['taskId'] + '/' + payload['nodeId'])
            return {'id': cursor.lastrowid, 'duplicate': False}

    def decide(self, project_id, request_id, username, value):
        if type(request_id) is not int or request_id < 1:
            raise ValueError('Invalid request id')
        decision = value.get('decision')
        if decision not in ('approved', 'denied'):
            raise ValueError('Decision must be approved or denied')
        reason = required(value.get('reason'), 'reason', 2000)
        at = utcnow()
        expires = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat() if decision == 'approved' else None
        with self.connection(project_id) as connection:
            connection.execute('BEGIN IMMEDIATE')
            request = connection.execute('SELECT * FROM permission_requests WHERE id=?', (request_id,)).fetchone()
            if request is None:
                raise ValueError('Permission request not found')
            if connection.execute('SELECT 1 FROM permission_decisions WHERE request_id=?', (request_id,)).fetchone():
                raise ValueError('Permission request already decided')
            if decision == 'approved':
                self.require_current_task(connection, request['requester_role_id'], {
                    'taskId': request['task_id'], 'nodeId': request['node_id'],
                    'operation': request['operation'], 'writeSet': json.loads(request['write_set_json']),
                    'attemptNumber': request['attempt_number'],
                    'planRevision': request['plan_revision'],
                    'requirementRevision': request['requirement_revision'],
                    'designRevision': request['design_revision'],
                    'boundaryRevision': request['boundary_revision']})
            connection.execute('''INSERT INTO permission_decisions
                (request_id,decision,decided_by,reason,decided_at,expires_at) VALUES (?,?,?,?,?,?)''',
                (request_id, decision, username, reason, at, expires))
            self.append_event(connection, 'permission-'+decision,
                              {'kind': 'user', 'id': username}, request_id, reason)
        return {'requestId': request_id, 'decision': decision, 'expiresAt': expires,
                'executionAuthorized': False}

    def view(self, project_id, role_id=None):
        with self.connection(project_id) as connection:
            if role_id is None:
                messages = connection.execute('SELECT * FROM channel_messages ORDER BY id DESC LIMIT 100').fetchall()
                requests = connection.execute('''SELECT r.*,d.decision,d.decided_by,d.reason AS decision_reason,
                    d.decided_at,d.expires_at FROM permission_requests AS r
                    LEFT JOIN permission_decisions AS d ON d.request_id=r.id ORDER BY r.id DESC LIMIT 100''').fetchall()
                events = connection.execute('SELECT * FROM channel_events ORDER BY seq DESC LIMIT 100').fetchall()
            else:
                messages = connection.execute('''SELECT * FROM channel_messages
                    WHERE (sender_kind='role' AND sender_id=?) OR to_role_id=?
                    ORDER BY id DESC LIMIT 100''', (role_id, role_id)).fetchall()
                requests = connection.execute('''SELECT r.*,d.decision,d.decided_by,d.reason AS decision_reason,
                    d.decided_at,d.expires_at FROM permission_requests AS r
                    LEFT JOIN permission_decisions AS d ON d.request_id=r.id
                    WHERE r.requester_role_id=? ORDER BY r.id DESC LIMIT 100''', (role_id,)).fetchall()
                events = []
        snapshot = self.cloud.projection(project_id)['snapshot']
        result_requests = []
        for row in requests:
            item = dict(row)
            item['writeSet'] = json.loads(item.pop('write_set_json'))
            item.pop('payload_hash')
            item.pop('client_id')
            current = self.task_is_current(snapshot, item['requester_role_id'], {
                'taskId': item['task_id'], 'nodeId': item['node_id'],
                'operation': item['operation'], 'writeSet': item['writeSet'],
                'attemptNumber': item['attempt_number'], 'planRevision': item['plan_revision'],
                'requirementRevision': item['requirement_revision'],
                'designRevision': item['design_revision'],
                'boundaryRevision': item['boundary_revision']})
            item['status'] = ('denied' if item['decision'] == 'denied' else
                              'stale' if not current else
                              'expired' if item['decision'] == 'approved' and item['expires_at'] <= utcnow() else
                              item['decision'] or 'pending')
            item['executionAuthorized'] = False
            result_requests.append(item)
        result_messages = []
        for row in messages:
            item = dict(row)
            item.pop('payload_hash')
            item.pop('client_id')
            result_messages.append(item)
        roles = [{'id': role['id'], 'name': role.get('name', role['id'])}
                 for role in snapshot['roles']]
        return {'roles': roles, 'messages': result_messages, 'requests': result_requests,
                'events': [dict(row) for row in events]}
