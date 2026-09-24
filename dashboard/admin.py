"""Bootstrap the first Dashboard administrator without putting a password in shell history."""
import argparse
import getpass
import sys

from .cloud_store import CloudStore


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', required=True)
    parser.add_argument('--username', required=True)
    parser.add_argument('--password-stdin', action='store_true', help='Read password from stdin instead of prompting')
    args = parser.parse_args(argv)
    password = sys.stdin.readline().rstrip('\n') if args.password_stdin else getpass.getpass('Initial administrator password: ')
    store = CloudStore(args.state_dir)
    try:
        result = store.create_user(args.username, password, role='admin', bootstrap=True)
    except ValueError as exc:
        parser.error(str(exc))
    print('Created administrator:', result['username'])


if __name__ == '__main__':
    main()
