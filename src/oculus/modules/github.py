import asyncio
import re
from typing import Dict, List, NamedTuple, Tuple

import aiohttp
import pandas as pd

from oculus.helpers.generic import QueryType
from oculus.collector import Collector


class IdentItem(NamedTuple):
    full_name: str
    email: str
    source_name: str
    query: str
    spider_recommended: bool
    platform_name: str
    platform_url: str

class GitHub:
    """Scrapes GitHub for data relating to a given username"""
    def __init__(self, collector:Collector, api_key:str):
        self.source_name:str = 'GitHub'
        self.collector:Collector = collector
        self.__username_validation_pattern: str = r'((?!.*(-){2,}.*)[a-z0-9][a-z0-9-]{0,38}[a-z0-9])'
        self.__page_length:int = 100
        self.__maximum_query_depth:int = 1000 # Search api only provides 1000 results currently
        self.__api_endpoint:str = 'https://api.github.com/search/commits?sort=author-date&order={ORDER}&per_page={PAGE_LEN}&q=author:{USERNAME}&page=<PAGE>'
        self.__generic_headers:Dict[str, str] = {
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        }

        if api_key != '':
            self.__generic_headers['Authorization'] = f'Bearer {api_key}'

    
    async def __get_page(self, session:aiohttp.ClientSession, url:str, headers:Dict[str, str]):
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f'Failed to get results from GitHub. Status code: {response.status}')
                return None
            
    async def __get_pages(self, url:str):
        async with aiohttp.ClientSession() as session:
            tasks = []

            for page in range(1, (self.__maximum_query_depth // self.__page_length) + 1):
                url = url.replace('<PAGE>', str(page))
                tasks.append(self.__get_page(session=session, url=url, headers=self.__generic_headers))

            results = await asyncio.gather(*tasks)
            filtered_results = [result for result in results if result is not None]
            return filtered_results


    def accepts(self, query:str, query_type:str) -> bool:
        if query_type != QueryType.TEXT and query_type != QueryType.USERNAME:
            return False
        
        if not re.match(self.__username_validation_pattern, query):
            return False
        
        return True


    def search_commit_identities(self, username:str, ignore_noreply:bool=False) -> pd.DataFrame:
        """Query GitHub for all identities associated with commits authored by a given username

        Keyword Arguments:
            username {str} -- The username to search for

        Returns:
            pd.DataFrame -- A DataFrame containing the results of the search
        """

        pages: List = []
        data: set = set()

        for order in ['desc', 'asc']:
            url = self.__api_endpoint.format(PAGE_LEN=self.__page_length, USERNAME=username, ORDER=order )
            loop = asyncio.get_event_loop()
            pages.extend(loop.run_until_complete(self.__get_pages(url=url)))

        for page in pages:
            for item in page['items']:
                data.add(IdentItem(
                    full_name = item['commit']['author']['name'],
                    email = item['commit']['author']['email'],
                    source_name = self.source_name,
                    query = username,
                    spider_recommended = True,
                    platform_name = 'GitHub',
                    platform_url = f'https://github.com/{username}',
                ))

        # data starts out as a set for on-the-fly deduplication --- this type difference is intentional
        data: List[IdentItem] = list(data)
        new_data = pd.DataFrame(data)

        # clean up the data a bit
        if ignore_noreply:
            mask = ~new_data['email'].str.contains('@users.noreply.github.com')
            new_data = new_data[mask]

        return new_data


    def search(self, query:str, in_recursion:bool=False, query_type:str=QueryType.TEXT) -> pd.DataFrame:
        all_new_data: pd.DataFrame = pd.DataFrame()

        results_by_username: pd.DataFrame = self.search_commit_identities(username=query)
        
        all_new_data = pd.concat([all_new_data, results_by_username], ignore_index=True)

        self.collector.insert(results_by_username)

        return all_new_data
