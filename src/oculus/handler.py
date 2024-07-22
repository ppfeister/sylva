from typing import List, NamedTuple, Tuple

from colorama import Fore, Back, Style
import pandas as pd
import phonenumbers

from .collector import Collector
from .config import config
from .easy_logger import LogLevel, loglevel, NoColor, overwrite_previous_line
from .helpers.helpers import (
    IncompatibleQueryType,
    QueryType,
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


class QueryDataItem(NamedTuple):
    query: str
    type: QueryType


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor

class Handler:
    def __init__(self):
        self.collector:Collector = Collector()
        self.__default_country:str = 'US'
        self.runners:List = [
            proxynova.ProxyNova(collector=self.collector),
            endato.Endato(collector=self.collector, api_name=config['Keys']['endato-name'], api_key=config['Keys']['endato-key'], country=self.__default_country),
            #intelx.IntelX(collector=self.collector, api_key=config['Keys']['intelx-key']),
            pgp_module.PGPModule(collector=self.collector),
            veriphone.Veriphone(collector=self.collector, api_key=config['Keys']['veriphone-key'], country=self.__default_country),
            sherlock.Sherlock(collector=self.collector),
        ]
        self.__in_recursion = False
    def search_all(self, query:str|QueryDataItem, no_deduplicate:bool=False):
        if isinstance(query, QueryDataItem):
            query_type:QueryType = query.type
            query:str = query.query
        else:
            query_type = QueryType.TEXT

        for runner in self.runners:
            if not runner.accepts(query=query, query_type=query_type):
                if loglevel >= LogLevel.DEBUG.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Query type not supported by {runner.source_name}')
                continue

            if loglevel >= LogLevel.SUCCESS_ONLY.value:
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Searching {runner.source_name}...')

            try:
                results = len(runner.search(query=query, in_recursion=self.__in_recursion, query_type=query_type).index)
                if loglevel >= LogLevel.SUCCESS_ONLY.value and results > 0:
                    overwrite_previous_line()
                    print(f'{Fore.LIGHTGREEN_EX}{Style.BRIGHT}[+]{Style.RESET_ALL}{Fore.RESET} Found {results} via {runner.source_name}')
                elif loglevel >= LogLevel.INFO.value and results == 0:
                    overwrite_previous_line()
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} No results found via {runner.source_name}')
                elif loglevel >= LogLevel.SUCCESS_ONLY.value and results == 0:
                    overwrite_previous_line()
                else:
                    print("Something weird happened.")
            except RequestError:
                pass
            except APIKeyError as e:
                if e.key_not_provided:
                    if loglevel >= LogLevel.INFO.value:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} API key has not been provided for {runner.source_name} - {runner.source_obtain_keys_url}')
        
        if not no_deduplicate:
            self.collector.deduplicate()

    def spider_all(self, query: str, depth: int = 1, no_deduplicate: bool = False):
        # TODO Any way to pretty this up? Avoid re-running queries against all on raw input
        queries_made: set = set((QueryDataItem(query=query, type=QueryType.TEXT),))
        queries_made.add(QueryDataItem(query=query, type=QueryType.USERNAME))
        queries_made.add(QueryDataItem(query=query, type=QueryType.EMAIL))
        queries_made.add(QueryDataItem(query=query, type=QueryType.PHONE))
        queries_made.add(QueryDataItem(query=query, type=QueryType.FULLNAME))
        queries_made.add(QueryDataItem(query=query, type=QueryType.FIRSTNAME_LASTNAME))
        self.search_all(query=query)

        try:
            # Some modules automatically normalize phone numbers to E164, negating this additional query
            e164_query = phonenumbers.format_number(phonenumbers.parse(query, self.__default_country), phonenumbers.PhoneNumberFormat.E164)
            queries_made.add(QueryDataItem(query=e164_query, type=QueryType.PHONE))
        except (phonenumbers.phonenumberutil.NumberParseException, AttributeError):
            pass

        self.__in_recursion = True # Passed to runners so they can self-skip if spider-in disabled

        for i in range(depth):
            new_queries: set = set()

            new_queries.update(QueryDataItem(query=query, type=QueryType.USERNAME) for query in self.collector.get_unique_usernames(spiderable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.EMAIL) for query in self.collector.get_unique_emails(spiderable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.PHONE) for query in self.collector.get_unique_phones(spiderable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.FULLNAME) for query in self.collector.get_unique_fullnames(spiderable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.FIRSTNAME_LASTNAME) for query in self.collector.get_unique_firstname_middlename_lastname_groups(spiderable_only=True))

            new_queries -= queries_made
            queries_made.update(new_queries)

            for new_query in new_queries:
                if loglevel >= LogLevel.SUCCESS_ONLY.value:
                    print(f'{Fore.BLUE}{Style.BRIGHT}[{Fore.RESET}Depth {i+1}{Fore.BLUE}{Style.BRIGHT}]{Fore.RESET}{Style.RESET_ALL} {new_query.query}')
                self.search_all(query=new_query)

            if not no_deduplicate:
                self.collector.deduplicate()
