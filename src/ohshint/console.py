from argparse import ArgumentParser

from .__init__ import __short_name__, __long_name__, __version__
from .config import config, InteractiveConfig


def config_subcommand(args):
    if args.interactive_edit:
        editor = InteractiveConfig()
        editor.launch_preferred_editor()
        return


def interactive():
    parser = ArgumentParser(description=f'{__long_name__}')
    subparsers = parser.add_subparsers(dest='command')

    parser_search = subparsers.add_parser('find', help='Find an identity')
    parser_search.add_argument('query', help='The query to search for')
    parser_search.set_defaults(func=config_subcommand)

    parser_config = subparsers.add_parser('config', help=f'Edit {__short_name__}\'s config')
    parser_config.add_argument('--edit', dest='interactive_edit', action='store_true', default=False, help='Edit the config interactively')
    parser_config.set_defaults(func=config_subcommand)

    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version=f'{__short_name__} {__version__}',
        help='Show the version and exit'
    )

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()
