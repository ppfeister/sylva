import json
import pathlib
from typing import Dict
import pandas as pd
import requests

from .. import __github_raw_data_url__
from ..config import config
from ..helpers.helpers import RequestError
from ..collector import Collector


class TargetInformation:
    def __init__(self):
        self._local_manifest_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/gpg.json'
        self._local_schema_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/gpg.schema.json'
        self._remote_manifest_uri = __github_raw_data_url__

        r = requests.get(self._remote_manifest_uri)
        if r.status_code != 200:
            with open(self._local_manifest_uri, 'r') as f:
                self.targets:Dict = json.load(f)
        else:
            # TODO add validation against discovered schema version number
            self.targets:Dict = json.loads(r.text)


class PGPModule:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'pgp'
        self.source_name:str = 'GPG'
        self.collector:Collector = collector
        self.targets:TargetInformation = TargetInformation()
    # TODO add validation for username, email, password
    def search(self, query:str) -> pd.DataFrame:
        pass
    def oldsearch(self, query:str, start:int=0, end:int=config['Target Options']['proxycheck-default-limit']) -> pd.DataFrame:
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
