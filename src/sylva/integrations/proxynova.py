import json
import pandas as pd
import requests

from ..config import config
from ..helpers.generic import IncompatibleQueryType, QueryType, RequestError
from ..collector import Collector


class ProxyNova:
    def __init__(self, collector:Collector):
        self.__api_url:str = 'https://api.proxynova.com/comb?query={QUERY}&start={START}&limit={END}'
        self.__debug_disable_tag:str = 'proxynova'
        self.source_name:str = 'ProxyNova'
        self.collector:Collector = collector

    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        # TODO add validation for username, email, password
        if isinstance(query, str):
            return True
        return False

    def search(self, query:str, start:int=0, end:int=config['Target Options']['proxynova-default-limit'], in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        if in_recursion and not config['Target Options']['proxynova-spider-in']:
            return pd.DataFrame()
        
        if not self.accepts(query=query):
            raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')
        
        sanitized_query = requests.utils.requote_uri(query)
        response = requests.get(self.__api_url.format(QUERY=sanitized_query, START=start, END=end))
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from ProxyNova. Status code: {response.status_code}')
        json_data:dict = json.loads(response.text)
        rows = [line.split(':') if ':' in line else [line, None] for line in json_data['lines']] # ugly but functional
        new_data = pd.DataFrame(rows[:1], columns=['email', 'password'])
        new_data['query'] = query
        new_data['source_name'] = self.source_name
        new_data['spider_recommended'] = bool(config['Target Options']['proxynova-spider-out'])
        self.collector.insert(new_data)
        return new_data
