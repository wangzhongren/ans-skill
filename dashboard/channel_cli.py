"""Role agent client using one shared project Key for Dashboard communication."""
import argparse
import json
import os
from pathlib import Path
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .cloud_store import PROJECT_ID
from .paths import normalize_base_path


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *_args, **_kwargs):
        return None


def call(server_url, project_id, token, action, value=None):
    parsed = urlparse(server_url)
    if not PROJECT_ID.fullmatch(project_id):
        raise ValueError('Invalid project id')
    if not parsed.netloc or parsed.params or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Server URL must not contain credentials, parameters, query, or fragment')
    base_path = normalize_base_path(parsed.path)
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost')):
        raise ValueError('Project channel requires HTTPS; HTTP is only allowed on loopback')
    if action not in ('channel', 'messages', 'permission-requests'):
        raise ValueError('Unknown channel action')
    url = parsed._replace(path=base_path+'/p/'+project_id+'/api/'+action,
                          params='', query='', fragment='').geturl()
    data = None if value is None else json.dumps(value, ensure_ascii=False).encode('utf-8')
    headers = {'Authorization': 'Bearer '+token}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    request = Request(url, data=data, headers=headers, method='GET' if data is None else 'POST')
    try:
        with build_opener(NoRedirect).open(request, timeout=20) as response:
            return json.load(response)
    except HTTPError as error:
        try:
            detail = json.load(error).get('error', 'HTTP '+str(error.code))
        except (ValueError, AttributeError):
            detail = 'HTTP '+str(error.code)
        raise ValueError(detail) from None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-url', required=True)
    parser.add_argument('--project-id', required=True)
    parser.add_argument('--token-env', default='ANS_DASHBOARD_KEY')
    parser.add_argument('--role', help='Sending role ID; also filters list output when provided')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('list')
    for command in ('send', 'request'):
        sub.add_parser(command).add_argument('--input', type=Path, required=True)
    args = parser.parse_args(argv)
    token = os.environ.get(args.token_env)
    if not token:
        parser.error('Project Key environment variable is not set')
    try:
        value = None if args.command == 'list' else json.loads(args.input.read_text(encoding='utf-8'))
        if args.command in ('send', 'request'):
            if not args.role:
                raise ValueError('--role is required when sending as a role')
            if not isinstance(value, dict):
                raise ValueError('Input JSON must be an object')
            field = 'fromRoleId' if args.command == 'send' else 'requesterRoleId'
            if field in value and value[field] != args.role:
                raise ValueError('Input role does not match --role')
            value[field] = args.role
        action = {'list': 'channel', 'send': 'messages', 'request': 'permission-requests'}[args.command]
        result = call(args.server_url, args.project_id, token, action, value)
        if args.command == 'list' and args.role:
            result['messages'] = [item for item in result['messages']
                                  if item['to_role_id'] == args.role or
                                  (item['sender_kind'] == 'role' and item['sender_id'] == args.role)]
            result['requests'] = [item for item in result['requests']
                                  if item['requester_role_id'] == args.role]
    except (OSError, ValueError, URLError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
