import json
from typing import Dict

import pandas as pd
import phonenumbers
import requests

from ..collector import Collector
from ..config import config
from ..errors import APIKeyError, IncompatibleQueryType, RequestError
from ..types import QueryType, SearchArgs


class Endato:
    def __init__(self, collector:Collector, api_name:str, api_key:str, country:str):
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
        self.collector:Collector = collector


    def _type(self, query:str) -> QueryType:
        try:
            phonenumbers.is_valid_number(phonenumbers.parse(query, self.__country))
            return QueryType.PHONE
        except phonenumbers.phonenumberutil.NumberParseException:
            pass

        raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')


    def accepts(self, search_args:SearchArgs) -> bool:
        """Determine if the search is supported by the module

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            bool -- True if the search is supported, False otherwise
        """
        if self.__country != 'US':
            # Not sure if Endato supports queries for non-US information
            return False

        if search_args.query_type != QueryType.PHONE:
            return False

        try:
            self._type(search_args.query)
        except IncompatibleQueryType:
            return False
        else:
            return True


    def _query_phone(self, query:str) -> pd.DataFrame:
        e164_query = phonenumbers.format_number(
            phonenumbers.parse(query, self.__country),
            phonenumbers.PhoneNumberFormat.E164,
        )
        readable_query = phonenumbers.format_number(
            phonenumbers.parse(query, self.__country),
            phonenumbers.PhoneNumberFormat.NATIONAL,
        )

        headers = self.__base_headers
        headers['galaxy-search-type'] = 'DevAPICallerID'
        values = {
            'Phone': readable_query,
            'Page': 1,
            'ResultsPerPage': 3,
        }

        response = requests.post(self.__api_url['phone'], headers=headers, data=values)
        if response.status_code != 200:
            raise RequestError(f'Failed to get results from Endato. Status code: {response.status_code}\n\n{response.text}')  # fmt: skip # noqa: E501
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
            'branch_recommended': True,
            'phone': e164_query,
        }
        new_data = pd.DataFrame([flattened_data])
        self.collector.insert(new_data)
        return new_data


    def search(self, search_args:SearchArgs) -> pd.DataFrame:  # type: ignore[return]
        """Initiate a search of Endato data

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            pd.DataFrame -- The results of the search
        """
        if search_args.in_recursion and not config['Target Options']['endato-branch-in']:
            return pd.DataFrame()

        if not self.__api_name or not self.__api_key:
            raise APIKeyError(key_not_provided=True)

        try:
            query_type = self._type(search_args.query)
        except IncompatibleQueryType:
            return pd.DataFrame()

        if query_type == QueryType.PHONE:
            return self._query_phone(search_args.query)
