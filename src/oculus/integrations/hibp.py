from typing import Dict

import pandas as pd
import requests

from oculus import __user_agent__
from oculus.helpers.generic import APIKeyError, IncompatibleQueryType, QueryType


class HIBP:
    def __init__(self, collector:pd.DataFrame, api_key:str, country:str):
        self.__api_key:str = api_key
        self.__api_url:str = 'https://haveibeenpwned.com/api/v3/{service}/{parameter}'
        self.__generic_headers:Dict[str, str] = {
            'hibp-api-key': self.__api_key,
            'User-Agent': __user_agent__,
        }
        self.__debug_disable_tag:str = 'hibp'
        self.source_name:str = 'Have I Been Pwned'
        self.collector:pd.DataFrame = collector
        self.__rate_limit_per_minute:int


    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        if (
            query_type != QueryType.TEXT
            and query_type != QueryType.USERNAME
            and query_type != QueryType.EMAIL
            and query_type != QueryType.PHONE
        ):
            return False
        
        # TODO text validation?
        return True
    

    def status(self) -> str|Dict:
        api_url: str = self.__api_url.format(service='subscription', parameter='status')
        response = requests.get(api_url, headers=self.__generic_headers).json()
        self.__rate_limit_per_minute = response['rpm']
        return response

    
    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT) -> pd.DataFrame:
        if not self.accepts(query):
            raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')
        if not self.__api_key:
            raise APIKeyError(key_not_provided=True)
        
        self.status() # Rate limit is needing to be set

        api_url: str = self.__api_url.format(service='breaches', parameter=query)
        
        return pd.DataFrame()

