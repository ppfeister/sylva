import time
from typing import List, NamedTuple

from colorama import Fore, Back, Style
import phonenumbers

from .collector import Collector
from .config import config
from .easy_logger import LogLevel, loglevel, NoColor, overwrite_previous_line
from .helpers.proxy import ProxySvc, test_if_flaresolverr_online
from .helpers.generic import (
    QueryType,
    RequestError,
    APIKeyError,
)
from .integrations import (
    endato,
    #proxynova, FIXME problems on certain queries that have multiple results
    #intelx,
    veriphone,
)
from .modules import (
    pgp as pgp_module,
    sherlock,
    github,
    voter,
)


class QueryDataItem(NamedTuple):
    """Query value and typographical data.

    The QueryDataItem is a simple dataclass that holds the query itself and the enumerated type.
    This helps make the distinction between simple strings, identitical dicts, and similar, more apparent to Sylva."""
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
            endato.Endato(collector=self.collector, api_name=config['Keys']['endato-name'], api_key=config['Keys']['endato-key'], country=self.__default_country),
            #intelx.IntelX(collector=self.collector, api_key=config['Keys']['intelx-key']),
            pgp_module.PGPModule(collector=self.collector),
            veriphone.Veriphone(collector=self.collector, api_key=config['Keys']['veriphone-key'], country=self.__default_country),
            sherlock.Sherlock(collector=self.collector),
            github.GitHub(collector=self.collector, api_key=config['Keys']['github-key']),
            voter.Voter(collector=self.collector),
        ]

        self.__proxy_svc:ProxySvc = ProxySvc()
        if config['General']['flaresolverr'] == 'True':
            self.__proxy_svc.start()
            self.__proxy_svc.start_primary_session()


    def __del__(self):
        if test_if_flaresolverr_online(proxy_url=self.__proxy_svc.primary_proxy_url):
            self.__proxy_svc.destroy_all_sessions()
        self.__proxy_svc.stop()


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
            if not runner.accepts(query=query, query_type=query_type):
                if loglevel >= LogLevel.DEBUG.value:
                    print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} Query type not supported by {runner.source_name}')
                continue

            if loglevel >= LogLevel.SUCCESS_ONLY.value:
                print(f'{Fore.LIGHTCYAN_EX}{Style.BRIGHT}[*]{Style.RESET_ALL}{Fore.RESET} Searching {runner.source_name}...')

            proxy_data:dict[str, str] = {
                'proxy_url': self.__proxy_svc.primary_proxy_url,
                'flaresolverr_session_id': self.__proxy_svc.primary_session_id,
            }

            try:
                # Each runner should return a DataFrame, but since that data is already
                # added to the collector, all we care about is the number of new rows.
                results = len(runner.search(query=query, in_recursion=self.__in_recursion, query_type=query_type, proxy_data=proxy_data).index)
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
                total_discovered += results
            except RequestError:
                pass
            except APIKeyError as e:
                if e.key_not_provided:
                    if loglevel >= LogLevel.INFO.value:
                        print(f'{Fore.LIGHTBLACK_EX}{Style.BRIGHT}[-]{Style.RESET_ALL}{Fore.RESET} API key has not been provided for {runner.source_name} - {runner.source_obtain_keys_url}')
        
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
            e164_query = phonenumbers.format_number(phonenumbers.parse(query, self.__default_country), phonenumbers.PhoneNumberFormat.E164)
            queries_made.add(QueryDataItem(query=e164_query, type=QueryType.PHONE))
        except (phonenumbers.phonenumberutil.NumberParseException, AttributeError):
            pass

        self.__in_recursion = True # Passed to runners so they can self-skip if branch-in disabled

        for i in range(depth):
            new_queries: set = set()

            new_queries.update(QueryDataItem(query=query, type=QueryType.USERNAME) for query in self.collector.get_unique_usernames(branchable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.EMAIL) for query in self.collector.get_unique_emails(branchable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.PHONE) for query in self.collector.get_unique_phones(branchable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.FULLNAME) for query in self.collector.get_unique_fullnames(branchable_only=True))
            new_queries.update(QueryDataItem(query=query, type=QueryType.FIRSTNAME_LASTNAME) for query in self.collector.get_unique_firstname_middlename_lastname_groups(branchable_only=True))

            new_queries -= queries_made
            queries_made.update(new_queries)

            for new_query in new_queries:
                if loglevel >= LogLevel.SUCCESS_ONLY.value:
                    print(f'{Fore.BLUE}{Style.BRIGHT}[{Fore.RESET}Depth {i+1}{Fore.BLUE}{Style.BRIGHT}]{Fore.RESET}{Style.RESET_ALL} {new_query.query}')
                if not self.search_all(query=new_query):
                    overwrite_previous_line()

            if not no_deduplicate:
                self.collector.deduplicate()

        self.__proxy_svc.stop()
