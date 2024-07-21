from typing import List
import pandas as pd

from .helpers.helpers import ResultDataFrame

class Collector:
    def __init__(self):
        self.__data:ResultDataFrame = ResultDataFrame()


    def insert(self, new_data:ResultDataFrame):
        self.__data.insert_frame(new_data)


    def get_data(self) -> pd.DataFrame:
        return self.__data.get_data()
    

    def deduplicate(self) -> pd.DataFrame:
        return self.__data.deduplicate()
    

    def get_unique_usernames(self) -> List[str]:
        return self.__data.get_data()['username'].unique().tolist()
