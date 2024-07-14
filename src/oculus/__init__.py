from importlib.metadata import version

__short_name__ = 'Oculus'
__long_name__ = f'{__short_name__} - OSINT Simplified'
__version__ = version(__short_name__.lower())
__forge_url__ = 'https://github.com/ppfeister/oculus'
__user_agent__ = f'{__short_name__}/{__version__} ({__forge_url__})'
__author__ = 'Paul Pfeister'
__author_email__ = 'code@pfeister.dev'
__license__ = 'AGPL-3.0-or-later'
__copyright__ = f'Copyright 2024 {__author__}'

__github_raw_data_url__ = 'https://raw.githubusercontent.com/ppfeister/oculus/master/src/oculus/data/gpg.json'
__github_raw_schema_url__ = 'https://raw.githubusercontent.com/ppfeister/oculus/master/src/oculus/data/gpg.schema.json'
