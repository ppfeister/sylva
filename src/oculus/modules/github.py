import re

import pandas as pd

from oculus.helpers.generic import QueryType
from oculus.collector import Collector


class GitHub:
    """Scrapes GitHub for data relating to a given username"""
    def __init__(self, collector:Collector, api_key:str):
        self.source_name:str = 'GitHub'
        self.collector:Collector = collector
        self.__username_validation_pattern: str = r'((?!.*(-){2,}.*)[a-z0-9][a-z0-9-]{0,38}[a-z0-9])'


    def accepts(self, query:str, query_type:str) -> bool:
        if query_type != QueryType.TEXT and query_type != QueryType.USERNAME:
            return False
        
        if not re.match(self.__username_validation_pattern, query):
            return False
        
        return True


    def search_commit_identities(self, username:str) -> pd.DataFrame:
        """Query GitHub for all identities associated with commits authored by a given username

        Keyword Arguments:
            username {str} -- The username to search for

        Returns:
            pd.DataFrame -- A DataFrame containing the results of the search
        """
        print(username)
        return pd.DataFrame()


    def search(self, query:str, in_recursion:bool=False, query_type:str=QueryType.TEXT) -> pd.DataFrame:
        self.search_commit_identities(username=query)
        return pd.DataFrame()
