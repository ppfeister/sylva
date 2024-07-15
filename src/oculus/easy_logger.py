from enum import Enum

from colorama import Fore, Back, Style

from . import __short_name__, __long_name__, __version__
from .config import config

class LogLevel(Enum):
    FATAL = 0
    ERROR = 1
    WARNING = 2
    SUCCESS_ONLY = 3
    INFO = 4 # Default
    DEBUG = 5
    TRACE = 6

if not config['General']['colorful']:
    class NoColor:
        BLACK=RED=''
    Fore = NoColor

loglevel = int(config['General']['log_level'])

def info(message:str):
    if loglevel < LogLevel.INFO.value:
        return
    print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} {message}')
