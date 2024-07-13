import argparse

from . import __short_name__, __long_name__, __version__
from .config import config, InteractiveConfig
from .handler import Handler

def config_subcommand(args:argparse.Namespace):
    """Handles the config subcommand
    
    Keyword Arguments:
    args -- argparse.Namespace"""
    if args.interactive_edit:
        editor = InteractiveConfig()
        editor.launch_preferred_editor()
        return


def search_subcommand(args:argparse.Namespace):
    """Handles the search subcommand

    Keyword Arguments:
    args -- argparse.Namespace"""
    handler = Handler()
    handler.search_all(args.query)
    print(handler.collector.get_data())


def spider_subcommand(args:argparse.Namespace):
    pass


def interactive():
    parser = argparse.ArgumentParser(description=f'{__long_name__}')
    subparsers = parser.add_subparsers(dest='command')

    parser_search = subparsers.add_parser('search', help='Find an identity')
    parser_search.add_argument('query', help='The query to search for')
    parser_search.set_defaults(func=search_subcommand)

    parser_spider = subparsers.add_parser('spider', help='Recursively search based on discovered identities')
    parser_spider.add_argument('query', help='The query to search for')
    parser_spider.add_argument('--depth', '-d', type=int, default=1, help='The depth to search')
    parser_spider.set_defaults(func=spider_subcommand)

    parser_config = subparsers.add_parser('config', help=f'Edit {__short_name__}\'s config')
    parser_config.add_argument('--edit', '-e', dest='interactive_edit', action='store_true', default=False, help='Edit the config interactively')
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
