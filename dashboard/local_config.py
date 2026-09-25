"""Private, per-project configuration for local Dashboard clients."""
import argparse
import getpass
import json
import os
from pathlib import Path
import stat
import tempfile
from urllib.parse import urlparse

from .cloud_store import PROJECT_ID
from .paths import normalize_base_path


def config_path(project_id):
    if not isinstance(project_id, str) or not PROJECT_ID.fullmatch(project_id):
        raise ValueError('Project id must be a lowercase hyphenated slug')
    base = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home()/'.config').expanduser()
    return base/'ans-dashboard'/'projects'/(project_id+'.json')


def validate_server_url(server_url):
    if not isinstance(server_url, str):
        raise ValueError('Server URL must be HTTPS (HTTP is allowed only on loopback)')
    parsed = urlparse(server_url)
    if not parsed.netloc or parsed.params or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError('Server URL must not contain credentials, parameters, query, or fragment')
    if parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('127.0.0.1', 'localhost')):
        raise ValueError('Server URL must be HTTPS (HTTP is allowed only on loopback)')
    normalize_base_path(parsed.path)
    return server_url.rstrip('/')


def validate_config(config, project_id):
    if not isinstance(config, dict) or config.get('schemaVersion') != 1 or config.get('projectId') != project_id:
        raise ValueError('Invalid local project configuration')
    root = config.get('root')
    if not isinstance(root, str) or not Path(root).is_absolute():
        raise ValueError('Project root must be an absolute path')
    validate_server_url(config.get('serverUrl'))
    key = config.get('projectKey')
    if not isinstance(key, str) or not key.startswith('ansp_') or not 5 < len(key) <= 256:
        raise ValueError('Invalid project Key')
    return config


def load_project_config(project_id):
    path = config_path(project_id)
    if path.parent.is_symlink() or path.parent.parent.is_symlink():
        raise ValueError('Local configuration directory must not be a symlink')
    if not path.exists() and not path.is_symlink():
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError('Local project configuration must be a regular file')
    if os.name == 'posix' and stat.S_IMODE(path.stat().st_mode) & 0o077:
        raise ValueError('Local project configuration must be readable only by its owner (chmod 600)')
    try:
        config = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as error:
        raise ValueError('Cannot read local project configuration') from error
    return validate_config(config, project_id)


def save_project_config(project_id, root, server_url, key, replace=False):
    path = config_path(project_id)
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('Project root does not exist')
    config = validate_config({'schemaVersion': 1, 'projectId': project_id,
                              'root': str(root), 'serverUrl': validate_server_url(server_url),
                              'projectKey': key}, project_id)
    for directory in (path.parent.parent, path.parent):
        if directory.is_symlink():
            raise ValueError('Local configuration directory must not be a symlink')
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(directory, 0o700)
    if path.is_symlink():
        raise ValueError('Local project configuration must not be a symlink')
    if path.exists() and not replace:
        raise ValueError('Local project configuration already exists; use --replace to update it')
    fd, temporary = tempfile.mkstemp(prefix='.'+project_id+'-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as output:
            json.dump(config, output, ensure_ascii=False, indent=2)
            output.write('\n')
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    initialize = commands.add_parser('init', help='Save a private project configuration')
    initialize.add_argument('--project-id', required=True)
    initialize.add_argument('--root', type=Path, required=True)
    initialize.add_argument('--server-url', required=True)
    initialize.add_argument('--replace', action='store_true', help='Replace an existing local configuration')
    show = commands.add_parser('show', help='Show configuration without revealing the Key')
    show.add_argument('--project-id', required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            path = config_path(args.project_id)
            if path.exists() and not args.replace:
                raise ValueError('Local project configuration already exists; use --replace to update it')
            key = getpass.getpass('Project Key: ')
            path = save_project_config(args.project_id, args.root, args.server_url, key, args.replace)
            print('Saved '+str(path))
        else:
            config = load_project_config(args.project_id)
            if config is None:
                raise ValueError('Local project configuration not found')
            print(json.dumps({name: value for name, value in config.items() if name != 'projectKey'},
                             ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
