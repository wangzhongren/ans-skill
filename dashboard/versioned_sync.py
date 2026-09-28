"""Versioned, periodic Dashboard replication. Source code remains in Git."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

from .cloud_store import PROJECT_ID, utcnow
from .local_config import load_project_config, resolve_document_roots
from .paths import normalize_base_path
from .sync_runtime import SyncAlreadyRunning, SyncLease, sync_status

MAX_BYTES = 8 * 1024 * 1024


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def fingerprint(value):
    return hashlib.sha256(encoded(value).encode('utf-8')).hexdigest()


def entities(value):
    """Stable per-item view used to audit changes inside a captured snapshot."""
    found = {'project': value['snapshot'].get('project')}
    for role in value['snapshot'].get('roles', []):
        found['role:'+str(role['id'])] = role
    for task in value['snapshot'].get('tasks', []):
        key = str(task.get('taskId', ''))+':'+str(task.get('nodeId', ''))
        found['task:'+key] = task
    for role_id, context in value.get('contexts', {}).items():
        found['context-overview:'+role_id] = context.get('outline')
        for topic_id, topic in context.get('topics', {}).items():
            found['context-topic:'+role_id+':'+topic_id] = topic
    for path, content in value.get('artifacts', {}).items():
        found['artifact:'+path] = content
    return found


class ProjectReplica:
    """Append-only snapshot versions in one cloud project's existing SQLite."""
    def __init__(self, cloud):
        self.cloud = cloud
        self._initialized = set()
        self._init_lock = threading.Lock()

    def _open(self, project_id):
        with self.cloud.connection() as global_db:
            if global_db.execute('SELECT 1 FROM projects WHERE id=?', (project_id,)).fetchone() is None:
                raise ValueError('Project not found')
        with self._init_lock:
            if project_id not in self._initialized:
                path = self.cloud.ensure_project_db(project_id)
                with closing(sqlite3.connect(path, timeout=5)) as initial:
                    initial.executescript('''
            CREATE TABLE IF NOT EXISTS sync_meta (singleton INTEGER PRIMARY KEY CHECK(singleton=1), active INTEGER NOT NULL);
            INSERT OR IGNORE INTO sync_meta VALUES (1,0);
            CREATE TABLE IF NOT EXISTS sync_versions (
                revision INTEGER PRIMARY KEY, change_id TEXT NOT NULL UNIQUE,
                content_hash TEXT NOT NULL, content_json TEXT NOT NULL, created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS sync_conflicts (
                id INTEGER PRIMARY KEY, change_id TEXT NOT NULL UNIQUE,
                base_revision INTEGER NOT NULL, head_revision INTEGER NOT NULL,
                content_hash TEXT NOT NULL, content_json TEXT NOT NULL,
                created_at TEXT NOT NULL, resolved_at TEXT);
                    ''')
                    initial.commit()
                self._initialized.add(project_id)
        db = sqlite3.connect(self.cloud.project_path(project_id), timeout=5)
        db.execute('PRAGMA busy_timeout=5000')
        return db

    @staticmethod
    def _activate(db):
        if db.execute('SELECT active FROM sync_meta WHERE singleton=1').fetchone()[0]:
            return
        old = db.execute('SELECT snapshot_json,contexts_json,received_at FROM projection WHERE singleton=1').fetchone()
        if old:
            data = {'schemaVersion': 1, 'snapshot': json.loads(old[0]), 'contexts': json.loads(old[1])}
            raw = encoded(data)
            db.execute('INSERT INTO sync_versions VALUES (1,?,?,?,?)',
                       ('legacy-initial', fingerprint(data), raw, old[2]))
        db.execute('UPDATE sync_meta SET active=1 WHERE singleton=1')

    def changes(self, project_id, after=0, limit=20):
        if not isinstance(after, int) or after < 0 or not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ValueError('Invalid sync cursor')
        with closing(self._open(project_id)) as db:
            db.execute('BEGIN IMMEDIATE')
            self._activate(db)
            head = db.execute('SELECT COALESCE(MAX(revision),0) FROM sync_versions').fetchone()[0]
            rows = db.execute('''SELECT revision,change_id,content_hash,content_json,created_at
                FROM sync_versions WHERE revision>? ORDER BY revision LIMIT ?''', (after, limit)).fetchall()
            db.commit()
        items, total = [], 0
        for row in rows:
            size = len(row[3].encode('utf-8'))
            if items and total + size > MAX_BYTES:
                break
            items.append({'revision': row[0], 'changeId': row[1], 'hash': row[2],
                          'data': json.loads(row[3]), 'createdAt': row[4]})
            total += size
        return {'headVersion': head, 'changes': items,
                'nextVersion': items[-1]['revision'] if items else after,
                'hasMore': bool(items and items[-1]['revision'] < head)}

    def conflicts(self, project_id):
        with closing(self._open(project_id)) as db:
            rows = db.execute('''SELECT id,change_id,base_revision,head_revision,created_at
                FROM sync_conflicts WHERE resolved_at IS NULL ORDER BY id DESC LIMIT 100''').fetchall()
        return [{'id': row[0], 'changeId': row[1], 'baseRevision': row[2],
                 'headRevision': row[3], 'createdAt': row[4]} for row in rows]

    def head(self, project_id):
        with closing(self._open(project_id)) as db:
            return db.execute('SELECT COALESCE(MAX(revision),0) FROM sync_versions').fetchone()[0]

    def conflict_detail(self, project_id, conflict_id):
        if type(conflict_id) is not int or conflict_id < 1:
            raise ValueError('Invalid conflict ID')
        with closing(self._open(project_id)) as db:
            row = db.execute('''SELECT change_id,base_revision,head_revision,content_json
                FROM sync_conflicts WHERE id=?''', (conflict_id,)).fetchone()
            current = db.execute('SELECT content_json FROM sync_versions ORDER BY revision DESC LIMIT 1').fetchone()
        if row is None or current is None:
            raise ValueError('Sync conflict not found')
        candidate = json.loads(row[3])
        candidate_available = isinstance(candidate, dict) and 'snapshot' in candidate
        local_items = entities(candidate) if candidate_available else {}
        cloud_items = entities(json.loads(current[0]))
        changed = []
        for key in (sorted(local_items.keys() | cloud_items.keys()) if candidate_available else ()):
            local, cloud = local_items.get(key), cloud_items.get(key)
            if local == cloud:
                continue
            def preview(value):
                rendered = encoded(value)
                return rendered[:2000]+('…' if len(rendered) > 2000 else '')
            changed.append({'item': key, 'local': preview(local), 'cloud': preview(cloud)})
            if len(changed) >= 100:
                break
        return {'changeId': row[0], 'baseRevision': row[1], 'headRevision': row[2],
                'differences': changed, 'candidateAvailable': candidate_available}

    def design_history(self, project_id, path=None, revision=None):
        return self._document_history(project_id, path, revision, design_only=True)

    def document_history(self, project_id, path=None, revision=None):
        return self._document_history(project_id, path, revision, design_only=False)

    def _document_history(self, project_id, path, revision, design_only):
        if path is not None and (not isinstance(path, str) or len(path) > 300 or
                                 path.startswith('/') or '\\' in path or '\x00' in path or
                                 '..' in Path(path).parts):
            if design_only:
                raise ValueError('Invalid design document path')
            raise ValueError('Invalid document path')
        if revision is not None and (type(revision) is not int or revision < 1):
            if design_only:
                raise ValueError('Invalid design revision')
            raise ValueError('Invalid document revision')
        with closing(self._open(project_id)) as db:
            rows = db.execute('SELECT revision,content_json,created_at FROM sync_versions ORDER BY revision').fetchall()
        documents = {}
        last_hash = {}
        for number, raw, stamp in rows:
            artifacts = json.loads(raw).get('artifacts', {})
            for name, content in artifacts.items():
                if not isinstance(content, str) or not name.endswith('.md'):
                    continue
                if design_only and 'design' not in Path(name).parts:
                    continue
                signature = hashlib.sha256(content.encode('utf-8')).hexdigest()
                if last_hash.get(name) == signature:
                    continue
                match = re.search(r'^id:\s*([a-z0-9-]+)\s*$', content, re.MULTILINE)
                documents.setdefault(name, []).append({'revision': number, 'hash': signature,
                    'id': match.group(1) if match else None, 'createdAt': stamp, 'content': content})
                last_hash[name] = signature
        if path is None:
            items = [{'path': name, 'id': versions[-1]['id'],
                      'latestRevision': versions[-1]['revision'], 'versionCount': len(versions)}
                     for name, versions in sorted(documents.items())]
            if design_only:
                items = items[:200]
            return {'documents': items}
        versions = documents.get(path, [])
        if not versions and not design_only:
            raise ValueError('云端没有这份文档：'+path)
        if revision is None:
            return {'path': path, 'versions': [{k: v for k, v in item.items() if k != 'content'} for item in versions]}
        item = next((item for item in versions if item['revision'] == revision), None)
        if item is None:
            if design_only:
                raise ValueError('Design document version not found')
            raise ValueError('Document version not found')
        return {'path': path, **item}

    def report_conflict(self, project_id, value):
        change_id, base, head = value.get('changeId'), value.get('baseRevision'), value.get('headRevision')
        if not isinstance(change_id, str) or not 1 <= len(change_id) <= 120 or type(base) is not int or type(head) is not int or base < 0 or head < base:
            raise ValueError('Invalid conflict report')
        candidate = value.get('data')
        if candidate is not None and (not isinstance(candidate, dict) or
                                      not isinstance(candidate.get('snapshot'), dict) or
                                      candidate['snapshot'].get('projectId') != project_id):
            raise ValueError('Invalid conflict candidate')
        raw = encoded(candidate) if candidate is not None else '{}'
        if len(raw.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Conflict candidate exceeds 8 MiB')
        with closing(self._open(project_id)) as db:
            db.execute('''INSERT OR IGNORE INTO sync_conflicts
                (change_id,base_revision,head_revision,content_hash,content_json,created_at)
                VALUES (?,?,?,?,?,?)''', (change_id, base, head,
                                        fingerprint(candidate) if candidate is not None else '', raw, utcnow()))
            db.commit()
        return {'recorded': True}

    def resolve_conflict(self, project_id, value):
        change_id = value.get('changeId')
        if not isinstance(change_id, str) or not 1 <= len(change_id) <= 120 or value.get('choice') != 'cloud':
            raise ValueError('Only a reviewed keep-cloud decision can dismiss a conflict')
        with closing(self._open(project_id)) as db:
            cursor = db.execute('''UPDATE sync_conflicts SET resolved_at=?
                WHERE change_id=? AND resolved_at IS NULL''', (utcnow(), change_id))
            existing = db.execute('SELECT id FROM sync_conflicts WHERE change_id=?', (change_id,)).fetchone()
            db.commit()
        if cursor.rowcount != 1 and existing is None:
            raise ValueError('Open cloud conflict not found')
        return {'resolved': True, 'changeId': change_id}

    def publish(self, project_id, value):
        if value.get('schemaVersion') != 2 or type(value.get('baseRevision')) is not int or value['baseRevision'] < 0:
            raise ValueError('Versioned sync requires schemaVersion 2 and baseRevision')
        change_id, data = value.get('changeId'), value.get('data')
        if not isinstance(change_id, str) or not 1 <= len(change_id) <= 120 or not isinstance(data, dict) or data.get('schemaVersion') != 1:
            raise ValueError('Invalid versioned change')
        snapshot, contexts = data.get('snapshot'), data.get('contexts')
        if not isinstance(snapshot, dict) or snapshot.get('projectId') != project_id or not isinstance(snapshot.get('roles'), list) or not isinstance(contexts, dict):
            raise ValueError('Invalid project snapshot')
        data = dict(data)
        data['snapshot'] = dict(snapshot)
        data['snapshot'].pop('projectRootUri', None)
        artifacts = data.get('artifacts', {})
        if not isinstance(artifacts, dict) or len(artifacts) > 300:
            raise ValueError('Invalid governance artifacts')
        for path, content in artifacts.items():
            if (not isinstance(path, str) or not path or len(path) > 300 or path.startswith('/') or
                    '\\' in path or '\x00' in path or
                    '..' in Path(path).parts or not isinstance(content, str) or
                    len(content.encode('utf-8')) > 256 * 1024):
                raise ValueError('Invalid governance artifact path or content')
        raw = encoded(data)
        if len(raw.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Sync payload exceeds 8 MiB')
        signature = fingerprint(data)
        display = dict(data['snapshot'])
        if any(not isinstance(role, dict) for role in display['roles']):
            raise ValueError('Invalid role in snapshot')
        display['roles'] = [{**role, 'documents': {}} for role in display['roles']]
        with closing(self._open(project_id)) as db:
            db.execute('BEGIN IMMEDIATE')
            self._activate(db)
            previous = db.execute('SELECT revision,content_hash FROM sync_versions WHERE change_id=?', (change_id,)).fetchone()
            if previous:
                if previous[1] != signature:
                    raise ValueError('Change ID reused with different content')
                db.commit()
                return {'received': True, 'revision': previous[0], 'hash': signature}
            head = db.execute('SELECT COALESCE(MAX(revision),0) FROM sync_versions').fetchone()[0]
            if value['baseRevision'] != head:
                db.execute('''INSERT OR IGNORE INTO sync_conflicts
                    (change_id,base_revision,head_revision,content_hash,content_json,created_at)
                    VALUES (?,?,?,?,?,?)''', (change_id, value['baseRevision'], head, signature, raw, utcnow()))
                db.commit()
                return {'conflict': True, 'headVersion': head, 'baseRevision': value['baseRevision']}
            stamp, revision = utcnow(), head + 1
            db.execute('INSERT INTO sync_versions VALUES (?,?,?,?,?)', (revision, change_id, signature, raw, stamp))
            db.execute('UPDATE sync_conflicts SET resolved_at=? WHERE change_id=?', (stamp, change_id))
            display['sampledAt'] = stamp
            db.execute('''INSERT OR REPLACE INTO projection
                (singleton,snapshot_json,contexts_json,received_at) VALUES (1,?,?,?)''',
                       (json.dumps(display, ensure_ascii=False), json.dumps(contexts, ensure_ascii=False), stamp))
            db.commit()
        with self.cloud.connection() as global_db:
            global_db.execute('UPDATE projects SET last_received_at=? WHERE id=?', (stamp, project_id))
        return {'received': True, 'revision': revision, 'hash': signature}


class LocalReplica:
    """Untracked SQLite copy and journal; never contains the project Key."""
    def __init__(self, root, project_id):
        root = Path(root).expanduser().resolve()
        if not root.is_dir() or not PROJECT_ID.fullmatch(project_id):
            raise ValueError('Invalid local project')
        folder = root/'.ans'
        if folder.is_symlink():
            raise ValueError('Local state directory must not be a symlink')
        folder.mkdir(mode=0o700, exist_ok=True)
        self.path = folder/'project.sqlite3'
        if self.path.is_symlink():
            raise ValueError('Local replica must not be a symlink')
        self._ignore_git(root)
        created = not self.path.exists()
        with closing(sqlite3.connect(self.path, timeout=5)) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS meta (
                    singleton INTEGER PRIMARY KEY CHECK(singleton=1), project_id TEXT NOT NULL,
                    server_version INTEGER NOT NULL DEFAULT 0, observed_hash TEXT NOT NULL DEFAULT '',
                    cloud_hash TEXT NOT NULL DEFAULT '');
                CREATE TABLE IF NOT EXISTS local_changes (
                    id INTEGER PRIMARY KEY, change_id TEXT NOT NULL UNIQUE,
                    content_hash TEXT NOT NULL, content_json TEXT NOT NULL,
                    status TEXT NOT NULL CHECK(status IN ('ready','acked','conflict')));
                CREATE TABLE IF NOT EXISTS cloud_changes (
                    revision INTEGER PRIMARY KEY, change_id TEXT NOT NULL UNIQUE,
                    content_hash TEXT NOT NULL, content_json TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS conflicts (
                    id INTEGER PRIMARY KEY, change_id TEXT NOT NULL UNIQUE,
                    base_revision INTEGER NOT NULL, head_revision INTEGER NOT NULL,
                    reported INTEGER NOT NULL DEFAULT 0, resolved INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS entity_changes (
                    id INTEGER PRIMARY KEY, change_id TEXT NOT NULL,
                    entity_key TEXT NOT NULL, before_hash TEXT, after_hash TEXT,
                    after_json TEXT, FOREIGN KEY(change_id) REFERENCES local_changes(change_id));
                CREATE TABLE IF NOT EXISTS channel_events (
                    seq INTEGER PRIMARY KEY, content_json TEXT NOT NULL);
            ''')
            columns = {row[1] for row in db.execute('PRAGMA table_info(conflicts)')}
            if 'resolved' not in columns:
                db.execute('ALTER TABLE conflicts ADD COLUMN resolved INTEGER NOT NULL DEFAULT 0')
            db.execute('INSERT OR IGNORE INTO meta(singleton,project_id) VALUES (1,?)', (project_id,))
            if db.execute('SELECT project_id FROM meta WHERE singleton=1').fetchone()[0] != project_id:
                raise ValueError('Local SQLite belongs to a different project')
            db.commit()
        if created:
            os.chmod(self.path, 0o600)

    def _ignore_git(self, root):
        result = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                                capture_output=True, text=True, check=False)
        if result.returncode:
            return
        repository = Path(result.stdout.strip()).resolve()
        relative = self.path.relative_to(repository).as_posix()
        if subprocess.run(['git', '-C', str(repository), 'ls-files', '--error-unmatch', '--', relative],
                          capture_output=True, check=False).returncode == 0:
            raise ValueError('Local sync database must not be tracked by Git')
        info = subprocess.run(['git', '-C', str(repository), 'rev-parse', '--git-path', 'info/exclude'],
                              capture_output=True, text=True, check=True).stdout.strip()
        exclude = Path(info)
        if not exclude.is_absolute():
            exclude = repository/exclude
        exclude.parent.mkdir(parents=True, exist_ok=True)
        old = exclude.read_text(encoding='utf-8') if exclude.exists() else ''
        rule = '/'+relative+'*'
        if rule not in old.splitlines():
            with exclude.open('a', encoding='utf-8') as output:
                output.write(('' if not old or old.endswith('\n') else '\n')+rule+'\n')

    def _db(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.execute('PRAGMA busy_timeout=5000')
        return db

    def state(self):
        with closing(self._db()) as db:
            version, observed, cloud = db.execute('SELECT server_version,observed_hash,cloud_hash FROM meta').fetchone()
            pending = db.execute("SELECT COUNT(*) FROM local_changes WHERE status='ready'").fetchone()[0]
            conflicts = db.execute('SELECT COUNT(*) FROM conflicts WHERE resolved=0').fetchone()[0]
            channel_seq = db.execute('SELECT COALESCE(MAX(seq),0) FROM channel_events').fetchone()[0]
        return {'serverVersion': version, 'observedHash': observed, 'cloudHash': cloud,
                'pending': pending, 'conflicts': conflicts, 'channelSequence': channel_seq}

    def latest_cloud(self):
        with closing(self._db()) as db:
            row = db.execute('SELECT revision,content_json FROM cloud_changes ORDER BY revision DESC LIMIT 1').fetchone()
        return {'revision': row[0], 'data': json.loads(row[1])} if row else None

    def pull_channel(self, result):
        with closing(self._db()) as db:
            cursor = db.execute('SELECT COALESCE(MAX(seq),0) FROM channel_events').fetchone()[0]
            for change in result.get('changes', []):
                event = change.get('event')
                seq = event.get('seq') if isinstance(event, dict) else None
                if type(seq) is not int or seq != cursor + 1:
                    raise ValueError('Cloud channel event sequence is invalid')
                db.execute('INSERT INTO channel_events VALUES (?,?)', (seq, encoded(change)))
                cursor = seq
            db.commit()

    def channel_history(self, after=0):
        with closing(self._db()) as db:
            rows = db.execute('SELECT content_json FROM channel_events WHERE seq>? ORDER BY seq', (after,)).fetchall()
        return [json.loads(row[0]) for row in rows]

    def observe(self, value):
        raw, signature = encoded(value), fingerprint(value)
        if len(raw.encode('utf-8')) > MAX_BYTES:
            raise ValueError('Local sync snapshot exceeds 8 MiB')
        with closing(self._db()) as db:
            version, previous, cloud = db.execute('SELECT server_version,observed_hash,cloud_hash FROM meta').fetchone()
            if signature == previous:
                return False
            change_id = uuid.uuid4().hex
            conflict = bool(previous and cloud and cloud not in (previous, signature))
            previous_row = db.execute('SELECT content_json FROM local_changes ORDER BY id DESC LIMIT 1').fetchone()
            previous_entities = entities(json.loads(previous_row[0])) if previous_row else {}
            current_entities = entities(value)
            db.execute('INSERT INTO local_changes(change_id,content_hash,content_json,status) VALUES (?,?,?,?)',
                       (change_id, signature, raw, 'conflict' if conflict else 'ready'))
            for key in sorted(previous_entities.keys() | current_entities.keys()):
                before, after = previous_entities.get(key), current_entities.get(key)
                if before == after:
                    continue
                db.execute('''INSERT INTO entity_changes
                    (change_id,entity_key,before_hash,after_hash,after_json) VALUES (?,?,?,?,?)''',
                    (change_id, key, fingerprint(before) if key in previous_entities else None,
                     fingerprint(after) if key in current_entities else None,
                     encoded(after) if key in current_entities else None))
            if conflict:
                db.execute('INSERT INTO conflicts(change_id,base_revision,head_revision) VALUES (?,?,?)',
                           (change_id, version, version))
            db.execute('UPDATE meta SET observed_hash=? WHERE singleton=1', (signature,))
            db.commit()
        return True

    def entity_history(self, entity_key=None):
        with closing(self._db()) as db:
            rows = db.execute('''SELECT change_id,entity_key,before_hash,after_hash,after_json
                FROM entity_changes WHERE (? IS NULL OR entity_key=?) ORDER BY id''',
                (entity_key, entity_key)).fetchall()
        return [{'changeId': row[0], 'entityKey': row[1], 'beforeHash': row[2],
                 'afterHash': row[3], 'after': json.loads(row[4]) if row[4] is not None else None}
                for row in rows]

    def pending(self):
        with closing(self._db()) as db:
            row = db.execute("SELECT change_id,content_hash,content_json FROM local_changes WHERE status='ready' ORDER BY id LIMIT 1").fetchone()
        return {'changeId': row[0], 'hash': row[1], 'data': json.loads(row[2])} if row else None

    def pull(self, result):
        with closing(self._db()) as db:
            version = db.execute('SELECT server_version FROM meta').fetchone()[0]
            for item in result.get('changes', []):
                if item['revision'] <= version:
                    continue
                if item['revision'] != version + 1 or fingerprint(item['data']) != item['hash']:
                    raise ValueError('Cloud change sequence or hash is invalid')
                db.execute('INSERT INTO cloud_changes VALUES (?,?,?,?)',
                           (item['revision'], item['changeId'], item['hash'], encoded(item['data'])))
                rows = db.execute("SELECT change_id,content_hash FROM local_changes WHERE status='ready'").fetchall()
                for change_id, local_hash in rows:
                    if local_hash == item['hash']:
                        db.execute("UPDATE local_changes SET status='acked' WHERE change_id=?", (change_id,))
                    elif item['changeId'] != 'legacy-initial':
                        db.execute("UPDATE local_changes SET status='conflict' WHERE change_id=?", (change_id,))
                        db.execute('''INSERT OR IGNORE INTO conflicts(change_id,base_revision,head_revision)
                            VALUES (?,?,?)''', (change_id, version, item['revision']))
                db.execute('UPDATE meta SET server_version=?,cloud_hash=? WHERE singleton=1',
                           (item['revision'], item['hash']))
                version = item['revision']
            db.commit()

    def ack(self, change, result):
        with closing(self._db()) as db:
            if result['hash'] != change['hash']:
                raise ValueError('Cloud acknowledgment hash mismatch')
            db.execute("UPDATE local_changes SET status='acked' WHERE change_id=?", (change['changeId'],))
            db.execute('''INSERT OR IGNORE INTO cloud_changes
                (revision,change_id,content_hash,content_json) VALUES (?,?,?,?)''',
                (result['revision'], change['changeId'], change['hash'], encoded(change['data'])))
            db.execute('UPDATE meta SET server_version=?,cloud_hash=? WHERE singleton=1',
                       (result['revision'], result['hash']))
            db.commit()

    def conflict(self, change, head):
        with closing(self._db()) as db:
            version = db.execute('SELECT server_version FROM meta').fetchone()[0]
            db.execute("UPDATE local_changes SET status='conflict' WHERE change_id=?", (change['changeId'],))
            db.execute('''INSERT OR IGNORE INTO conflicts(change_id,base_revision,head_revision)
                VALUES (?,?,?)''', (change['changeId'], version, head))
            db.commit()

    def unreported(self):
        with closing(self._db()) as db:
            rows = db.execute('''SELECT c.id,c.change_id,c.base_revision,c.head_revision,l.content_json
                FROM conflicts c LEFT JOIN local_changes l ON l.change_id=c.change_id
                WHERE c.reported=0 AND c.resolved=0 ORDER BY c.id''').fetchall()
        return [{'id': row[0], 'changeId': row[1], 'baseRevision': row[2],
                 'headRevision': row[3], 'data': json.loads(row[4]) if row[4] else None}
                for row in rows]

    def mark_reported(self, conflict_id):
        with closing(self._db()) as db:
            db.execute('UPDATE conflicts SET reported=1 WHERE id=?', (conflict_id,))
            db.commit()

    def resolve(self, change_id, choice, current_payload=None):
        if choice not in ('local', 'cloud'):
            raise ValueError('Conflict choice must be local or cloud')
        with closing(self._db()) as db:
            row = db.execute('''SELECT c.resolved,l.content_hash FROM conflicts c
                JOIN local_changes l ON l.change_id=c.change_id WHERE c.change_id=?''', (change_id,)).fetchone()
            if row is None or row[0]:
                raise ValueError('Open conflict not found')
            if choice == 'cloud':
                cloud_hash = db.execute('SELECT cloud_hash FROM meta').fetchone()[0]
                if current_payload is None or fingerprint(current_payload) != cloud_hash:
                    raise ValueError('Local project files do not match the chosen cloud version')
            db.execute('UPDATE conflicts SET resolved=1 WHERE change_id=?', (change_id,))
            db.execute('UPDATE local_changes SET status=? WHERE change_id=?',
                       ('ready' if choice == 'local' else 'acked', change_id))
            if choice == 'cloud':
                db.execute('UPDATE meta SET observed_hash=cloud_hash WHERE singleton=1')
            db.commit()


def capture(root, project_id, document_roots=None):
    from .sync import projection
    root = Path(root).expanduser().resolve()
    if document_roots is None:
        config = load_project_config(root, project_id)
        document_roots = []
        if config is not None:
            document_roots = config.get('documentRoots', [])
    configured_directories = resolve_document_roots(root, document_roots)
    value = projection(root, project_id)
    value['snapshot'].pop('projectRootUri', None)
    value['snapshot'].pop('sampledAt', None)
    artifacts, total = {}, 0
    parents = [(root/name, False) for name in ('角色卡', 'role-cards', 'doc', 'docs')]
    parents.extend((directory, True) for directory in configured_directories)
    for parent, configured in parents:
        if not parent.is_dir() or parent.is_symlink():
            continue
        for path in sorted(parent.rglob('*')):
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root):
                continue
            relative = path.relative_to(root)
            name = relative.as_posix()
            if name in artifacts:
                continue
            if configured:
                if path.suffix != '.md':
                    continue
            elif path.name not in ('role-card.md', 'boundary.md', 'functional-description.md', 'api-spec.md', 'changelog.md') and not (path.suffix in ('.md', '.json', '.jsonl') and any(part in ('design','feature','change','fix','scheduling') for part in relative.parts)):
                continue
            if len(artifacts) >= 300:
                raise ValueError('Document count exceeds 300; next document: '+name)
            if path.stat().st_size > 256 * 1024:
                raise ValueError('Document exceeds 256 KiB: '+name)
            text = path.read_text(encoding='utf-8')
            total += len(text.encode('utf-8'))
            if total > 4 * 1024 * 1024:
                raise ValueError('Governance documents exceed 4 MiB; document: '+name)
            artifacts[name] = text
    value['artifacts'] = artifacts
    return value


def request(server_url, project_id, token, action, value=None):
    parsed = urlparse(server_url)
    if not PROJECT_ID.fullmatch(project_id) or not parsed.netloc or parsed.username or parsed.password or parsed.params or parsed.query or parsed.fragment:
        raise ValueError('Invalid server URL or project ID')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost','127.0.0.1')):
        raise ValueError('Sync requires HTTPS')
    endpoint, _, query = action.partition('?')
    if not endpoint or any(not part or any(not (c.isalnum() or c == '-') for c in part)
                           for part in endpoint.split('/')):
        raise ValueError('Invalid sync endpoint')
    url = parsed._replace(path=normalize_base_path(parsed.path)+'/p/'+project_id+'/api/'+endpoint,
                          params='', query=query, fragment='').geturl()
    data = None if value is None else json.dumps(value, ensure_ascii=False).encode('utf-8')
    headers = {'Authorization': 'Bearer '+token}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    call = Request(url, data=data, headers=headers, method='GET' if data is None else 'POST')
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None
    try:
        with build_opener(NoRedirect).open(call, timeout=20) as response:
            return json.load(response)
    except HTTPError as error:
        if error.code == 409:
            return json.load(error)
        raise


def synchronize(root, project_id, server_url, token, local, pull_only=False):
    local.observe(capture(root, project_id))
    while True:
        batch = request(server_url, project_id, token,
                        'changes?after='+str(local.state()['serverVersion'])+'&limit=20')
        local.pull(batch)
        if not batch['hasMore']:
            break
    while True:
        batch = request(server_url, project_id, token,
                        'channel/changes?after='+str(local.state()['channelSequence'])+'&limit=50')
        local.pull_channel(batch)
        if not batch['hasMore']:
            break
    for conflict in local.unreported():
        request(server_url, project_id, token, 'conflict-report', conflict)
        local.mark_reported(conflict['id'])
        print('同步冲突：'+conflict['changeId']+'，请客户在 Dashboard 查看并决定如何合并。',
              file=sys.stderr, flush=True)
    if local.state()['conflicts']:
        return {'status': 'conflict', **local.state()}
    if pull_only:
        return {'status': 'pulled', **local.state()}
    sent = 0
    while change := local.pending():
        result = request(server_url, project_id, token, 'sync-v2',
                         {'schemaVersion': 2, 'baseRevision': local.state()['serverVersion'],
                          'changeId': change['changeId'], 'data': change['data']})
        if result.get('conflict'):
            local.conflict(change, result['headVersion'])
            for conflict in local.unreported():
                request(server_url, project_id, token, 'conflict-report', conflict)
                local.mark_reported(conflict['id'])
                print('同步冲突：'+conflict['changeId']+'，请客户在 Dashboard 查看并决定如何合并。',
                      file=sys.stderr, flush=True)
            return {'status': 'conflict', **local.state()}
        local.ack(change, result)
        sent += 1
    return {'status': 'synced', 'sent': sent, **local.state()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--interval', type=float, help='Opt in to periodic sync; default runs once')
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--pull-only', action='store_true', help='Download cloud changes without uploading')
    parser.add_argument('--status', action='store_true')
    parser.add_argument('--record', action='store_true', help='Journal the current completed local management change')
    parser.add_argument('--resolve', metavar='CHANGE_ID')
    parser.add_argument('--choice', choices=('local', 'cloud'))
    parser.add_argument('--design-list', action='store_true')
    parser.add_argument('--design-path')
    parser.add_argument('--design-revision', type=int)
    parser.add_argument('--document-list', action='store_true')
    parser.add_argument('--document-path')
    parser.add_argument('--document-revision', type=int)
    parser.add_argument('--remote-summary', action='store_true')
    parser.add_argument('--remote-artifact')
    parser.add_argument('--remote-context')
    parser.add_argument('--local-history', metavar='ENTITY_KEY')
    parser.add_argument('--channel-after', type=int, metavar='SEQ')
    args = parser.parse_args(argv)
    if args.document_revision is not None:
        if not args.document_path or args.document_revision < 1:
            parser.error('--document-revision requires --document-path and a positive version')
    if (args.document_list or args.document_path) and (args.design_list or args.design_path):
        parser.error('Use either document history or design history in one command')
    root = args.root.expanduser().resolve()
    if args.status:
        print(json.dumps(sync_status(root), ensure_ascii=False))
        return 0
    try:
        config = load_project_config(root)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if config is None:
        parser.error('Project cloud configuration is missing')
    if args.interval is not None and not 2 <= args.interval <= 3600:
        parser.error('--interval must be between 2 and 3600 seconds')
    try:
        local = LocalReplica(root, config['projectId'])
    except (OSError, ValueError) as error:
        parser.error(str(error))
    if args.local_history:
        print(json.dumps({'changes': local.entity_history(args.local_history)}, ensure_ascii=False, indent=2))
        return 0
    if args.channel_after is not None:
        if args.channel_after < 0:
            parser.error('--channel-after must be nonnegative')
        print(json.dumps({'changes': local.channel_history(args.channel_after)}, ensure_ascii=False, indent=2))
        return 0
    if args.record:
        try:
            changed = local.observe(capture(root, config['projectId']))
        except (OSError, ValueError) as error:
            parser.error(str(error))
        print(json.dumps({'recorded': changed, **local.state()}, ensure_ascii=False))
        return 0
    if args.remote_summary or args.remote_artifact or args.remote_context:
        latest = local.latest_cloud()
        if latest is None:
            parser.error('No cloud version has been pulled yet')
        if args.remote_artifact:
            content = latest['data'].get('artifacts', {}).get(args.remote_artifact)
            if content is None:
                parser.error('Cloud artifact not found')
            print(content, end='' if content.endswith('\n') else '\n')
        elif args.remote_context:
            content = latest['data'].get('contexts', {}).get(args.remote_context)
            if content is None:
                parser.error('Cloud role context not found')
            print(json.dumps({'revision': latest['revision'], 'context': content}, ensure_ascii=False, indent=2))
        else:
            data = latest['data']
            print(json.dumps({'revision': latest['revision'],
                              'roles': [role.get('id') for role in data['snapshot'].get('roles', [])],
                              'artifacts': sorted(data.get('artifacts', {})),
                              'contextRoles': sorted(data.get('contexts', {}))}, ensure_ascii=False, indent=2))
        return 0
    if args.design_list or args.design_path or args.document_list or args.document_path:
        if args.document_list or args.document_path:
            action = 'document-history'
            path, revision = args.document_path, args.document_revision
        else:
            action = 'design-docs'
            path, revision = args.design_path, args.design_revision
        if path:
            action += '?path='+quote(path, safe='')
            if revision is not None:
                action += '&revision='+str(revision)
        try:
            print(json.dumps(request(config['serverUrl'], config['projectId'],
                                     config['projectKey'], action), ensure_ascii=False, indent=2))
            return 0
        except HTTPError as error:
            try:
                detail = json.load(error)
            except (OSError, ValueError) as detail_error:
                print(str(error)+'; '+str(detail_error), file=sys.stderr)
            else:
                print(detail.get('error', str(error)), file=sys.stderr)
            return 2
        except (OSError, ValueError, URLError) as error:
            print(str(error), file=sys.stderr)
            return 2
    if args.resolve:
        if not args.choice:
            parser.error('--resolve requires --choice local or cloud')
        try:
            current = capture(root, config['projectId']) if args.choice == 'cloud' else None
            if args.choice == 'cloud':
                if fingerprint(current) != local.state()['cloudHash']:
                    raise ValueError('Local project files do not match the chosen cloud version')
                request(config['serverUrl'], config['projectId'], config['projectKey'],
                        'conflict-resolve', {'changeId': args.resolve, 'choice': 'cloud'})
            local.resolve(args.resolve, args.choice, current)
            print(json.dumps({'resolved': args.resolve, 'choice': args.choice}, ensure_ascii=False))
            return 0
        except (OSError, ValueError, URLError) as error:
            print(str(error), file=sys.stderr)
            return 2
    try:
        with SyncLease(root, config['projectId'], None if args.once else args.interval) as lease:
            while True:
                try:
                    result = synchronize(root, config['projectId'], config['serverUrl'],
                                         config['projectKey'], local, pull_only=args.pull_only)
                    lease.success()
                    print(json.dumps(result, ensure_ascii=False), flush=True)
                except HTTPError as error:
                    lease.failure(error)
                    if 400 <= error.code < 500 and error.code not in (408, 429):
                        print('Cloud sync stopped: HTTP '+str(error.code), file=sys.stderr)
                        return 2
                    print('Cloud sync HTTP '+str(error.code)+'; retrying', file=sys.stderr)
                    if args.once or args.interval is None:
                        return 2
                except (URLError, OSError) as error:
                    lease.failure(error)
                    print('Cloud sync unavailable; retrying', file=sys.stderr, flush=True)
                    if args.once or args.interval is None:
                        return 2
                if args.once or args.interval is None:
                    return 0
                time.sleep(args.interval)
    except (SyncAlreadyRunning, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
