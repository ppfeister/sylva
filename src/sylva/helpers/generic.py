from enum import Enum
import hashlib
import os
from typing import Dict
from urllib.parse import urlunparse, urlparse

import pandas as pd
import requests
from tldextract import extract as tldx

from sylva import __github_maintainer_url__

class RequestError(Exception):
    pass
class IncompatibleQueryType(Exception):
    pass
class APIKeyError(Exception):
    def __init__(self, message:str=None, key_not_provided:bool=False):
        super().__init__(message)
        self.key_not_provided = key_not_provided


class QueryType(Enum):
    TEXT = 0
    EMAIL = 1
    PHONE = 2
    USERNAME = 3
    FULLNAME = 4
    FIRSTNAME = 5
    LASTNAME = 6
    FIRSTNAME_LASTNAME = 7


ref_list: Dict[str, str] = {
    'ref_a': '14fc468bc4ac40a22ae70106b351d1ce',
}
    

class ResultDataFrame:
    def __init__(self):
        self.data = pd.DataFrame(
            columns=[
                'query',
                'source_name',
                'spider_recommended',
                'platform_name',
                'platform_url',
                'username',
                'email',
                'phone',
                'password',
                'age',
                'sex',
                'first_name',
                'middle_name',
                'last_name',
                'full_name',
                'birth_year',
                'birth_month',
                'birth_day',
                'street',
                'unit',
                'city',
                'region',
                'postal_code',
                'country',
                'raw_address',
                'comment',
                ]
        )
        pd.set_option('display.max_rows', None)
    def __str__(self) -> str:
        return self.data.__str__()
    def insert_frame(self, new_data:pd.DataFrame) -> pd.DataFrame:
        self.data = pd.concat([self.data, new_data], ignore_index=True)
        return self.data
    def get_data(self) -> pd.DataFrame:
        return self.data
    def deduplicate(self) -> pd.DataFrame:
        self.data = self.data.drop_duplicates()
        return self.data

def compare_to_known(query: str, id: str) -> bool:
    if os.environ.get('SYLVA_COMPARATOR', 'True') == 'False':
        return False
    if hashlib.sha256(query.replace(' ', '').lower().encode('utf-8')).hexdigest() in requests.get(url=f'{urlunparse(urlparse(__github_maintainer_url__)._replace(netloc=f'gist.{tldx(__github_maintainer_url__).domain}.{tldx(__github_maintainer_url__).suffix}'))}/{id}/raw').text:
        return True
    return False
