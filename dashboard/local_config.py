"""Private Dashboard connection settings stored beside each business project."""
import argparse
import getpass
import json
import os
from pathlib import Path
import stat
import subprocess
import tempfile
from urllib.parse import urlparse

from .cloud_store import PROJECT_ID
from .paths import normalize_base_path

CONFIG_NAME = '.ans-dashboard.local.json'


def config_path(root):
    return Path(root).expanduser().resolve()/CONFIG_NAME


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


def validate_config(config, project_id=None):
    if not isinstance(config, dict) or config.get('schemaVersion') != 1:
        raise ValueError('Invalid local project configuration')
    stored_id = config.get('projectId')
    if not isinstance(stored_id, str) or not PROJECT_ID.fullmatch(stored_id):
        raise ValueError('Project id must be a lowercase hyphenated slug')
    if project_id is not None and stored_id != project_id:
        raise ValueError('Local project ID does not match --project-id')
    validate_server_url(config.get('serverUrl'))
    key = config.get('projectKey')
    if not isinstance(key, str) or not key.startswith('ansp_') or not 5 < len(key) <= 256:
        raise ValueError('Invalid project Key')
    return config


def load_project_config(root, project_id=None):
    path = config_path(root)
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


def exclude_from_git(root, path):
    """Exclude the local secret without changing a tracked .gitignore."""
    try:
        top = subprocess.run(['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
                             capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return
    if top.returncode:
        return
    repository = Path(top.stdout.strip()).resolve()
    relative = path.relative_to(repository).as_posix()
    tracked = subprocess.run(['git', '-C', str(repository), 'ls-files', '--error-unmatch',
                              '--', relative], capture_output=True, check=False)
    if tracked.returncode == 0:
        raise ValueError('Local project configuration is tracked by Git; untrack it before saving a Key')
    exclude = subprocess.run(['git', '-C', str(root), 'rev-parse', '--git-path', 'info/exclude'],
                             capture_output=True, text=True, check=True).stdout.strip()
    exclude_path = Path(exclude)
    if not exclude_path.is_absolute():
        exclude_path = root/exclude_path
    parent = Path(relative).parent.as_posix()
    prefix = '/' if parent == '.' else '/'+parent+'/'
    patterns = (prefix+CONFIG_NAME, prefix+'.ans-dashboard-*')
    existing = exclude_path.read_text(encoding='utf-8') if exclude_path.exists() else ''
    missing = [pattern for pattern in patterns if pattern not in existing.splitlines()]
    if missing:
        exclude_path.parent.mkdir(parents=True, exist_ok=True)
        with exclude_path.open('a', encoding='utf-8') as output:
            output.write(('' if not existing or existing.endswith('\n') else '\n')+'\n'.join(missing)+'\n')
    ignored = subprocess.run(['git', '-C', str(repository), 'check-ignore', '-q', '--no-index',
                              '--', relative], capture_output=True, check=False)
    if ignored.returncode:
        raise ValueError('Git did not ignore the local project configuration')


def save_project_config(project_id, root, server_url, key, replace=False):
    root = Path(root).expanduser().resolve()
    if not root.is_dir():
        raise ValueError('Project root does not exist')
    config = validate_config({'schemaVersion': 1, 'projectId': project_id,
                              'serverUrl': validate_server_url(server_url),
                              'projectKey': key})
    path = config_path(root)
    if path.is_symlink():
        raise ValueError('Local project configuration must not be a symlink')
    if path.exists() and not replace:
        raise ValueError('Local project configuration already exists; use --replace to update it')
    exclude_from_git(root, path)
    fd, temporary = tempfile.mkstemp(prefix='.ans-dashboard-', dir=root)
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
    show.add_argument('--root', type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        if args.command == 'init':
            path = config_path(args.root)
            if path.exists() and not args.replace:
                raise ValueError('Local project configuration already exists; use --replace to update it')
            key = getpass.getpass('Project Key: ')
            path = save_project_config(args.project_id, args.root, args.server_url, key, args.replace)
            print('Saved '+str(path))
        else:
            config = load_project_config(args.root)
            if config is None:
                raise ValueError('Local project configuration not found')
            shown = {'schemaVersion': config['schemaVersion'], 'projectId': config['projectId'],
                     'serverUrl': config['serverUrl'], 'root': str(Path(args.root).expanduser().resolve())}
            print(json.dumps(shown, ensure_ascii=False, indent=2))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.error(str(error))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
