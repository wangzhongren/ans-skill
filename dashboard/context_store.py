#!/usr/bin/env python3
"""One project SQLite store for role-filtered project understanding and AI CRUD."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

CATEGORIES = ('flows', 'definitions', 'events', 'interfaces', 'data')
TOPIC_ID = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
SCHEMA_VERSION = 7
SCHEMA = '''
PRAGMA foreign_keys=ON;
CREATE TABLE meta (schema_version INTEGER NOT NULL);
CREATE TABLE overview (role_id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT NOT NULL, revision INTEGER NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE overview_steps (role_id TEXT NOT NULL REFERENCES overview(role_id) ON DELETE CASCADE, position INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, ref TEXT NOT NULL, PRIMARY KEY(role_id,position));
CREATE TABLE overview_step_links (role_id TEXT NOT NULL, step_position INTEGER NOT NULL, position INTEGER NOT NULL, target_topic_id TEXT NOT NULL, PRIMARY KEY(role_id,step_position,position), FOREIGN KEY(role_id,step_position) REFERENCES overview_steps(role_id,position) ON DELETE CASCADE, FOREIGN KEY(role_id,target_topic_id) REFERENCES topics(role_id,topic_id));
CREATE TABLE category_summaries (role_id TEXT NOT NULL REFERENCES overview(role_id) ON DELETE CASCADE, category TEXT NOT NULL CHECK(category IN ('flows','definitions','events','interfaces','data')), summary TEXT NOT NULL, revision INTEGER NOT NULL, updated_at TEXT NOT NULL, PRIMARY KEY(role_id,category));
CREATE TABLE topics (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, category TEXT NOT NULL CHECK(category IN ('flows','definitions','events','interfaces','data')), title TEXT NOT NULL, summary TEXT NOT NULL, details TEXT NOT NULL, revision INTEGER NOT NULL, updated_at TEXT NOT NULL, deleted_at TEXT, PRIMARY KEY(role_id,topic_id));
CREATE TABLE topic_refs (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, ref TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE topic_links (role_id TEXT NOT NULL, source_topic_id TEXT NOT NULL, position INTEGER NOT NULL, target_topic_id TEXT NOT NULL, PRIMARY KEY(role_id,source_topic_id,position), FOREIGN KEY(role_id,source_topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE, FOREIGN KEY(role_id,target_topic_id) REFERENCES topics(role_id,topic_id));
CREATE TABLE event_definitions (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, occurrence TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE flow_steps (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, ref TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE flow_relations (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('triggered_by','emits','input','output','interface')), position INTEGER NOT NULL, target_topic_id TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,kind,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE, FOREIGN KEY(role_id,target_topic_id) REFERENCES topics(role_id,topic_id));
CREATE TABLE flow_trigger_conditions (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, when_text TEXT NOT NULL, source_flow_id TEXT, ref TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE, FOREIGN KEY(role_id,source_flow_id) REFERENCES topics(role_id,topic_id));
CREATE TABLE flow_graphs (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, graph_json TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE flow_intents (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, purpose TEXT NOT NULL, success TEXT NOT NULL, failure TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE data_schemas (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, owner TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE interface_specs (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, entry TEXT NOT NULL, method TEXT NOT NULL, request_url TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('network','internal')), protocol TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
CREATE TABLE topic_fields (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, section TEXT NOT NULL CHECK(section IN ('data','input','output')), position INTEGER NOT NULL, name TEXT NOT NULL, field_type TEXT NOT NULL, description TEXT NOT NULL, required INTEGER NOT NULL CHECK(required IN (0,1)), PRIMARY KEY(role_id,topic_id,section,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE);
'''


def now():
    return datetime.now(timezone.utc).isoformat()


def required_text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name+' must be nonempty text')
    return value.strip()


def optional_text(value, name):
    if not isinstance(value, str):
        raise ValueError(name+' must be text')
    return value.strip()


def refs(value):
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError('refs must be an array of nonempty strings')
    return [item.strip() for item in value]


def links(value):
    if not isinstance(value, list) or any(not isinstance(item, str) or not TOPIC_ID.fullmatch(item) for item in value):
        raise ValueError('links must be an array of topic IDs')
    if len(set(value)) != len(value):
        raise ValueError('links must not repeat a topic ID')
    return value


def overview_input(value):
    if not isinstance(value, dict):
        raise ValueError('Overview input must be an object')
    steps = value.get('steps', [])
    if not isinstance(steps, list):
        raise ValueError('steps must be an array')
    cleaned = []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Each step must be an object')
        cleaned.append({'title': required_text(step.get('title'), 'step title'),
                        'description': optional_text(step.get('description', ''), 'step description'),
                        'ref': optional_text(step.get('ref', ''), 'step ref'),
                        'links': links(step.get('links', []))})
    return {'title': required_text(value.get('title'), 'title'),
            'summary': optional_text(value.get('summary'), 'summary'), 'steps': cleaned}


FLOW_RELATIONS = {'triggeredBy': ('triggered_by', 'events'), 'emits': ('emits', 'events'),
                  'inputs': ('input', 'data'), 'outputs': ('output', 'data'), 'interfaces': ('interface', 'interfaces')}


def flow_intent_input(value):
    if not isinstance(value, dict):
        raise ValueError('flow.intent 要说明这条流程做什么、成功后怎样')
    purpose = required_text(value.get('purpose'), 'flow.intent.purpose')
    success = required_text(value.get('success'), 'flow.intent.success')
    failure = optional_text(value.get('failure', ''), 'flow.intent.failure')
    if any(len(text) > 500 for text in (purpose, success, failure)):
        raise ValueError('流程用途或结果不能超过 500 字')
    return {'purpose': purpose, 'success': success, 'failure': failure}


def graph_input(value):
    if not isinstance(value, dict):
        raise ValueError('flow.graph 必须是流程图对象')
    nodes, edges = value.get('nodes'), value.get('edges')
    if not isinstance(nodes, list) or not 2 <= len(nodes) <= 60:
        raise ValueError('流程图需要 2–60 个节点')
    if not isinstance(edges, list) or not 1 <= len(edges) <= 120:
        raise ValueError('流程图需要 1–120 条连线')
    cleaned_nodes, kinds = [], {}
    for node in nodes:
        if not isinstance(node, dict) or not isinstance(node.get('id'), str) or not TOPIC_ID.fullmatch(node['id']):
            raise ValueError('节点 id 只能用小写字母、数字和短横线，例如 check-input')
        node_id = node['id']
        if node_id in kinds:
            raise ValueError('节点 id 重复：'+node_id)
        kind = node.get('kind')
        if kind not in ('start', 'action', 'decision', 'end', 'error'):
            raise ValueError('节点类型只能是 start、action、decision、end 或 error')
        title = required_text(node.get('title'), 'graph node title')
        description = optional_text(node.get('description', ''), 'graph node description')
        ref = optional_text(node.get('ref', ''), 'graph node ref')
        checks = node.get('checks', [])
        if not isinstance(checks, list) or len(checks) > 10:
            raise ValueError('节点 checks 最多写 10 条排查方法')
        checks = [required_text(check, 'graph node check') for check in checks]
        if kind in ('decision', 'error') and not ref:
            raise ValueError('判断和异常节点要写代码位置 ref')
        if kind in ('end', 'error') and not description:
            raise ValueError('完成和异常节点要说明用户会看到什么结果')
        if kind == 'error' and not checks:
            raise ValueError('异常节点至少要写一条具体排查方法 checks')
        if any(len(text) > limit for text, limit in ((title, 120), (description, 1000), (ref, 300))):
            raise ValueError('流程图节点文字太长')
        if any(len(check) > 500 for check in checks):
            raise ValueError('一条排查方法不能超过 500 字')
        kinds[node_id] = kind
        cleaned_nodes.append({'id': node_id, 'kind': kind, 'title': title,
                              'description': description, 'ref': ref, 'checks': checks})
    starts = [node_id for node_id, kind in kinds.items() if kind == 'start']
    terminals = {node_id for node_id, kind in kinds.items() if kind in ('end', 'error')}
    if len(starts) != 1 or not terminals:
        raise ValueError('流程图必须有一个入口，以及至少一个完成或异常节点')
    outgoing = {node_id: [] for node_id in kinds}
    incoming = {node_id: [] for node_id in kinds}
    cleaned_edges, seen_edges = [], set()
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError('每条连线都要写 from 和 to')
        source, target = edge.get('from'), edge.get('to')
        if not isinstance(source, str) or not isinstance(target, str) or source not in kinds or target not in kinds or source == target:
            raise ValueError('连线的 from 和 to 必须是两个不同的现有节点')
        if source in terminals or target == starts[0]:
            raise ValueError('完成或异常节点不能继续向外连，其他节点也不能连回入口')
        condition = optional_text(edge.get('condition', ''), 'graph edge condition')
        if kinds[source] == 'decision' and not condition:
            raise ValueError('判断节点的每条分支都要写明条件 condition')
        if len(condition) > 300:
            raise ValueError('分支条件不能超过 300 字')
        identity = (source, target, condition)
        if identity in seen_edges:
            raise ValueError('流程图有重复连线')
        seen_edges.add(identity)
        outgoing[source].append((target, condition))
        incoming[target].append(source)
        cleaned_edges.append({'from': source, 'to': target, 'condition': condition})
    for node_id, kind in kinds.items():
        branches = outgoing[node_id]
        if kind in ('end', 'error') and branches:
            raise ValueError('完成或异常节点不能再连到下一步')
        if kind not in ('end', 'error') and not branches:
            raise ValueError('未结束的节点要连到下一步')
        if kind != 'decision' and len(branches) > 1:
            raise ValueError('只有判断节点可以分出多条路')
        if kind == 'decision' and (len(branches) < 2 or len({condition for _, condition in branches}) != len(branches)):
            raise ValueError('判断节点至少要有两条条件不同的分支')
    def reachable(seeds, neighbors):
        visited, queue = set(seeds), list(seeds)
        while queue:
            for target in neighbors(queue.pop(0)):
                if target not in visited:
                    visited.add(target)
                    queue.append(target)
        return visited
    from_start = reachable(starts, lambda node_id: [target for target, _ in outgoing[node_id]])
    to_terminal = reachable(terminals, lambda node_id: incoming[node_id])
    if from_start != set(kinds) or to_terminal != set(kinds):
        raise ValueError('每个节点都要能从入口走到，也要能走到完成或异常结果')
    return {'nodes': cleaned_nodes, 'edges': cleaned_edges}


def flow_input(value):
    if not isinstance(value, dict):
        raise ValueError('Flow topics require a flow object')
    graph = graph_input(value['graph']) if value.get('graph') is not None else None
    intent = flow_intent_input(value['intent']) if value.get('intent') is not None else None
    if graph is not None and intent is None:
        raise ValueError('有流程图时，请填写 flow.intent.purpose（做什么）和 success（成功后怎样）')
    steps = value.get('steps', [])
    if not isinstance(steps, list) or (not steps and graph is None):
        raise ValueError('流程至少要有文字步骤 steps 或流程图 graph')
    cleaned = []
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Flow step must be an object')
        cleaned.append({'title': required_text(step.get('title'), 'flow step title'),
                        'description': optional_text(step.get('description', ''), 'flow step description'),
                        'ref': optional_text(step.get('ref', ''), 'flow step ref')})
    triggers = value.get('triggers', [])
    if not isinstance(triggers, list):
        raise ValueError('Flow triggers must be an array')
    cleaned_triggers = []
    for trigger in triggers:
        if not isinstance(trigger, dict):
            raise ValueError('Flow trigger must be an object')
        source_flow = trigger.get('sourceFlow')
        if source_flow is not None and (not isinstance(source_flow, str) or not TOPIC_ID.fullmatch(source_flow)):
            raise ValueError('sourceFlow must be a flow topic ID')
        cleaned_triggers.append({'when': required_text(trigger.get('when'), 'flow trigger.when'),
                                 'sourceFlow': source_flow,
                                 'ref': optional_text(trigger.get('ref', ''), 'flow trigger.ref')})
    result = {'steps': cleaned, 'triggers': cleaned_triggers, 'graph': graph, 'intent': intent}
    for name in FLOW_RELATIONS:
        result[name] = links(value.get(name, []))
    if result['triggers'] and result['triggeredBy']:
        raise ValueError('Use direct flow triggers or legacy event links, not both')
    return result


def field_input(value):
    if not isinstance(value, list):
        raise ValueError('fields must be an array')
    cleaned = []
    names = set()
    for field in value:
        if not isinstance(field, dict):
            raise ValueError('Each field must be an object')
        name = required_text(field.get('name'), 'field name')
        if name in names:
            raise ValueError('Duplicate field name: '+name)
        names.add(name)
        required = field.get('required', False)
        if type(required) is not bool:
            raise ValueError('field required must be boolean')
        cleaned.append({'name': name, 'type': required_text(field.get('type'), 'field type'),
                        'description': optional_text(field.get('description', ''), 'field description'),
                        'required': required})
    return cleaned


def data_input(value):
    if not isinstance(value, dict):
        raise ValueError('Data topics require a data object')
    fields = field_input(value.get('fields'))
    if not fields:
        raise ValueError('Data topics require at least one field')
    return {'owner': required_text(value.get('owner'), 'data owner'), 'fields': fields}


def interface_input(value):
    if not isinstance(value, dict):
        raise ValueError('Interface topics require an interface object')
    inputs = field_input(value.get('inputs'))
    outputs = field_input(value.get('outputs'))
    if not inputs and not outputs:
        raise ValueError('Interface topics require input or output fields')
    method = optional_text(value.get('method', ''), 'HTTP method').upper()
    request_url = optional_text(value.get('requestUrl', ''), 'request URL')
    kind = value.get('kind', 'network' if request_url else 'internal')
    if kind not in ('network', 'internal'):
        raise ValueError('interface.kind must be network or internal')
    protocol = optional_text(value.get('protocol', ''), 'network protocol')
    if kind == 'network':
        if not request_url:
            raise ValueError('Network interfaces require requestUrl')
        if not protocol:
            protocol = 'HTTP' if method else 'Network'
        if protocol.upper() == 'HTTP' and not method:
            raise ValueError('HTTP interfaces require method')
    elif method or request_url or protocol:
        raise ValueError('Internal interfaces cannot have HTTP method, request URL, or network protocol')
    return {'entry': required_text(value.get('entry'), 'interface entry'),
            'kind': kind, 'protocol': protocol, 'method': method, 'requestUrl': request_url,
            'inputs': inputs, 'outputs': outputs}


def topic_input(value):
    if not isinstance(value, dict):
        raise ValueError('Topic input must be an object')
    category = value.get('category')
    if category not in CATEGORIES:
        raise ValueError('category must be one of '+', '.join(CATEGORIES))
    event = value.get('event')
    if category == 'events':
        if not isinstance(event, dict):
            raise ValueError('Event topics require an event definition')
        event = {'occurrence': required_text(event.get('occurrence'), 'event.occurrence')}
    elif event is not None:
        raise ValueError('Only event topics may define an occurrence')
    if value.get('trigger') is not None:
        raise ValueError('Use event.occurrence; flow relationships define what happens next')
    flow = value.get('flow')
    if category == 'flows':
        flow = flow_input(flow)
    elif flow is not None:
        raise ValueError('Only flow topics may define a flow')
    data = value.get('data')
    if category == 'data':
        data = data_input(data)
    elif data is not None:
        raise ValueError('Only data topics may define data fields')
    interface = value.get('interface')
    if category == 'interfaces':
        interface = interface_input(interface)
    elif interface is not None:
        raise ValueError('Only interface topics may define interface fields')
    title = required_text(value.get('title'), 'title')
    if category == 'flows' and flow['intent'] is not None and flow['intent']['purpose'] == title:
        raise ValueError('流程用途不能只重复标题；要写清用户想做什么和结果')
    summary_value = value.get('summary')
    if category == 'flows' and flow['intent'] is not None:
        summary_value = flow['intent']['purpose']
    summary = optional_text(summary_value, 'summary')
    if category == 'flows' and not summary:
        raise ValueError('请用一句话说明这条流程具体做什么')
    return {'category': category, 'title': title,
            'summary': summary,
            'details': optional_text(value.get('details', ''), 'details'),
            'refs': refs(value.get('refs', [])), 'links': links(value.get('links', [])),
            'event': event, 'flow': flow, 'data': data, 'interface': interface}


def category_input(value):
    if not isinstance(value, dict) or 'summary' not in value:
        raise ValueError('Category input requires summary')
    return value['summary']


class ContextStore:
    def __init__(self, root, role, roles=None):
        self.root = Path(root).resolve()
        self.roles = Path(roles) if roles else next((self.root/name for name in ('角色卡', 'role-cards') if (self.root/name).is_dir()), self.root/'角色卡')
        if not self.roles.is_absolute():
            self.roles = self.root/self.roles
        if self.roles.is_symlink() or not self.roles.resolve().is_relative_to(self.root):
            raise ValueError('Role directory must stay inside the project')
        self.roles = self.roles.resolve()
        if not isinstance(role, str) or not role or role in ('.', '..') or '/' in role or '\\' in role:
            raise ValueError('role must name one direct role folder')
        self.role = role
        self.role_dir = self.roles/role
        self.folder = self.root/'project-context'
        self.db = self.folder/'context.sqlite3'
        card = self.role_dir/'role-card.md'
        if self.role_dir.is_symlink() or card.is_symlink() or not card.is_file():
            raise ValueError('Role card not found in a direct role folder')
        if self.folder.is_symlink() or self.db.is_symlink():
            raise ValueError('Symlinked context paths are not allowed')

    def role_metadata(self):
        card = self.role_dir/'role-card.md'
        purpose = next((line.strip() for line in card.read_text(encoding='utf-8').splitlines()
                        if line.strip() and not line.lstrip().startswith(('#', '-', '|', '```'))), '')
        boundary = self.role_dir/'boundary.md'
        paths = []
        if boundary.is_file():
            if boundary.is_symlink():
                raise ValueError('Symlinked role boundary is not readable')
            for line in boundary.read_text(encoding='utf-8').splitlines():
                if not line.lstrip().startswith('|'):
                    continue
                match = re.search(r'`([^`]+)`', line)
                if match and match.group(1) not in paths:
                    paths.append(match.group(1))
        return {'purpose': purpose, 'boundaryPaths': paths}

    @contextmanager
    def connection(self, readonly=True):
        if not self.db.is_file() or self.db.is_symlink():
            raise FileNotFoundError('Project context database is not initialized')
        connection = sqlite3.connect(self.db.as_uri()+'?mode=ro', uri=True, timeout=5) if readonly else sqlite3.connect(self.db, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('PRAGMA busy_timeout=5000')
            meta = connection.execute('SELECT schema_version FROM meta').fetchall()
            if len(meta) != 1 or meta[0]['schema_version'] not in (6, SCHEMA_VERSION):
                raise ValueError('Context database schema mismatch; run the authorized migrate command')
            yield connection
            if not readonly:
                connection.commit()
        except Exception:
            if not readonly:
                connection.rollback()
            raise
        finally:
            connection.close()

    def migrate(self):
        if not self.db.is_file() or self.db.is_symlink():
            raise FileNotFoundError('Project context database is not initialized')
        connection = sqlite3.connect(self.db, timeout=5)
        try:
            connection.row_factory = sqlite3.Row
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('BEGIN IMMEDIATE')
            meta = connection.execute('SELECT schema_version FROM meta').fetchall()
            if len(meta) != 1:
                raise ValueError('Invalid context database metadata')
            version = meta[0]['schema_version']
            if version == SCHEMA_VERSION:
                connection.commit()
                return {'schemaVersion': version, 'changed': False}
            if version not in (1, 2, 3, 4, 5, 6):
                raise ValueError('Unsupported context database schema')
            if version == 1:
                connection.execute('CREATE TABLE event_triggers (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, when_text TEXT NOT NULL, action_text TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute('CREATE TABLE event_trigger_consumers (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, consumer TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES event_triggers(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute('CREATE TABLE flow_steps (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, title TEXT NOT NULL, description TEXT NOT NULL, ref TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute("CREATE TABLE flow_relations (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, kind TEXT NOT NULL CHECK(kind IN ('triggered_by','emits','input','output','interface')), position INTEGER NOT NULL, target_topic_id TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,kind,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE, FOREIGN KEY(role_id,target_topic_id) REFERENCES topics(role_id,topic_id))")
                version = 2
            if version == 2:
                connection.execute('CREATE TABLE data_schemas (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, owner TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute('CREATE TABLE interface_specs (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, entry TEXT NOT NULL, method TEXT NOT NULL, request_url TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute("CREATE TABLE topic_fields (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, section TEXT NOT NULL CHECK(section IN ('data','input','output')), position INTEGER NOT NULL, name TEXT NOT NULL, field_type TEXT NOT NULL, description TEXT NOT NULL, required INTEGER NOT NULL CHECK(required IN (0,1)), PRIMARY KEY(role_id,topic_id,section,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)")
                version = 3
            if version == 3:
                connection.execute('CREATE TABLE event_definitions (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, occurrence TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute('INSERT INTO event_definitions SELECT role_id,topic_id,when_text FROM event_triggers')
                version = 4
            if version == 4:
                connection.execute('CREATE TABLE flow_trigger_conditions (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, position INTEGER NOT NULL, when_text TEXT NOT NULL, source_flow_id TEXT, ref TEXT NOT NULL, PRIMARY KEY(role_id,topic_id,position), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE, FOREIGN KEY(role_id,source_flow_id) REFERENCES topics(role_id,topic_id))')
                version = 5
            if version == 5:
                connection.execute("ALTER TABLE interface_specs ADD COLUMN kind TEXT NOT NULL DEFAULT 'internal'")
                connection.execute("ALTER TABLE interface_specs ADD COLUMN protocol TEXT NOT NULL DEFAULT ''")
                connection.execute("UPDATE interface_specs SET kind='network', protocol='HTTP' WHERE request_url<>''")
                version = 6
            if version == 6:
                connection.execute('CREATE TABLE IF NOT EXISTS flow_graphs (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, graph_json TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
                connection.execute('CREATE TABLE IF NOT EXISTS flow_intents (role_id TEXT NOT NULL, topic_id TEXT NOT NULL, purpose TEXT NOT NULL, success TEXT NOT NULL, failure TEXT NOT NULL, PRIMARY KEY(role_id,topic_id), FOREIGN KEY(role_id,topic_id) REFERENCES topics(role_id,topic_id) ON DELETE CASCADE)')
            connection.execute('UPDATE meta SET schema_version=?', (SCHEMA_VERSION,))
            connection.commit()
            return {'schemaVersion': SCHEMA_VERSION, 'changed': True}
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def init(self, value):
        overview = overview_input(value)
        self.folder.mkdir(parents=True, exist_ok=True)
        if self.folder.is_symlink():
            raise ValueError('Symlinked context directory is not allowed')
        created = False
        if not self.db.exists():
            fd = os.open(self.db, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
            os.close(fd)
            created = True
        try:
            if created:
                connection = sqlite3.connect(self.db)
                try:
                    connection.executescript(SCHEMA)
                    connection.execute('INSERT INTO meta VALUES (?)', (SCHEMA_VERSION,))
                    connection.commit()
                finally:
                    connection.close()
            with self.connection(False) as connection:
                connection.execute('BEGIN IMMEDIATE')
                if connection.execute('SELECT 1 FROM overview WHERE role_id=?', (self.role,)).fetchone():
                    raise ValueError('This role already has an overview')
                connection.execute('INSERT INTO overview VALUES (?,?,?,?,?)', (self.role, overview['title'], overview['summary'], 1, now()))
                self.save_steps(connection, overview['steps'])
        except Exception:
            if created:
                self.db.unlink(missing_ok=True)
            raise
        return self.overview()

    def overview(self):
        with self.connection() as connection:
            row = connection.execute('SELECT title,summary,revision,updated_at FROM overview WHERE role_id=?', (self.role,)).fetchone()
            if row is None:
                raise ValueError('This role has no project overview')
            steps = []
            for step in connection.execute('SELECT position,title,description,ref FROM overview_steps WHERE role_id=? ORDER BY position', (self.role,)):
                linked = [item['target_topic_id'] for item in connection.execute('SELECT target_topic_id FROM overview_step_links WHERE role_id=? AND step_position=? ORDER BY position', (self.role, step['position']))]
                steps.append({'title': step['title'], 'description': step['description'], 'ref': step['ref'], 'links': linked})
            return {**dict(row), 'steps': steps}

    def save_steps(self, connection, steps):
        connection.execute('DELETE FROM overview_steps WHERE role_id=?', (self.role,))
        for position, step in enumerate(steps):
            connection.execute('INSERT INTO overview_steps VALUES (?,?,?,?,?)', (self.role, position, step['title'], step['description'], step['ref']))
            for link_position, target in enumerate(step['links']):
                connection.execute('INSERT INTO overview_step_links VALUES (?,?,?,?)', (self.role, position, link_position, target))

    def set_overview(self, value, expected):
        overview = overview_input(value)
        with self.connection(False) as connection:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT revision FROM overview WHERE role_id=?', (self.role,)).fetchone()
            if row is None or row['revision'] != expected:
                raise ValueError('Overview revision changed; reread before writing')
            connection.execute('UPDATE overview SET title=?,summary=?,revision=?,updated_at=? WHERE role_id=?',
                               (overview['title'], overview['summary'], expected+1, now(), self.role))
            self.save_steps(connection, overview['steps'])
        return self.overview()

    def get_category(self, category):
        if category not in CATEGORIES:
            raise ValueError('Unknown category')
        with self.connection() as connection:
            row = connection.execute('SELECT category,summary,revision,updated_at FROM category_summaries WHERE role_id=? AND category=?', (self.role, category)).fetchone()
            if row is None:
                raise ValueError('Category summary not found for this role')
            return dict(row)

    def set_category(self, category, summary, expected):
        if category not in CATEGORIES:
            raise ValueError('Unknown category')
        summary = required_text(summary, 'category summary')
        with self.connection(False) as connection:
            connection.execute('BEGIN IMMEDIATE')
            if connection.execute('SELECT 1 FROM overview WHERE role_id=?', (self.role,)).fetchone() is None:
                raise ValueError('Initialize this role overview first')
            row = connection.execute('SELECT revision FROM category_summaries WHERE role_id=? AND category=?', (self.role, category)).fetchone()
            if row is None:
                if expected != 0:
                    raise ValueError('New category summary requires expected revision 0')
                connection.execute('INSERT INTO category_summaries VALUES (?,?,?,?,?)', (self.role, category, summary, 1, now()))
            else:
                if row['revision'] != expected:
                    raise ValueError('Category summary revision changed; reread before writing')
                connection.execute('UPDATE category_summaries SET summary=?,revision=?,updated_at=? WHERE role_id=? AND category=?',
                                   (summary, expected+1, now(), self.role, category))
        return self.get_category(category)

    def list_categories(self):
        with self.connection() as connection:
            return {row['category']: dict(row) for row in connection.execute('SELECT category,summary,revision,updated_at FROM category_summaries WHERE role_id=? ORDER BY category', (self.role,))}

    def list_topics(self, category=None):
        if category is not None and category not in CATEGORIES:
            raise ValueError('Unknown category')
        with self.connection() as connection:
            version = connection.execute('SELECT schema_version FROM meta').fetchone()[0]
            explained = ({row['topic_id'] for row in connection.execute('SELECT topic_id FROM flow_intents WHERE role_id=?', (self.role,))}
                         if version >= 7 and category in (None, 'flows') else set())
            query = 'SELECT topic_id,category,title,summary,revision,updated_at FROM topics WHERE role_id=? AND deleted_at IS NULL'
            params = [self.role]
            if category is not None:
                query += ' AND category=?'
                params.append(category)
            query += ' ORDER BY category,title,topic_id'
            result = []
            for row in connection.execute(query, params):
                topic = dict(row)
                if topic['category'] == 'flows':
                    topic['hasIntent'] = topic['topic_id'] in explained
                result.append(topic)
            return result

    def get_topic(self, topic_id, include_deleted=False):
        with self.connection() as connection:
            row = connection.execute('SELECT topic_id,category,title,summary,details,revision,updated_at,deleted_at FROM topics WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            if row is None or (row['deleted_at'] is not None and not include_deleted):
                raise ValueError('Topic not found for this role')
            references = [ref['ref'] for ref in connection.execute('SELECT ref FROM topic_refs WHERE role_id=? AND topic_id=? ORDER BY position', (self.role, topic_id))]
            linked = [item['target_topic_id'] for item in connection.execute('SELECT target_topic_id FROM topic_links WHERE role_id=? AND source_topic_id=? ORDER BY position', (self.role, topic_id))]
            event_row = connection.execute('SELECT occurrence FROM event_definitions WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            event = {'occurrence': event_row['occurrence']} if event_row is not None else None
            triggered_flows = []
            if row['category'] == 'events':
                triggered_flows = [item['topic_id'] for item in connection.execute("SELECT flow.topic_id FROM flow_relations AS relation JOIN topics AS flow ON flow.role_id=relation.role_id AND flow.topic_id=relation.topic_id WHERE relation.role_id=? AND relation.target_topic_id=? AND relation.kind='triggered_by' AND flow.deleted_at IS NULL ORDER BY flow.title", (self.role, topic_id))]
            flow = None
            if row['category'] == 'flows':
                steps = [dict(step) for step in connection.execute('SELECT title,description,ref FROM flow_steps WHERE role_id=? AND topic_id=? ORDER BY position', (self.role, topic_id))]
                flow = {'steps': steps}
                version = connection.execute('SELECT schema_version FROM meta').fetchone()[0]
                graph_row = (connection.execute('SELECT graph_json FROM flow_graphs WHERE role_id=? AND topic_id=?',
                                                (self.role, topic_id)).fetchone() if version >= 7 else None)
                flow['graph'] = json.loads(graph_row['graph_json']) if graph_row is not None else None
                intent_row = (connection.execute('SELECT purpose,success,failure FROM flow_intents WHERE role_id=? AND topic_id=?',
                                                 (self.role, topic_id)).fetchone() if version >= 7 else None)
                flow['intent'] = dict(intent_row) if intent_row is not None else None
                for name, (kind, _) in FLOW_RELATIONS.items():
                    flow[name] = [item['target_topic_id'] for item in connection.execute('SELECT target_topic_id FROM flow_relations WHERE role_id=? AND topic_id=? AND kind=? ORDER BY position', (self.role, topic_id, kind))]
                flow['triggers'] = [{'when': item['when_text'], 'sourceFlow': item['source_flow_id'], 'ref': item['ref']}
                                    for item in connection.execute('SELECT when_text,source_flow_id,ref FROM flow_trigger_conditions WHERE role_id=? AND topic_id=? ORDER BY position', (self.role, topic_id))]
                if not flow['triggers']:
                    for event_id in flow['triggeredBy']:
                        occurrence = connection.execute('SELECT occurrence FROM event_definitions WHERE role_id=? AND topic_id=?', (self.role, event_id)).fetchone()
                        if occurrence is not None:
                            flow['triggers'].append({'when': occurrence['occurrence'], 'sourceFlow': None, 'ref': '', 'legacyEventId': event_id})
            fields = {'data': [], 'input': [], 'output': []}
            for field in connection.execute('SELECT section,name,field_type,description,required FROM topic_fields WHERE role_id=? AND topic_id=? ORDER BY section,position', (self.role, topic_id)):
                fields[field['section']].append({'name': field['name'], 'type': field['field_type'],
                                                  'description': field['description'], 'required': bool(field['required'])})
            data_row = connection.execute('SELECT owner FROM data_schemas WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            data = {'owner': data_row['owner'], 'fields': fields['data']} if data_row is not None else None
            interface_row = connection.execute('SELECT entry,method,request_url,kind,protocol FROM interface_specs WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            interface = ({'entry': interface_row['entry'], 'method': interface_row['method'],
                          'requestUrl': interface_row['request_url'], 'kind': interface_row['kind'],
                          'protocol': interface_row['protocol'], 'inputs': fields['input'],
                          'outputs': fields['output']} if interface_row is not None else None)
            return {**dict(row), 'refs': references, 'links': linked, 'event': event,
                    'triggeredFlows': triggered_flows, 'flow': flow, 'data': data, 'interface': interface}

    def upsert(self, topic_id, value, expected):
        if not TOPIC_ID.fullmatch(topic_id):
            raise ValueError('Topic ID must be a lowercase hyphenated slug')
        topic = topic_input(value)
        with self.connection(False) as connection:
            version = connection.execute('SELECT schema_version FROM meta').fetchone()[0]
            if topic['flow'] is not None and (topic['flow']['graph'] is not None or topic['flow']['intent'] is not None) and version < 7:
                raise ValueError('项目理解数据库是旧版；先运行 migrate，再写流程图或用途说明')
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT revision,deleted_at,category FROM topics WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            if row is None:
                if topic['category'] == 'flows' and topic['flow']['intent'] is None:
                    raise ValueError('新流程必须写 flow.intent.purpose（做什么）和 success（成功后怎样）')
                if expected != 0:
                    raise ValueError('New topic requires expected revision 0')
                connection.execute('INSERT INTO topics VALUES (?,?,?,?,?,?,1,?,NULL)',
                                   (self.role, topic_id, topic['category'], topic['title'], topic['summary'], topic['details'], now()))
            else:
                if topic['category'] == 'flows' and row['category'] != 'flows' and topic['flow']['intent'] is None:
                    raise ValueError('改成流程时必须写 flow.intent.purpose 和 success')
                if topic['category'] == 'flows' and topic['flow']['intent'] is None and version >= 7:
                    had_intent = connection.execute('SELECT 1 FROM flow_intents WHERE role_id=? AND topic_id=?',
                                                    (self.role, topic_id)).fetchone()
                    if had_intent is not None:
                        raise ValueError('更新流程时要保留 flow.intent，不能把用途说明删掉')
                if row['deleted_at'] is not None:
                    raise ValueError('Deleted topic must be restored before editing')
                if row['revision'] != expected:
                    raise ValueError('Topic revision changed; reread before writing')
                connection.execute('UPDATE topics SET category=?,title=?,summary=?,details=?,revision=?,updated_at=? WHERE role_id=? AND topic_id=?',
                                   (topic['category'], topic['title'], topic['summary'], topic['details'], expected+1, now(), self.role, topic_id))
                connection.execute('DELETE FROM topic_refs WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM topic_links WHERE role_id=? AND source_topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM event_definitions WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM flow_steps WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM flow_relations WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM flow_trigger_conditions WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                if version >= 7:
                    connection.execute('DELETE FROM flow_graphs WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                    connection.execute('DELETE FROM flow_intents WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM data_schemas WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM interface_specs WHERE role_id=? AND topic_id=?', (self.role, topic_id))
                connection.execute('DELETE FROM topic_fields WHERE role_id=? AND topic_id=?', (self.role, topic_id))
            for position, ref in enumerate(topic['refs']):
                connection.execute('INSERT INTO topic_refs VALUES (?,?,?,?)', (self.role, topic_id, position, ref))
            for position, target in enumerate(topic['links']):
                connection.execute('INSERT INTO topic_links VALUES (?,?,?,?)', (self.role, topic_id, position, target))
            if topic['event'] is not None:
                connection.execute('INSERT INTO event_definitions VALUES (?,?,?)',
                                   (self.role, topic_id, topic['event']['occurrence']))
            if topic['flow'] is not None:
                for position, trigger in enumerate(topic['flow']['triggers']):
                    source_flow = trigger['sourceFlow']
                    if source_flow is not None:
                        source = connection.execute('SELECT category,deleted_at FROM topics WHERE role_id=? AND topic_id=?', (self.role, source_flow)).fetchone()
                        if source is None or source['category'] != 'flows' or source['deleted_at'] is not None:
                            raise ValueError('sourceFlow must reference an active Flow of this role: '+source_flow)
                    connection.execute('INSERT INTO flow_trigger_conditions VALUES (?,?,?,?,?,?)',
                                       (self.role, topic_id, position, trigger['when'], source_flow, trigger['ref']))
                for position, step in enumerate(topic['flow']['steps']):
                    connection.execute('INSERT INTO flow_steps VALUES (?,?,?,?,?,?)', (self.role, topic_id, position, step['title'], step['description'], step['ref']))
                if topic['flow']['graph'] is not None:
                    connection.execute('INSERT INTO flow_graphs VALUES (?,?,?)',
                                       (self.role, topic_id, json.dumps(topic['flow']['graph'], ensure_ascii=False)))
                if topic['flow']['intent'] is not None:
                    intent = topic['flow']['intent']
                    connection.execute('INSERT INTO flow_intents VALUES (?,?,?,?,?)',
                                       (self.role, topic_id, intent['purpose'], intent['success'], intent['failure']))
                for name, (kind, category) in FLOW_RELATIONS.items():
                    for position, target in enumerate(topic['flow'][name]):
                        target_row = connection.execute('SELECT category,deleted_at FROM topics WHERE role_id=? AND topic_id=?', (self.role, target)).fetchone()
                        if target_row is None or target_row['category'] != category or target_row['deleted_at'] is not None:
                            raise ValueError(name+' must reference an active '+category+' topic of this role: '+target)
                        connection.execute('INSERT INTO flow_relations VALUES (?,?,?,?,?)', (self.role, topic_id, kind, position, target))
            if topic['data'] is not None:
                connection.execute('INSERT INTO data_schemas VALUES (?,?,?)', (self.role, topic_id, topic['data']['owner']))
                for position, field in enumerate(topic['data']['fields']):
                    connection.execute('INSERT INTO topic_fields VALUES (?,?,?,?,?,?,?,?)',
                                       (self.role, topic_id, 'data', position, field['name'], field['type'], field['description'], int(field['required'])))
            if topic['interface'] is not None:
                spec = topic['interface']
                connection.execute('INSERT INTO interface_specs VALUES (?,?,?,?,?,?,?)',
                                   (self.role, topic_id, spec['entry'], spec['method'], spec['requestUrl'], spec['kind'], spec['protocol']))
                for section, values in (('input', spec['inputs']), ('output', spec['outputs'])):
                    for position, field in enumerate(values):
                        connection.execute('INSERT INTO topic_fields VALUES (?,?,?,?,?,?,?,?)',
                                           (self.role, topic_id, section, position, field['name'], field['type'], field['description'], int(field['required'])))
        return self.get_topic(topic_id)

    def delete(self, topic_id, expected, restore=False):
        with self.connection(False) as connection:
            connection.execute('BEGIN IMMEDIATE')
            row = connection.execute('SELECT revision,deleted_at FROM topics WHERE role_id=? AND topic_id=?', (self.role, topic_id)).fetchone()
            if row is None:
                raise ValueError('Topic not found for this role')
            if row['revision'] != expected:
                raise ValueError('Topic revision changed; reread before writing')
            if restore and row['deleted_at'] is None:
                raise ValueError('Topic is already active')
            if not restore and row['deleted_at'] is not None:
                raise ValueError('Topic is already deleted')
            connection.execute('UPDATE topics SET deleted_at=?,revision=?,updated_at=? WHERE role_id=? AND topic_id=?',
                               (None if restore else now(), expected+1, now(), self.role, topic_id))
        return self.get_topic(topic_id, include_deleted=True)

    def search(self, query):
        term = required_text(query, 'query').replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        with self.connection() as connection:
            sql = "SELECT topic_id,category,title,summary,revision FROM topics WHERE role_id=? AND deleted_at IS NULL AND (title LIKE ? ESCAPE '\\' OR summary LIKE ? ESCAPE '\\' OR details LIKE ? ESCAPE '\\') ORDER BY category,title LIMIT 50"
            return [dict(row) for row in connection.execute(sql, (self.role, '%'+term+'%', '%'+term+'%', '%'+term+'%'))]

    def flows_without_triggers(self):
        with self.connection() as connection:
            query = """SELECT flow.topic_id FROM topics AS flow
                       WHERE flow.role_id=? AND flow.category='flows' AND flow.deleted_at IS NULL
                       AND NOT EXISTS (
                         SELECT 1 FROM flow_trigger_conditions AS condition
                         WHERE condition.role_id=flow.role_id AND condition.topic_id=flow.topic_id
                       ) AND NOT EXISTS (
                         SELECT 1 FROM flow_relations AS legacy
                         WHERE legacy.role_id=flow.role_id AND legacy.topic_id=flow.topic_id AND legacy.kind='triggered_by'
                       ) ORDER BY flow.topic_id"""
            return [row['topic_id'] for row in connection.execute(query, (self.role,))]

    def flows_without_purpose(self):
        with self.connection() as connection:
            version = connection.execute('SELECT schema_version FROM meta').fetchone()[0]
            if version < 7:
                query = "SELECT topic_id FROM topics WHERE role_id=? AND category='flows' AND deleted_at IS NULL ORDER BY topic_id"
            else:
                query = """SELECT flow.topic_id FROM topics AS flow
                           LEFT JOIN flow_intents AS intent ON intent.role_id=flow.role_id AND intent.topic_id=flow.topic_id
                           WHERE flow.role_id=? AND flow.category='flows' AND flow.deleted_at IS NULL
                           AND intent.topic_id IS NULL ORDER BY flow.topic_id"""
            return [row['topic_id'] for row in connection.execute(query, (self.role,))]

    def validate(self):
        triggers = self.flows_without_triggers()
        purpose = self.flows_without_purpose()
        return {'valid': not triggers and not purpose, 'roleId': self.role,
                'flowsWithoutTriggers': triggers, 'flowsWithoutPurpose': purpose}

    def outline(self):
        return {'roleId': self.role, 'role': self.role_metadata(), 'overview': self.overview(),
                'categorySummaries': self.list_categories(), 'topics': self.list_topics(),
                'flowsWithoutTriggers': self.flows_without_triggers(),
                'flowsWithoutPurpose': self.flows_without_purpose()}


def input_json(path):
    content = sys.stdin.read() if path == '-' else Path(path).read_text(encoding='utf-8')
    return json.loads(content)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, help='Project root')
    parser.add_argument('--role', required=True, help='Target role folder name; reads are filtered to this role')
    parser.add_argument('--actor-role', help='Required for writes; must equal target role')
    parser.add_argument('--roles', help='Optional role directory inside project root')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('outline', 'overview'):
        commands.add_parser(name)
    commands.add_parser('validate')
    commands.add_parser('migrate')
    for name in ('init', 'set-overview'):
        command = commands.add_parser(name)
        command.add_argument('--input', required=True, help='JSON input file, or - for stdin')
        if name == 'set-overview':
            command.add_argument('--expect-revision', type=int, required=True)
    listing = commands.add_parser('list')
    listing.add_argument('--category', choices=CATEGORIES)
    category_read = commands.add_parser('get-category')
    category_read.add_argument('category', choices=CATEGORIES)
    category_write = commands.add_parser('set-category')
    category_write.add_argument('category', choices=CATEGORIES)
    category_write.add_argument('--input', required=True, help='JSON object with summary')
    category_write.add_argument('--expect-revision', type=int, required=True)
    detail = commands.add_parser('get')
    detail.add_argument('topic_id')
    search = commands.add_parser('search')
    search.add_argument('query')
    upsert = commands.add_parser('upsert')
    upsert.add_argument('topic_id')
    upsert.add_argument('--input', required=True)
    upsert.add_argument('--expect-revision', type=int, required=True)
    for name in ('delete', 'restore'):
        command = commands.add_parser(name)
        command.add_argument('topic_id')
        command.add_argument('--expect-revision', type=int, required=True)
    args = parser.parse_args(argv)
    try:
        writes = {'init', 'migrate', 'set-overview', 'set-category', 'upsert', 'delete', 'restore'}
        if args.command in writes and args.actor_role != args.role:
            raise ValueError('Writes require --actor-role matching --role and an accepted role boundary')
        store = ContextStore(args.root, args.role, args.roles)
        if args.command == 'init': result = store.init(input_json(args.input))
        elif args.command == 'migrate': result = store.migrate()
        elif args.command == 'set-overview': result = store.set_overview(input_json(args.input), args.expect_revision)
        elif args.command == 'overview': result = store.overview()
        elif args.command == 'outline': result = store.outline()
        elif args.command == 'validate': result = store.validate()
        elif args.command == 'list': result = store.list_topics(args.category)
        elif args.command == 'get-category': result = store.get_category(args.category)
        elif args.command == 'set-category': result = store.set_category(args.category, category_input(input_json(args.input)), args.expect_revision)
        elif args.command == 'get': result = store.get_topic(args.topic_id)
        elif args.command == 'search': result = store.search(args.query)
        elif args.command == 'upsert': result = store.upsert(args.topic_id, input_json(args.input), args.expect_revision)
        elif args.command == 'delete': result = store.delete(args.topic_id, args.expect_revision)
        else: result = store.delete(args.topic_id, args.expect_revision, restore=True)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if args.command == 'validate' and not result['valid']:
            return 2
        return 0
    except (OSError, ValueError, sqlite3.Error) as exc:
        print(json.dumps({'error': str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
