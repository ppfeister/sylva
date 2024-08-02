import json
from typing import Dict, List

import pandas as pd
import requests
import phonenumbers

from ..helpers.generic import IncompatibleQueryType, QueryType, RequestError
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
    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        if query_type != QueryType.PHONE and query_type != QueryType.TEXT:
            return False

        try:
            return phonenumbers.is_valid_number(phonenumbers.parse(query, self.__country))
        except phonenumbers.phonenumberutil.NumberParseException:
            return False
    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        # TODO Should this integreation have a toggle for spidering?
        #if in_recursion and not config['Target Options']['veriphone-spider-in']:
        #    return pd.DataFrame()

        if not self.accepts(query):
            raise IncompatibleQueryType('Query unable to be parsed as phone number')
        
        e164_query = phonenumbers.format_number(phonenumbers.parse(query, self.__country), phonenumbers.PhoneNumberFormat.E164)

        sanitized_query = requests.utils.requote_uri(e164_query)
        response = requests.get(self.__api_url.format(KEY=self.__api_key, COUNTRY=self.__country, PHONE=sanitized_query))
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from ProxyNova. Status code: {response.status_code}')
        
        json_data:dict = json.loads(response.text)
        raw_rows:List[Dict] = [
            {
                'phone': json_data.get('e164', None),
                'country': json_data.get('country', None),
                'region': json_data.get('phone_region', None),
                'query': e164_query,
                'source_name': self.source_name,
                'spider_recommended': True,
            }
        ]
        self.collector.insert(pd.DataFrame(raw_rows))
        return pd.DataFrame(raw_rows)
