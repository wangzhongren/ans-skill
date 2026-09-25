"""Shared access metadata and separate SQLite projections for each project."""
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time

PROJECT_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
USERNAME = re.compile(r'^[A-Za-z0-9_.-]{3,64}$')
SCRYPT_N = 1 << 15
SCRYPT_R = 8
SCRYPT_P = 3
SESSION_SECONDS = 8 * 60 * 60
MAX_PROJECTION_BYTES = 4 * 1024 * 1024


def utcnow():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def password_digest(password, salt):
    if not isinstance(password, str) or not 15 <= len(password) <= 1024:
        raise ValueError('Password must contain 15–1024 characters')
    return hashlib.scrypt(password.encode('utf-8'), salt=salt, n=SCRYPT_N, r=SCRYPT_R,
                          p=SCRYPT_P, maxmem=128 * 1024 * 1024, dklen=32)


class CloudStore:
    def __init__(self, state_dir):
        self.state_dir = Path(state_dir).resolve()
        self.state_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.db = self.state_dir/'dashboard.sqlite3'
        self.projects_dir = self.state_dir/'projects'
        if self.projects_dir.is_symlink():
            raise ValueError('Project database directory must not be a symlink')
        self.projects_dir.mkdir(mode=0o700, exist_ok=True)
        created = not self.db.exists()
        with self.connection() as connection:
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY, username TEXT NOT NULL UNIQUE, salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','viewer')),
                    active INTEGER NOT NULL DEFAULT 1, failures INTEGER NOT NULL DEFAULT 0,
                    locked_until REAL NOT NULL DEFAULT 0, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    csrf_token TEXT NOT NULL, expires_at REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS projects (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL,
                    last_received_at TEXT, created_at TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS memberships (
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    PRIMARY KEY(user_id,project_id));
                CREATE TABLE IF NOT EXISTS project_keys (
                    id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    label TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL, revoked_at TEXT);
                CREATE TABLE IF NOT EXISTS role_tokens (
                    id INTEGER PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
                    role_id TEXT NOT NULL, label TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL, revoked_at TEXT);
            ''')
            columns = {row['name'] for row in connection.execute('PRAGMA table_info(projects)')}
            if 'last_received_at' not in columns:
                connection.execute('ALTER TABLE projects ADD COLUMN last_received_at TEXT')
            self.has_legacy_projection = {'snapshot_json', 'contexts_json', 'received_at'} <= columns
        if created:
            os.chmod(self.db, 0o600)
        self.migrate_project_data()

    def project_path(self, project_id):
        if not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id):
            raise ValueError('Invalid project id')
        if self.projects_dir.is_symlink():
            raise ValueError('Project database directory must not be a symlink')
        path = self.projects_dir/(project_id+'.sqlite3')
        if path.is_symlink():
            raise ValueError('Project database file must not be a symlink')
        return path

    def ensure_project_db(self, project_id):
        path = self.project_path(project_id)
        created = not path.exists()
        with closing(sqlite3.connect(path, timeout=5)) as connection:
            connection.execute('PRAGMA busy_timeout=5000')
            connection.execute('''CREATE TABLE IF NOT EXISTS projection (
                singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                snapshot_json TEXT NOT NULL, contexts_json TEXT NOT NULL,
                received_at TEXT NOT NULL)''')
            connection.commit()
        if created:
            os.chmod(path, 0o600)
        return path

    def write_project_data(self, project_id, snapshot_json, contexts_json, received_at, migrate=False):
        with self.connection() as connection:
            if connection.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is None:
                raise ValueError('Project not found')
        path = self.ensure_project_db(project_id)
        with self.connection() as connection:
            if migrate:
                connection.execute('PRAGMA secure_delete=ON')
            connection.execute('ATTACH DATABASE ? AS project_data', (str(path),))
            connection.execute('BEGIN IMMEDIATE')
            if connection.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is None:
                raise ValueError('Project not found')
            connection.execute('''INSERT OR REPLACE INTO project_data.projection
                (singleton,snapshot_json,contexts_json,received_at) VALUES (1,?,?,?)''',
                               (snapshot_json, contexts_json, received_at))
            if migrate:
                connection.execute('''UPDATE projects SET last_received_at=?,
                    snapshot_json=NULL,contexts_json=NULL,received_at=NULL WHERE id=?''',
                                   (received_at, project_id))
            else:
                connection.execute('UPDATE projects SET last_received_at=? WHERE id=?',
                                   (received_at, project_id))

    def migrate_project_data(self):
        with self.connection() as connection:
            rows = connection.execute('SELECT id FROM projects').fetchall()
            legacy = connection.execute('''SELECT id,snapshot_json,contexts_json,received_at FROM projects
                WHERE snapshot_json IS NOT NULL''').fetchall() if self.has_legacy_projection else []
        for row in rows:
            self.ensure_project_db(row['id'])
        for row in legacy:
            self.write_project_data(row['id'], row['snapshot_json'], row['contexts_json'] or '{}',
                                    row['received_at'] or utcnow(), migrate=True)

    @contextmanager
    def connection(self):
        connection = sqlite3.connect(self.db, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('PRAGMA busy_timeout=5000')
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def has_users(self):
        with self.connection() as connection:
            return connection.execute('SELECT 1 FROM users LIMIT 1').fetchone() is not None

    def create_user(self, username, password, role='viewer', bootstrap=False):
        if not isinstance(username, str) or not USERNAME.fullmatch(username):
            raise ValueError('Username must be 3–64 letters, digits, dots, underscores, or hyphens')
        if role not in ('admin', 'viewer'):
            raise ValueError('Role must be admin or viewer')
        salt = secrets.token_bytes(16)
        password_hash = password_digest(password, salt)
        with self.connection() as connection:
            connection.execute('BEGIN IMMEDIATE')
            if bootstrap and connection.execute('SELECT 1 FROM users LIMIT 1').fetchone():
                raise ValueError('An administrator already exists')
            connection.execute('INSERT INTO users(username,salt,password_hash,role,created_at) VALUES (?,?,?,?,?)',
                               (username, salt, password_hash, role, utcnow()))
        return {'username': username, 'role': role}

    def authenticate(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str) or len(password) > 1024:
            return None
        with self.connection() as connection:
            row = connection.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
            if row is not None and (not row['active'] or row['locked_until'] > time.time()):
                return None
            salt = row['salt'] if row is not None else b'\x00' * 16
            expected = row['password_hash'] if row is not None else b'\x00' * 32
            try:
                supplied = password_digest(password, salt)
            except ValueError:
                return None
            if row is not None and hmac.compare_digest(expected, supplied):
                connection.execute('UPDATE users SET failures=0,locked_until=0 WHERE id=?', (row['id'],))
                return {'id': row['id'], 'username': row['username'], 'role': row['role']}
            if row is not None:
                failures = row['failures'] + 1
                lock = time.time() + 15 * 60 if failures >= 5 else 0
                connection.execute('UPDATE users SET failures=?,locked_until=? WHERE id=?', (failures, lock, row['id']))
            return None

    def create_session(self, user_id):
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.connection() as connection:
            connection.execute('INSERT INTO sessions VALUES (?,?,?,?)',
                               (digest(token), user_id, csrf, time.time() + SESSION_SECONDS))
        return token, csrf

    def session(self, token):
        if not isinstance(token, str) or len(token) > 256:
            return None
        with self.connection() as connection:
            row = connection.execute('''SELECT users.id,users.username,users.role,sessions.csrf_token
                FROM sessions JOIN users ON users.id=sessions.user_id
                WHERE sessions.token_hash=? AND sessions.expires_at>? AND users.active=1''',
                                     (digest(token), time.time())).fetchone()
            return dict(row) if row else None

    def revoke_session(self, token):
        with self.connection() as connection:
            connection.execute('DELETE FROM sessions WHERE token_hash=?', (digest(token),))

    def projects_for(self, user):
        with self.connection() as connection:
            if user['role'] == 'admin':
                rows = connection.execute('SELECT id,title,last_received_at FROM projects ORDER BY title,id')
            else:
                rows = connection.execute('''SELECT projects.id,projects.title,projects.last_received_at
                    FROM projects JOIN memberships ON memberships.project_id=projects.id
                    WHERE memberships.user_id=? ORDER BY projects.title,projects.id''', (user['id'],))
            return [{'id': row['id'], 'name': row['title'], 'url': '/p/'+row['id']+'/',
                     'receivedAt': row['last_received_at']} for row in rows]

    def can_view(self, user, project_id):
        if user['role'] == 'admin':
            with self.connection() as connection:
                return connection.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is not None
        with self.connection() as connection:
            return connection.execute('SELECT 1 FROM memberships WHERE user_id=? AND project_id=?',
                                      (user['id'], project_id)).fetchone() is not None

    def add_project(self, project_id, title):
        if not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id):
            raise ValueError('Project id must be a lowercase hyphenated slug')
        if not isinstance(title, str) or not title.strip() or len(title) > 120:
            raise ValueError('Project title must be 1–120 characters')
        with self.connection() as connection:
            connection.execute('INSERT INTO projects(id,title,created_at) VALUES (?,?,?)',
                               (project_id, title.strip(), utcnow()))
            self.ensure_project_db(project_id)
        return {'id': project_id, 'name': title.strip(), 'url': '/p/'+project_id+'/'}

    def users(self):
        with self.connection() as connection:
            rows = connection.execute('SELECT id,username,role,active,created_at FROM users ORDER BY username').fetchall()
            return [{'id': row['id'], 'username': row['username'], 'role': row['role'],
                     'active': bool(row['active']), 'createdAt': row['created_at'],
                     'projects': [item['project_id'] for item in connection.execute(
                         'SELECT project_id FROM memberships WHERE user_id=? ORDER BY project_id', (row['id'],))]}
                    for row in rows]

    def grant(self, username, project_id):
        with self.connection() as connection:
            user = connection.execute('SELECT id FROM users WHERE username=? AND active=1', (username,)).fetchone()
            if user is None or connection.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is None:
                raise ValueError('User or project not found')
            connection.execute('INSERT OR IGNORE INTO memberships VALUES (?,?)', (user['id'], project_id))
        return {'username': username, 'projectId': project_id}

    def disable_user(self, username):
        with self.connection() as connection:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT id,role,active FROM users WHERE username=?', (username,)).fetchone()
            if row is None:
                raise ValueError('User not found')
            if row['role'] == 'admin' and row['active'] and connection.execute(
                    "SELECT COUNT(*) FROM users WHERE role='admin' AND active=1").fetchone()[0] <= 1:
                raise ValueError('Cannot disable the last active administrator')
            connection.execute('UPDATE users SET active=0 WHERE id=?', (row['id'],))
            connection.execute('DELETE FROM sessions WHERE user_id=?', (row['id'],))
        return {'username': username, 'active': False}

    def create_key(self, project_id, label):
        if not isinstance(label, str) or not label.strip() or len(label) > 120:
            raise ValueError('Key label must be 1–120 characters')
        token = 'ansp_' + secrets.token_urlsafe(32)
        with self.connection() as connection:
            if connection.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is None:
                raise ValueError('Project not found')
            cursor = connection.execute('INSERT INTO project_keys(project_id,label,token_hash,created_at) VALUES (?,?,?,?)',
                                        (project_id, label.strip(), digest(token), utcnow()))
            key_id = cursor.lastrowid
        return {'id': key_id, 'projectId': project_id, 'label': label.strip(), 'key': token}

    def keys(self):
        with self.connection() as connection:
            return [{'id': row['id'], 'projectId': row['project_id'], 'label': row['label'],
                     'createdAt': row['created_at'], 'revokedAt': row['revoked_at']}
                    for row in connection.execute('SELECT id,project_id,label,created_at,revoked_at FROM project_keys ORDER BY id DESC')]

    def revoke_key(self, key_id):
        with self.connection() as connection:
            cursor = connection.execute('UPDATE project_keys SET revoked_at=? WHERE id=? AND revoked_at IS NULL',
                                        (utcnow(), key_id))
            if cursor.rowcount != 1:
                raise ValueError('Active key not found')
        return {'id': key_id, 'revoked': True}

    def key_allows(self, project_id, token):
        if not isinstance(token, str) or not token.startswith('ansp_') or len(token) > 256:
            return False
        with self.connection() as connection:
            return connection.execute('''SELECT 1 FROM project_keys WHERE project_id=? AND token_hash=?
                AND revoked_at IS NULL''', (project_id, digest(token))).fetchone() is not None

    def role_exists(self, project_id, role_id):
        if not isinstance(role_id, str) or not role_id or len(role_id) > 120:
            return False
        return any(role.get('id') == role_id for role in self.projection(project_id)['snapshot']['roles'])

    def create_role_token(self, project_id, role_id, label):
        if not isinstance(label, str) or not label.strip() or len(label) > 120:
            raise ValueError('Role token label must be 1–120 characters')
        if not self.role_exists(project_id, role_id):
            raise ValueError('Sync this role before creating its credential')
        token = 'ansr_' + secrets.token_urlsafe(32)
        with self.connection() as connection:
            cursor = connection.execute('''INSERT INTO role_tokens
                (project_id,role_id,label,token_hash,created_at) VALUES (?,?,?,?,?)''',
                (project_id, role_id, label.strip(), digest(token), utcnow()))
        return {'id': cursor.lastrowid, 'projectId': project_id, 'roleId': role_id,
                'label': label.strip(), 'token': token}

    def role_tokens(self):
        with self.connection() as connection:
            return [{'id': row['id'], 'projectId': row['project_id'], 'roleId': row['role_id'],
                     'label': row['label'], 'createdAt': row['created_at'], 'revokedAt': row['revoked_at']}
                    for row in connection.execute('''SELECT id,project_id,role_id,label,created_at,revoked_at
                        FROM role_tokens ORDER BY id DESC''')]

    def revoke_role_token(self, token_id):
        with self.connection() as connection:
            cursor = connection.execute('''UPDATE role_tokens SET revoked_at=?
                WHERE id=? AND revoked_at IS NULL''', (utcnow(), token_id))
            if cursor.rowcount != 1:
                raise ValueError('Active role token not found')
        return {'id': token_id, 'revoked': True}

    def role_principal(self, project_id, token):
        if not isinstance(token, str) or not token.startswith('ansr_') or len(token) > 256:
            return None
        with self.connection() as connection:
            row = connection.execute('''SELECT id,role_id FROM role_tokens
                WHERE project_id=? AND token_hash=? AND revoked_at IS NULL''',
                (project_id, digest(token))).fetchone()
        if row is None or not self.role_exists(project_id, row['role_id']):
            return None
        return {'tokenId': row['id'], 'roleId': row['role_id']}

    def ingest(self, project_id, value):
        if not isinstance(value, dict) or value.get('schemaVersion') != 1:
            raise ValueError('Projection requires schemaVersion: 1')
        snapshot, contexts = value.get('snapshot'), value.get('contexts')
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('roles'), list) or not isinstance(contexts, dict):
            raise ValueError('Projection requires snapshot roles and contexts')
        if snapshot.get('projectId') != project_id:
            raise ValueError('Projection projectId mismatch')
        clean_snapshot = dict(snapshot)
        clean_snapshot.pop('projectRootUri', None)
        clean_snapshot['projectId'] = project_id
        clean_roles = []
        for role in clean_snapshot['roles']:
            if not isinstance(role, dict):
                raise ValueError('Projection roles must be objects')
            clean_role = dict(role)
            clean_role['documents'] = {}
            clean_roles.append(clean_role)
        clean_snapshot['roles'] = clean_roles
        serialized = json.dumps({'snapshot': clean_snapshot, 'contexts': contexts}, ensure_ascii=False)
        if len(serialized.encode('utf-8')) > MAX_PROJECTION_BYTES:
            raise ValueError('Projection exceeds 4 MiB')
        self.write_project_data(project_id, json.dumps(clean_snapshot, ensure_ascii=False),
                                json.dumps(contexts, ensure_ascii=False), utcnow())
        return {'projectId': project_id, 'received': True}

    def projection(self, project_id):
        with self.connection() as connection:
            row = connection.execute('SELECT title,last_received_at FROM projects WHERE id=?',
                                     (project_id,)).fetchone()
            if row is None:
                raise ValueError('Project not found')
        path = self.project_path(project_id)
        if not path.exists():
            raise sqlite3.DatabaseError('Project database file is missing')
        with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True, timeout=5)) as connection:
            connection.row_factory = sqlite3.Row
            projection = connection.execute('''SELECT snapshot_json,contexts_json,received_at
                FROM projection WHERE singleton=1''').fetchone()
        if projection is None:
            if row['last_received_at'] is not None:
                raise sqlite3.DatabaseError('Project projection is missing')
            return {'snapshot': {'project': row['title'], 'projectId': project_id, 'roles': [],
                                 'tasks': [], 'events': [], 'issues': [], 'sampledAt': None,
                                 'refreshSeconds': 2, 'limitations': ['项目尚未同步数据。']},
                    'contexts': {}, 'receivedAt': None}
        snapshot = json.loads(projection['snapshot_json'])
        snapshot['project'] = row['title']
        snapshot['receivedAt'] = projection['received_at']
        return {'snapshot': snapshot, 'contexts': json.loads(projection['contexts_json']),
                'receivedAt': projection['received_at']}
