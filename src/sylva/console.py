import argparse
import sys

from . import __author__, __forge_url__, __long_name__, __short_name__, __version__
from .config import InteractiveConfig
from .handler import Handler


def config_subcommand(args:argparse.Namespace) -> None:
    """Handles the config subcommand

    Keyword Arguments:
    args -- argparse.Namespace"""
    if args.interactive_edit:
        editor = InteractiveConfig()
        editor.launch_preferred_editor()
        return


def search_subcommand(args:argparse.Namespace) -> None:
    """Handles the search subcommand

    Keyword Arguments:
    args -- argparse.Namespace"""
    handler = Handler()
    handler.search_all(args.query)
    print()
    print(handler.collector.get_data())


def branch_subcommand(args:argparse.Namespace) -> None:
    handler = Handler()
    handler.branch_all(args.query, depth=args.branch_depth)
    print()
    print(handler.collector.get_data())


def interactive_setup_subcommand(args:argparse.Namespace) -> None:
    pass


def interactive() -> None:
    parser = argparse.ArgumentParser(description=f'{__long_name__}')
    subparsers = parser.add_subparsers(dest='command')

    parser_search = subparsers.add_parser('search', help='Find an identity')
    parser_search.add_argument('query', help='The query to search for')
    parser_search.add_argument('--captcha', dest='custom-captcha-proxy-address', action='store', default=None, metavar='PROXY_URL', help='Use an alternative captcha-solving proxy server')  # fmt: skip # noqa: E501
    parser_search.set_defaults(func=search_subcommand)

    parser_branch = subparsers.add_parser('branch', help='Recursively search based on discovered identities')
    parser_branch.add_argument('query', help='The query to search for')
    parser_branch.add_argument('-d', '--depth', type=int, default=3, dest='branch_depth', metavar='123', help='The depth to search')  # fmt: skip # noqa: E501
    parser_branch.add_argument('-a', '--show-all', dest='no_deduplicate', action='store_true', default=False, help='Do not deduplicate results')  # fmt: skip # noqa: E501
    parser_branch.add_argument('--captcha', dest='custom-captcha-proxy-address', action='store', default=None, metavar='PROXY_URL', help='Use an alternative captcha-solving proxy server')  # fmt: skip # noqa: E501
    parser_branch.set_defaults(func=branch_subcommand)

    parser_interactive = subparsers.add_parser('interactive', help='Launch the query builder (mutliple parameters allowed)')  # fmt: skip # noqa: E501
    parser_interactive.set_defaults(func=interactive_setup_subcommand)

    parser_config = subparsers.add_parser('config', help=f'Edit the {__short_name__} config')
    parser_config.add_argument('-e', '--edit', dest='interactive_edit', action='store_true', default=False, help='Edit the config interactively')  # fmt: skip # noqa: E501
    parser_config.set_defaults(func=config_subcommand)

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f'{__short_name__} Version {__version__}',
        help='Show the version and exit',
    )

    parser.add_argument(
        '--credits',
        dest='show_credits',
        action='store_true',
        default=False,
        help='Show author information and exit',
    )

    args = parser.parse_args()

    if args.show_credits:
        print(__long_name__)
        print(' - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -')
        print(f'Created by {__author__}    - https://pfeister.dev')
        print(f'Star the project on GitHub  - {__forge_url__}')
        print('Support further development - https://github.com/sponsors/ppfeister')
        return

    if args.command:
        if len(sys.argv) <= 2:
            subparsers.choices[args.command].print_help()
        args.func(args)
    else:
        parser.print_help()
