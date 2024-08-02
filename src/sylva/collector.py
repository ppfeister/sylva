from typing import List
import pandas as pd

from .helpers.generic import ResultDataFrame

class Collector:
    """Result collector object to store results

    This object should rarely be interacted with directly. Rather, developers
        are more likely to interact with this object via sylva.handler.Handler objects.

    Methods:
        insert: Insert a new ResultDataFrame into the collector
        get_data: Returns a Pandas DataFrame of the collected results
        deduplicate: Deduplicate the collected results
        get_unique_queries: Returns a list of unique queries
        get_unique_usernames: Returns a list of unique usernames
        get_unique_emails: Returns a list of unique emails
        get_unique_phones: Returns a list of unique phone numbers
        get_unique_fullnames: Returns a list of unique full names
        get_unique_firstname_middlename_lastname_groups: Returns a list of unique firstname, middlename, and lastname groups
    """
    def __init__(self):
        self.__data:ResultDataFrame = ResultDataFrame()


    def insert(self, new_data:ResultDataFrame):
        self.__data.insert_frame(new_data)


    def get_data(self) -> pd.DataFrame:
        return self.__data.get_data()
    

    def deduplicate(self) -> pd.DataFrame:
        return self.__data.deduplicate()
    

    def get_unique_queries(self, branchable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        return df['query'].dropna().unique().tolist()
    def get_unique_usernames(self, branchable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        return df['username'].dropna().unique().tolist()
    def get_unique_emails(self, branchable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        return df['email'].dropna().unique().tolist()
    def get_unique_phones(self, branchable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        return df['phone'].dropna().unique().tolist()
    def get_unique_fullnames(self, branchable_only:bool=False) -> List[str]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        return df['full_name'].dropna().unique().tolist()
    def get_unique_firstname_middlename_lastname_groups(self, branchable_only:bool=False) -> set[tuple[str, str, str]]:
        df = self.__data.get_data()
        if branchable_only:
            df = df[df['branch_recommended'] == True]
        filtered_df = df.dropna(subset=['first_name', 'last_name'])
        filtered_data = set(zip(filtered_df['first_name'], filtered_df['middle_name'], filtered_df['last_name']))
        return filtered_data
