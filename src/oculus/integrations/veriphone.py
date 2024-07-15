import json
from typing import Dict, List

import pandas as pd
import requests
import phonenumbers

from ..helpers.helpers import IncompatibleQueryType, RequestError
from ..collector import Collector


class Veriphone:
    def __init__(self, collector:Collector, api_key:str, country:str):
        self.__api_url:str = 'https://api.veriphone.io/v2/verify?key={KEY}&default_country={COUNTRY}&phone={PHONE}'
        self.__api_key:str = api_key
        self.__country:str = country
        self.__debug_disable_tag:str = 'veriphone'
        self.source_name:str = 'Veriphone'
        self.source_obtain_keys_url:str = 'https://veriphone.io/cp'
        self.collector:Collector = collector
    # TODO add validation for username, email, password
    def accepts(self, query:str) -> bool:
        return phonenumbers.is_valid_number(phonenumbers.parse(query, self.__country))
    def search(self, query:str) -> pd.DataFrame:
        if not self.accepts(query):
            raise IncompatibleQueryType(f'Query unable to be parsed as phone number')
        sanitized_query = requests.utils.requote_uri(query)
        response = requests.get(self.__api_url.format(KEY=self.__api_key, COUNTRY=self.__country, PHONE=sanitized_query))
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from ProxyNova. Status code: {response.status_code}')
        
        json_data:dict = json.loads(response.text)
        raw_rows:List[Dict] = [
            {
                'phone': json_data.get('e164', None),
                'country': json_data.get('country', None),
                'region': json_data.get('phone_region', None),
                'query': query,
                'source_name': self.source_name,
                'spider_recommended': False,
            }
        ]
        self.collector.insert(pd.DataFrame(raw_rows))
        return pd.DataFrame(raw_rows)

        print(json_data)

        sanitized_query = requests.utils.requote_uri(query)
        response = requests.get(self.__api_url.format(QUERY=sanitized_query, START=start, END=end))
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
