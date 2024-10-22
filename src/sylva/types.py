from dataclasses import dataclass
from enum import Enum

import pandas as pd


class QueryType(Enum):
    """Used to more consistently define the type of a query"""
    TEXT = 'Simple'
    EMAIL = 'Email'
    PHONE = 'Phone'
    USERNAME = 'Username'
    FULLNAME = 'Full Name'
    FIRSTNAME = 'First Name'
    LASTNAME = 'Last Name'
    FIRSTNAME_LASTNAME = 'Divided Name'

@dataclass
class SearchArgs:
    """Enumerated arguments for built in search functions

    Attributes:
        query (str): The query to search for
        in_recursion (bool): Whether or not the search is being performed recursively
        query_type (QueryType): The type of query being searched for
        proxy_data (dict[str, str]): Proxy data to use for the search
    """
    query: str
    in_recursion: bool = False
    query_type: QueryType = QueryType.TEXT
    proxy_data: dict[str, str]|None = None


class ResultDataFrame:
    """Structured DataFrame for result handling

    This object should rarely be interacted with directly, but the structure is
        valuable knowledge to have as returned DataFrames will be of this type.

    Attributes:
        data (pd.DataFrame): The internal DataFrame object

    Methods:
        insert_frame: Insert a new DataFrame into the collector
        get_data: Returns a Pandas DataFrame of the collected results
        deduplicate: Deduplicate the collected results
    """
    def __init__(self) -> None:
        self.data: pd.DataFrame = pd.DataFrame(
            columns=[
                'query',
                'source_name',
                'branch_recommended',
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
