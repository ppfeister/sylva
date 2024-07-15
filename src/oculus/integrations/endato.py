import json
import re
from typing import Dict

import pandas as pd
import requests

from ..helpers.helpers import RequestError, IncompatibleQueryType, APIKeyError


class Endato:
    def __init__(self, collector:pd.DataFrame, api_name:str, api_key:str):
        self.__api_name:str = api_name
        self.__api_key:str = api_key
        self.__api_url:Dict[str, str] = {
            'phone': 'https://devapi.endato.com/phone/enrich',
            'pro': '',
        }
        self.__debug_disable_tag:str = 'endato'
        self.__base_headers:Dict[str, str] = {
            'Accept': 'application/json',
            'galaxy-ap-name': self.__api_name,
            'galaxy-ap-password': self.__api_key,
        }
        self.source_obtain_keys_url:str = 'https://api.endato.com/Keys'
        self.source_name:str = 'Endato'
        self.collector:pd.DataFrame = collector
    def _type(self, query:str) -> str:
        pattern = r'^\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$'
        if re.match(pattern, query):
            return 'phone'
        raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')
    def accepts(self, query:str) -> bool:
        try:
            self._type(query)
        except IncompatibleQueryType:
            return False
        else:
            return True
    def _query_phone(self, query:str) -> pd.DataFrame:
        headers = self.__base_headers
        headers['galaxy-search-type'] = 'DevAPICallerID'
        values = {
            'Phone': query,
            'Page': 1,
            'ResultsPerPage': 3,
        }
        response = requests.post(self.__api_url['phone'], headers=headers, data=values)
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from Endato. Status code: {response.status_code}\n\n{response.text}')
        json_data:dict = json.loads(response.text)
        flattened_data:dict = {
            'first_name': json_data['person']['name']['firstName'],
            'middle_name': json_data['person']['name']['middleName'],
            'last_name': json_data['person']['name']['lastName'],
            'age': json_data['person']['age'],
            'street': json_data['person']['address']['street'],
            'unit': json_data['person']['address']['unit'],
            'city': json_data['person']['address']['city'],
            'region': json_data['person']['address']['state'],
            'zip': json_data['person']['address']['zip'],
            'email': json_data['person']['email'],
            'source_name': self.source_name,
            'query': query,
            'spider_recommended': False,
            'phone': query,
        }
        new_data = pd.DataFrame([flattened_data])
        self.collector.insert(new_data)
        return new_data
    def search(self, query:str) -> pd.DataFrame:
        if not self.__api_name or not self.__api_key:
            raise APIKeyError(key_not_provided=True)
        try:
            query_type = self._type(query)
        except IncompatibleQueryType:
            return pd.DataFrame()
        if query_type == 'phone':
            return self._query_phone(query)
