import json
import pandas as pd
import requests

from ..config import config
from .__helpers import RequestError
from ..collector import Collector


class ProxyNova:
    def __init__(self, collector:Collector):
        self.__api_url:str = 'https://api.proxynova.com/comb?query={QUERY}&start={START}&limit={END}'
        self.__debug_disable_tag:str = 'proxynova'
        self.spider_recommended:bool = False
        self.source_name:str = 'ProxyNova'
        self.description:str = 'Free API to search the COMB combo list (3.2 billion entries)'
        self.collector:Collector = collector
    def search(self, query:str, start:int=0, end:int=5) -> pd.DataFrame:
        print(self.__api_url.format(QUERY=query, START=start, END=end))
        if self.__debug_disable_tag in config['Debug']['disabled_modules']:
            return
        query = requests.utils.requote_uri(query)
        response = requests.get(self.__api_url.format(QUERY=query, START=start, END=end))
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from ProxyNova. Status code: {response.status_code}')
        json_data:dict = json.loads(response.text)
        rows = [line.split(':') if ':' in line else [line, None] for line in json_data['lines']] # ugly but functional
        new_data = pd.DataFrame(rows, columns=['email', 'password'])
        new_data['query'] = query
        new_data['source_name'] = self.source_name
        new_data['source_description'] = self.description
        new_data['spider_recommended'] = self.spider_recommended
        self.collector.insert(new_data)
        return new_data
