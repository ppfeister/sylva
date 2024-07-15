from typing import List

from colorama import Fore, Back, Style
import pandas as pd

from .collector import Collector
from .config import config
from .easy_logger import LogLevel, loglevel, NoColor
from .helpers.helpers import (
    IncompatibleQueryType,
    RequestError,
    APIKeyError,
)
from .integrations import (
    endato,
    proxynova,
    #intelx,
    veriphone,
)
from .modules import (
    pgp as pgp_module,
    sherlock,
)


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor

class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
        self.runners:List = [
            proxynova.ProxyNova(collector=self.collector),
            endato.Endato(collector=self.collector, api_name=config['Keys']['endato-name'], api_key=config['Keys']['endato-key']),
            #intelx.IntelX(collector=self.collector, api_key=config['Keys']['intelx-key']),
            pgp_module.PGPModule(collector=self.collector),
            veriphone.Veriphone(collector=self.collector, api_key=config['Keys']['veriphone-key'], country='US'),
            sherlock.Sherlock(collector=self.collector),
        ]
    def search_all(self, query:str):
        for runner in self.runners:

            if not runner.accepts(query):
                if loglevel >= LogLevel.DEBUG.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Query type not supported by {runner.source_name}')
                continue

            if loglevel >= LogLevel.INFO.value:
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Searching {runner.source_name}')

            try:
                results = len(runner.search(query=query).index)
                if loglevel >= LogLevel.SUCCESS_ONLY.value and results > 0:
                    print(f'{Fore.LIGHTGREEN_EX}{Style.BRIGHT}[+]{Style.RESET_ALL}{Fore.RESET} Found {results} via {runner.source_name}')
            except RequestError:
                pass
            except APIKeyError as e:
                if e.key_not_provided:
                    if loglevel >= LogLevel.INFO.value:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} API key has not been provided for {runner.source_name} - {runner.source_obtain_keys_url}')
