from typing import List
import pandas as pd

from .helpers.generic import ResultDataFrame

class Collector:
    def __init__(self):
        self.__data:ResultDataFrame = ResultDataFrame()


    def insert(self, new_data:ResultDataFrame):
        self.__data.insert_frame(new_data)


    def get_data(self) -> pd.DataFrame:
        return self.__data.get_data()
    

    def deduplicate(self) -> pd.DataFrame:
        return self.__data.deduplicate()
    

    def get_unique_queries(self, spiderable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        return df['query'].dropna().unique().tolist()
    def get_unique_usernames(self, spiderable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        return df['username'].dropna().unique().tolist()
    def get_unique_emails(self, spiderable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        return df['email'].dropna().unique().tolist()
    def get_unique_phones(self, spiderable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        return df['phone'].dropna().unique().tolist()
    def get_unique_fullnames(self, spiderable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        return df['full_name'].dropna().unique().tolist()
    def get_unique_firstname_middlename_lastname_groups(self, spiderable_only:bool=False) -> set[tuple[str, str, str]]:
        df = self.__data.get_data()
        if spiderable_only:
            df = df[df['spider_recommended'] == True]
        filtered_df = df.dropna(subset=['first_name', 'last_name'])
        filtered_data = set(zip(filtered_df['first_name'], filtered_df['middle_name'], filtered_df['last_name']))
        return filtered_data
