import asyncio
import re
import time
from typing import Dict, List, NamedTuple

import aiohttp
import pandas as pd
import requests

from .. import Collector
from ..errors import IncompatibleQueryType
from ..types import QueryType, SearchArgs


class IdentItem(NamedTuple):
    full_name: str
    email: str
    source_name: str
    query: str
    username: str
    branch_recommended: bool
    platform_name: str
    platform_url: str

class GitHub:
    """Scrapes GitHub for data relating to a given username"""
    def __init__(self, collector:Collector, api_key:str):
        self.source_name:str = 'GitHub'
        self.collector:Collector = collector
        self.__username_validation_pattern: str = r'^((?!.*(-){2,}.*)[a-z0-9][a-z0-9-]{0,38}[a-z0-9])$'
        self.__email_validation_pattern: str = r'^[^@]+@[^@]+\.[^@]+$'
        self.__page_length:int = 100
        self.__maximum_query_depth:int = 1000 # Search api only provides 1000 results currently
        self.__api_endpoint_commit_search:str = 'https://api.github.com/search/commits?sort=author-date&order={ORDER}&per_page={PAGE_LEN}&q=author:{USERNAME}&page=<PAGE>'
        self.__api_endpoint_account_search:str = 'https://api.github.com/search/users?q={QUERY}'
        self.__generic_headers:Dict[str, str] = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        if api_key != '':
            self.__generic_headers['Authorization'] = f'Bearer {api_key}'


    async def __get_page(self, session:aiohttp.ClientSession, url:str, headers:Dict[str, str]):  # type: ignore[no-untyped-def] # (unk. return type)
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                if response.status == 422: # username not found
                    return None
                # TODO status code specific handling? is that needed?
                return None


    async def __get_pages(self, url:str):  # type: ignore[no-untyped-def]
        # TODO Check for number of actually populated pages if account < maximum_query_depth values
        # Without this check, rate limit may be exceeded more quickly
        async with aiohttp.ClientSession() as session:
            tasks = []

            for page in range(1, (self.__maximum_query_depth // self.__page_length) + 1):
                url = url.replace('<PAGE>', str(page))
                tasks.append(self.__get_page(session=session, url=url, headers=self.__generic_headers))

            results = await asyncio.gather(*tasks)
            filtered_results = [result for result in results if result is not None]
            return filtered_results


    def __type(self, query:str) -> QueryType:
        """Determine the type of query based on the query string

        Keyword Arguments:
            query {str} -- The query to check

        Returns:
            QueryType -- The type of query
        """
        if re.match(self.__username_validation_pattern, query):
            return QueryType.USERNAME
        elif re.match(self.__email_validation_pattern, query):
            return QueryType.EMAIL
        elif isinstance(query, str):
            # TODO Not sure if there's a better way to check for full names without regional issues
            return QueryType.TEXT
        else:
            raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')


    def accepts(self, search_args:SearchArgs) -> bool:
        """Determine if the search is supported by the module

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            bool -- True if the search is supported, False otherwise
        """
        if (
            search_args.query_type != QueryType.TEXT
            and search_args.query_type != QueryType.USERNAME
            and search_args.query_type != QueryType.EMAIL
            and search_args.query_type != QueryType.FULLNAME
            and search_args.query_type != QueryType.FIRSTNAME_LASTNAME
        ):
            return False

        try:
            self.__type(search_args.query)
        except IncompatibleQueryType:
            return False

        return True


    def search_commits_by_username(self, username:str, ignore_noreply:bool=False) -> pd.DataFrame:
        """Query GitHub for all identities associated with commits authored by a given username

        Keyword Arguments:
            username {str} -- The username to search for

        Returns:
            pd.DataFrame -- A DataFrame containing the results of the search
        """

        pages: List = []
        data: set = set()

        for order in ['desc', 'asc']:
            url = self.__api_endpoint_commit_search.format(PAGE_LEN=self.__page_length, USERNAME=username, ORDER=order )
            loop = asyncio.get_event_loop()
            pages.extend(loop.run_until_complete(self.__get_pages(url=url)))

        for page in pages:
            for item in page['items']:
                data.add(IdentItem(
                    full_name = item['commit']['author']['name'],
                    email = item['commit']['author']['email'],
                    source_name = 'GitHub Commits',
                    username = username,
                    query = username,
                    branch_recommended = True,
                    platform_name = 'GitHub',
                    platform_url = f'https://github.com/{username}',
                ))

        # data starts out as a set for on-the-fly deduplication --- this type difference is intentional
        data: List[IdentItem] = list(data)  # type: ignore[no-redef] # TODO: Make redef unnecessary through double cast
        new_data = pd.DataFrame(data)

        # clean up the data a bit
        if ignore_noreply:
            mask = ~new_data['email'].str.contains('@users.noreply.github.com')
            new_data = new_data[mask]

        return new_data


    def search_accounts_by_keyword(
            self,
            username:str|None=None,
            email:str|None=None,
            full_name:str|None=None
        ) -> pd.DataFrame:

        if username is None and email is None and full_name is None:
            raise ValueError('At least one of username, email, or full_name must be provided')

        query:str|None = None

        if username is not None:
            if email is not None or full_name is not None:
                raise ValueError('Only one of username, email, or full_name may be provided')
            url = self.__api_endpoint_account_search.format(QUERY=username)
            query = username
        elif email is not None:
            if full_name is not None:
                raise ValueError('Only one of username, email, or full_name may be provided')
            url_encoded_email = requests.utils.requote_uri(email)
            url = self.__api_endpoint_account_search.format(QUERY=url_encoded_email)
            query = email
        elif full_name is not None:
            url_encoded_full_name = requests.utils.requote_uri(full_name)
            url = self.__api_endpoint_account_search.format(QUERY=url_encoded_full_name)
            query = full_name

        new_data: set = set()

        r = requests.get(url)
        if r.status_code != 200:
            return pd.DataFrame()
        data_raw = r.json()
        for item in data_raw['items']:
            if item['type'] != 'User':
                # TODO Should we process organizational accounts?
                continue
            profile_data_url = item['url']

            for attempt in range(3):
                profile_data = requests.get(profile_data_url)
                if profile_data.status_code == 200:
                    break
                if (
                    profile_data.status_code == 429
                    or (
                        profile_data.status_code == 403
                        and profile_data.json()['message'].startswith('API rate limit exceeded')
                    )
                ):
                    # TODO Header X-RateLimit-Reset may be worth investigating (epoch time)
                    time.sleep(5)
            else:
                continue

            profile_data = profile_data.json()
            email_found = profile_data['email'] if email is None else email  # type: ignore[index]
            new_data.add(IdentItem(
                full_name = profile_data['name'],  # type: ignore[index]
                username = profile_data['login'],  # type: ignore[index]
                email = email_found,
                source_name = self.source_name,
                query = query,  # type: ignore[arg-type] # TODO: Refactor to use en empty string or QDI rather than None
                branch_recommended = True,
                platform_name = 'GitHub',
                platform_url = profile_data['html_url'],  # type: ignore[index]
            ))

        return pd.DataFrame(new_data)


    def search(self, search_args:SearchArgs) -> pd.DataFrame:
        """Initiate a search of GitHub data

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            pd.DataFrame -- The results of the search
        """
        if search_args.query_type is None or search_args.query_type == QueryType.TEXT:
            search_args.query_type = self.__type(search_args.query)

        all_new_data: pd.DataFrame = pd.DataFrame()

        if search_args.query_type == QueryType.USERNAME:
            results_by_username: pd.DataFrame = self.search_commits_by_username(username=search_args.query)
            all_new_data = pd.concat([all_new_data, results_by_username], ignore_index=True)

        if search_args.query_type == QueryType.EMAIL:
            results_by_email: pd.DataFrame = self.search_accounts_by_keyword(email=search_args.query)
            all_new_data = pd.concat([all_new_data, results_by_email], ignore_index=True)

        if (
            search_args.query_type == QueryType.FULLNAME
            or search_args.query_type == QueryType.TEXT
            or search_args.query_type == QueryType.FIRSTNAME_LASTNAME
        ):
            if search_args.query_type == QueryType.FIRSTNAME_LASTNAME:
                search_args.query = search_args.query.join(' ')
            results_by_fullname: pd.DataFrame = self.search_accounts_by_keyword(full_name=search_args.query)
            if len(results_by_fullname.index) < 2: # Generic "full name" searches can be noisy
                all_new_data = pd.concat([all_new_data, results_by_fullname], ignore_index=True)

        self.collector.insert(all_new_data)

        return all_new_data
