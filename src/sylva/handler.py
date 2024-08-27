import os
from typing import List, NamedTuple

import phonenumbers
from colorama import Fore, Style

from . import Collector
from .config import config
from .easy_logger import LogLevel, NoColor, loglevel, overwrite_previous_line
from .errors import APIKeyError, RequestError
from .helpers.proxy import ProxySvc
from .integrations import (
    endato,
    #proxynova, FIXME problems on certain queries that have multiple results
    #intelx,
    veriphone,
)
from .modules import (
    github,
    reddit,
    sherlock,
    voter,
)
from .modules import (
    pgp as pgp_module,
)
from .types import QueryType, SearchArgs


class QueryDataItem(NamedTuple):
    """Query value and typographical data.

    The QueryDataItem is a simple dataclass that holds the query itself and the enumerated type.
    This helps make the distinction between simple strings, identical dicts, and similar, more
    apparent to Sylva."""
    query: str
    type: QueryType


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor

class Handler:
    """Request handler with built-in helpers and proxy services

    Attributes:
        collector (Collector): Collector object to store results
        runners (List[Runner]): List of search modules to execute queries

    Example: Executing a simple string-based search
        ```python
        from sylva.handler import Handler

        handler = Handler()
        handler.branch_all('username')
        results = handler.collector.get_data() # Returns a DataFrame

        print(results)
        ```

    Example: Executing a search using a QueryDataItem
        ```python
        from sylva.handler import Handler, QueryDataItem
        from sylva.helpers.generic import QueryType

        handler = Handler()

        query = QueryDataItem(query='username', type=QueryType.USERNAME)
        handler.branch_all(query)
        results = handler.collector.get_data() # Returns a DataFrame

        print(results)
        ```
    """
    def __init__(self):
        self.collector:Collector = Collector()
        self.__default_country:str = 'US'
        self.__in_recursion = False
        self.runners:List = [
            #proxynova.ProxyNova(collector=self.collector),
            endato.Endato(collector=self.collector, api_name=config['Keys']['endato-name'], api_key=config['Keys']['endato-key'], country=self.__default_country),  # fmt: skip # noqa: E501
            #intelx.IntelX(collector=self.collector, api_key=config['Keys']['intelx-key']),
            pgp_module.PGPModule(collector=self.collector),
            veriphone.Veriphone(collector=self.collector, api_key=config['Keys']['veriphone-key'], country=self.__default_country),  # fmt: skip # noqa: E501
            sherlock.Sherlock(collector=self.collector),
            github.GitHub(collector=self.collector, api_key=config['Keys']['github-key']),
            reddit.Reddit(collector=self.collector),
            voter.Voter(collector=self.collector),
        ]

        self.__proxy_svc:ProxySvc = ProxySvc()
        if config['General']['flaresolverr'] == 'True' and os.environ.get('SYLVA_FLARESOLVERR', '') != 'False':
            self.__prepare_flaresolverr()


    def __del__(self):
        del self.__proxy_svc


    def __prepare_flaresolverr(self):
        """Attempt to start the proxy service and a common browser session"""
        try:
            if loglevel >= LogLevel.SUCCESS_ONLY.value:
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Starting proxy service...')
            self.__proxy_svc.start()
        except Exception:
            if loglevel >= LogLevel.ERROR.value:
                if loglevel <= LogLevel.SUCCESS_ONLY.value:
                    overwrite_previous_line()
                print(f'{Fore.LIGHTRED_EX}{Style.BRIGHT}[!]{Style.RESET_ALL}{Fore.RESET} {Style.DIM}Failed to start proxy service{Style.RESET_ALL}')  # fmt: skip # noqa: E501
        else:
            if loglevel >= LogLevel.INFO.value:
                overwrite_previous_line()
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Proxy service started')
            if loglevel >= LogLevel.SUCCESS_ONLY.value:
                if loglevel == LogLevel.SUCCESS_ONLY.value:
                    overwrite_previous_line()
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Starting browser session...')
            try:
                self.__proxy_svc.start_primary_session()
            except Exception:
                if loglevel >= LogLevel.ERROR.value:
                    if loglevel <= LogLevel.SUCCESS_ONLY.value:
                        overwrite_previous_line()
                    print(f'{Fore.LIGHTRED_EX}{Style.BRIGHT}[!]{Style.RESET_ALL}{Fore.RESET} {Style.DIM}Failed to start proxy browser session{Style.RESET_ALL}')  # fmt: skip # noqa: E501
            else:
                if loglevel >= LogLevel.SUCCESS_ONLY.value:
                    overwrite_previous_line()
                if loglevel >= LogLevel.INFO.value:
                    print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Browser session started')


    def search_all(self, query:str|QueryDataItem, no_deduplicate:bool=False) -> int:
        """Search all available modules for the given query

        Runs a single-depth search for a given query across all available modules and
            integrations, automatically deduplicating the results. Results are added to
            the object's collector.

        Args:
            query (str|QueryDataItem): The query to search for
            no_deduplicate (bool, optional): Skip deduplication for manual processing.
                Defaults to False.

        Returns:
            int: The number of identities discovered
        """
        if isinstance(query, QueryDataItem):
            query_type:QueryType = query.type
            query:str = query.query
        else:
            query_type = QueryType.TEXT

        total_discovered: int = 0

        for runner in self.runners:
            search_args: SearchArgs = SearchArgs(
                    query=query,
                    in_recursion=self.__in_recursion,
                    query_type=query_type,
                    proxy_data={
                        'proxy_url': self.__proxy_svc.primary_proxy_url,
                        'flaresolverr_session_id': self.__proxy_svc.primary_session_id,
                    },
                )

            if not runner.accepts(search_args=search_args):
                if loglevel >= LogLevel.DEBUG.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Query type not supported by {runner.source_name}')  # fmt: skip # noqa: E501
                continue

            if loglevel >= LogLevel.SUCCESS_ONLY.value:
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Searching {runner.source_name}...')  # fmt: skip # noqa: E501

            try:
                # Each runner should return a DataFrame, but since that data is already
                # added to the collector, all we care about is the number of new rows.
                results = len(
                    runner.search(search_args=search_args).index
                    )

                if loglevel < LogLevel.DEBUG.value:
                    overwrite_previous_line()
                if loglevel >= LogLevel.SUCCESS_ONLY.value and results > 0:
                    print(f'{Fore.LIGHTGREEN_EX}{Style.BRIGHT}[+]{Style.RESET_ALL}{Fore.RESET} Found {results} via {runner.source_name}')  # fmt: skip # noqa: E501
                elif loglevel >= LogLevel.INFO.value and results == 0:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} No results found via {runner.source_name}')  # fmt: skip # noqa: E501

                total_discovered += results

            except RequestError as e:
                if loglevel <= LogLevel.DEBUG.value:
                    overwrite_previous_line()

                if loglevel >= LogLevel.INFO.value:
                    if e.rate_limit_exceeded:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Rate limit exceeded with {runner.source_name}')  # fmt: skip # noqa: E501
                    else:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Something unexpected happened with {runner.source_name}')  # fmt: skip # noqa: E501

                if loglevel >= LogLevel.DEBUG.value:
                    print(e)

            except APIKeyError as e:
                if loglevel <= LogLevel.DEBUG.value:
                    overwrite_previous_line()
                if e.key_not_provided:
                    if loglevel >= LogLevel.INFO.value:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} API key has not been provided for {runner.source_name} - {runner.source_obtain_keys_url}')  # fmt: skip # noqa: E501

        if not no_deduplicate:
            self.collector.deduplicate()

        return total_discovered

    def branch_all(self, query: str, depth: int = 1, no_deduplicate: bool = False):
        """Recursively search all available modules for the given query

        Runs a variable-depth search for a given query across all available modules and
            integrations, automatically deduplicating the results. Results are added to
            the object's collector.

        Args:
            query (str): The query to search for
            depth (int, optional): The depth to search. Defaults to 1.
            no_deduplicate (bool, optional): Skip deduplication for manual processing.
                Defaults to False.
        """
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
            e164_query = phonenumbers.format_number(phonenumbers.parse(query, self.__default_country), phonenumbers.PhoneNumberFormat.E164)  # fmt: skip # noqa: E501
            queries_made.add(QueryDataItem(query=e164_query, type=QueryType.PHONE))
        except (phonenumbers.phonenumberutil.NumberParseException, AttributeError):
            pass

        self.__in_recursion = True # Passed to runners so they can self-skip if branch-in disabled

        for i in range(depth):
            new_queries: set = set()

            new_queries.update(QueryDataItem(query=query, type=QueryType.USERNAME) for query in self.collector.get_unique_usernames(branchable_only=True))  # fmt: skip # noqa: E501
            new_queries.update(QueryDataItem(query=query, type=QueryType.EMAIL) for query in self.collector.get_unique_emails(branchable_only=True))  # fmt: skip # noqa: E501
            new_queries.update(QueryDataItem(query=query, type=QueryType.PHONE) for query in self.collector.get_unique_phones(branchable_only=True))  # fmt: skip # noqa: E501
            new_queries.update(QueryDataItem(query=query, type=QueryType.FULLNAME) for query in self.collector.get_unique_fullnames(branchable_only=True))  # fmt: skip # noqa: E501
            new_queries.update(QueryDataItem(query=query, type=QueryType.FIRSTNAME_LASTNAME) for query in self.collector.get_unique_fullname_groups(branchable_only=True))  # fmt: skip # noqa: E501

            new_queries -= queries_made
            queries_made.update(new_queries)

            for new_query in new_queries:
                if loglevel >= LogLevel.SUCCESS_ONLY.value:
                    depth_str:str = ''
                    if loglevel >= LogLevel.INFO.value:
                        depth_str = f' {i+1}' # Only show depth if verbosity above SUCCESS_ONLY
                    print(f'{Fore.BLUE}{Style.BRIGHT}[Branch{depth_str}]{Fore.RESET}{Style.RESET_ALL} {new_query.query}')  # fmt: skip # noqa: E501
                if not self.search_all(query=new_query):
                    overwrite_previous_line()

            if not no_deduplicate:
                self.collector.deduplicate()

        self.__proxy_svc.stop()
