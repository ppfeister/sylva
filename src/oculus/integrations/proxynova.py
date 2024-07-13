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
        self.collector:Collector = collector
    # TODO add validation for username, email, password
    def search(self, query:str, start:int=0, end:int=config['Target Options']['proxycheck-default-limit']) -> pd.DataFrame:
        if self.__debug_disable_tag in config['Debug']['disabled_modules']:
            return
        query = requests.utils.requote_uri(query)
        response = requests.get(self.__api_url.format(QUERY=query, START=start, END=end))
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from ProxyNova. Status code: {response.status_code}')
        json_data:dict = json.loads(response.text)
        rows = [line.split(':') if ':' in line else [line, None] for line in json_data['lines']] # ugly but functional
        new_data = pd.DataFrame(rows[:1], columns=['email', 'password'])
        new_data['query'] = query
        new_data['source_name'] = self.source_name
        new_data['spider_recommended'] = config['Target Options']['proxycheck-spider-out']
        self.collector.insert(new_data)
        return new_data
    #def accepts(self, query:str) -> bool:
