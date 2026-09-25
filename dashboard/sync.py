"""Send only dashboard projections from a project to its cloud Dashboard."""
import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlparse
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .cloud_store import PROJECT_ID
from .context_store import ContextStore
from .local_config import load_project_config
from .paths import normalize_base_path
from .server import Dashboard
from .sync_runtime import SyncAlreadyRunning, SyncLease, sync_status


def projection(root, project_id, roles=None, scheduling=None):
    if not PROJECT_ID.fullmatch(project_id):
        raise ValueError('Project id must be a lowercase hyphenated slug')
    dashboard = Dashboard(root, roles, scheduling)
    snapshot = dashboard.snapshot()
    snapshot.pop('projectRootUri', None)
    snapshot['projectId'] = project_id
    contexts = {}
    for role in snapshot['roles']:
        role['documents'] = {}
        outline = role.get('projectContext')
        if outline is None:
            continue
        store = ContextStore(root, role['id'], dashboard.roles)
        topics = {item['topic_id']: store.get_topic(item['topic_id']) for item in outline['topics']}
        contexts[role['id']] = {'outline': outline, 'topics': topics}
    return {'schemaVersion': 1, 'snapshot': snapshot, 'contexts': contexts}


def send(server_url, project_id, token, value):
    parsed = urlparse(server_url)
    if not PROJECT_ID.fullmatch(project_id):
        raise ValueError('Project id must be a lowercase hyphenated slug')
    if not parsed.netloc or parsed.params or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Server URL must not contain credentials, parameters, query, or fragment')
    base_path = normalize_base_path(parsed.path)
    local = parsed.hostname in ('127.0.0.1', 'localhost')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and local):
        raise ValueError('Cloud sync requires HTTPS; HTTP is allowed only on loopback for testing')
    url = parsed._replace(path=base_path+'/p/'+project_id+'/api/sync', params='',
                          query='', fragment='').geturl()
    data = json.dumps(value, ensure_ascii=False).encode('utf-8')
    request = Request(url, data=data, headers={'Content-Type': 'application/json',
                                               'Authorization': 'Bearer ' + token}, method='POST')
    class NoRedirect(HTTPRedirectHandler):
        def redirect_request(self, *_args, **_kwargs):
            return None
    with build_opener(NoRedirect).open(request, timeout=20) as response:
        return json.load(response)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path)
    parser.add_argument('--roles', help='Role directory override within project root')
    parser.add_argument('--scheduling', help='Scheduling directory override within project root')
    parser.add_argument('--project-id')
    parser.add_argument('--server-url')
    parser.add_argument('--key-env', default='ANS_DASHBOARD_KEY', help='Environment variable holding the project Key')
    parser.add_argument('--interval', type=float, help='Seconds between syncs; omit for one sync')
    parser.add_argument('--status', action='store_true', help='Report continuous sync liveness without reading the Key')
    args = parser.parse_args(argv)
    root = args.root or Path.cwd()
    if args.status:
        try:
            print(json.dumps(sync_status(root), ensure_ascii=False))
        except (OSError, ValueError) as error:
            parser.error(str(error))
        return 0
    environment_key = os.environ.get(args.key_env)
    config = None
    if args.project_id is None or args.server_url is None or not environment_key:
        try:
            config = load_project_config(root, args.project_id)
        except (OSError, ValueError) as error:
            parser.error(str(error))
    project_id = args.project_id or (config['projectId'] if config else None)
    server_url = args.server_url or (config['serverUrl'] if config else None)
    token = environment_key or (config['projectKey'] if config else None)
    if project_id is None or server_url is None:
        parser.error('Set up the project configuration or pass --project-id and --server-url')
    if not token:
        parser.error('Project Key is missing from local configuration and environment')
    if args.interval is not None and args.interval < 2:
        parser.error('--interval must be at least 2 seconds')
    if not root.is_dir():
        parser.error('Project root does not exist')
    try:
        lease_context = SyncLease(root, project_id, args.interval) if args.interval is not None else nullcontext(None)
        with lease_context as lease:
            while True:
                try:
                    result = send(server_url, project_id, token,
                                  projection(root, project_id, args.roles, args.scheduling))
                except HTTPError as error:
                    if lease is not None:
                        lease.failure(error)
                    if lease is None or (400 <= error.code < 500 and error.code not in (408, 429)):
                        raise
                    print('Cloud sync HTTP '+str(error.code)+'; retrying', file=sys.stderr, flush=True)
                except OSError as error:
                    if lease is not None:
                        lease.failure(error)
                    if lease is None:
                        raise
                    print('Cloud sync network error; retrying', file=sys.stderr, flush=True)
                except Exception as error:
                    if lease is not None:
                        lease.failure(error)
                    raise
                else:
                    if lease is not None:
                        lease.success()
                    print(json.dumps(result, ensure_ascii=False), flush=True)
                if args.interval is None:
                    return 0
                time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, SyncAlreadyRunning) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
