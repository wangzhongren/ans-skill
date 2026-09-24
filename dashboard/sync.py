"""Send only dashboard projections from a project to its cloud Dashboard."""
import argparse
import json
import os
from pathlib import Path
import sys
import time
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .cloud_store import PROJECT_ID
from .context_store import ContextStore
from .server import Dashboard


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
    if not parsed.netloc or parsed.path not in ('', '/') or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Server URL must be an origin without path, credentials, query, or fragment')
    local = parsed.hostname in ('127.0.0.1', 'localhost')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and local):
        raise ValueError('Cloud sync requires HTTPS; HTTP is allowed only on loopback for testing')
    url = server_url.rstrip('/') + '/p/' + project_id + '/api/sync'
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
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--roles', help='Role directory override within project root')
    parser.add_argument('--scheduling', help='Scheduling directory override within project root')
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--server-url', required=True)
    parser.add_argument('--key-env', default='ANS_DASHBOARD_KEY', help='Environment variable holding the project Key')
    parser.add_argument('--interval', type=float, help='Seconds between syncs; omit for one sync')
    args = parser.parse_args(argv)
    token = os.environ.get(args.key_env)
    if not token:
        parser.error('Project Key environment variable is not set')
    if args.interval is not None and args.interval < 2:
        parser.error('--interval must be at least 2 seconds')
    if not args.root.is_dir():
        parser.error('Project root does not exist')
    try:
        while True:
            result = send(args.server_url, args.project_id, token,
                          projection(args.root, args.project_id, args.roles, args.scheduling))
            print(json.dumps(result, ensure_ascii=False), flush=True)
            if args.interval is None:
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
