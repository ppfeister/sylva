import json
from typing import Dict

import pandas as pd
import phonenumbers
import requests

from ..config import config
from ..helpers.generic import QueryType, RequestError, IncompatibleQueryType, APIKeyError


class Endato:
    def __init__(self, collector:pd.DataFrame, api_name:str, api_key:str, country:str):
        self.__api_name:str = api_name
        self.__api_key:str = api_key
        self.__api_url:Dict[str, str] = {
            'phone': 'https://devapi.endato.com/phone/enrich',
            'pro': '',
        }
        self.__debug_disable_tag:str = 'endato'
        self.__country:str = country
        self.__base_headers:Dict[str, str] = {
            'Accept': 'application/json',
            'galaxy-ap-name': self.__api_name,
            'galaxy-ap-password': self.__api_key,
        }
        self.source_obtain_keys_url:str = 'https://api.endato.com/Keys'
        self.source_name:str = 'Endato'
        self.collector:pd.DataFrame = collector


    def _type(self, query:str) -> str:
        try:
            phonenumbers.is_valid_number(phonenumbers.parse(query, self.__country))
            return QueryType.PHONE
        except phonenumbers.phonenumberutil.NumberParseException:
            pass

        raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')
    

    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        if self.__country != 'US':
            # Not sure if Endato supports queries for non-US information
            return False
        
        if query_type != QueryType.PHONE and query_type != QueryType.TEXT:
            return False
        
        try:
            self._type(query)
        except IncompatibleQueryType:
            return False
        else:
            return True
        

    def _query_phone(self, query:str) -> pd.DataFrame:
        e164_query = phonenumbers.format_number(phonenumbers.parse(query, self.__country), phonenumbers.PhoneNumberFormat.E164)
        readable_query = phonenumbers.format_number(phonenumbers.parse(query, self.__country), phonenumbers.PhoneNumberFormat.NATIONAL)

        headers = self.__base_headers
        headers['galaxy-search-type'] = 'DevAPICallerID'
        values = {
            'Phone': readable_query,
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
            'query': e164_query,
            'spider_recommended': True,
            'phone': e164_query,
        }
        new_data = pd.DataFrame([flattened_data])
        self.collector.insert(new_data)
        return new_data


    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        if in_recursion and not config['Target Options']['endato-spider-in']:
            return pd.DataFrame()
        
        if not self.__api_name or not self.__api_key:
            raise APIKeyError(key_not_provided=True)
        
        try:
            query_type = self._type(query)
        except IncompatibleQueryType:
            return pd.DataFrame()
        
        if query_type == QueryType.PHONE:
            return self._query_phone(query)
