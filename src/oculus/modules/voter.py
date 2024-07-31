import pandas as pd
import requests
from typing import Dict

from oculus.collector import Collector
from oculus.helpers.generic import QueryType, compare_to_known, ref_list
from oculus.modules.voter_regions import USA


class Voter:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'voter'
        self.source_name:str = 'Voter Registry'
        self.collector:Collector = collector


    def accepts(self, query:str, query_type:str) -> bool|QueryType:
        return True


    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_url:str|None=None) -> pd.DataFrame:
        if query_type != QueryType.FULLNAME:
            return pd.DataFrame()
        
        if proxy_url is None:
            return pd.DataFrame()

        test_headers:dict = {'Accept': 'application/json',}
        flaresolverr_response_test = requests.get(url=f'{proxy_url}', headers=test_headers)
        if flaresolverr_response_test.status_code != 200:
            return pd.DataFrame()
        if flaresolverr_response_test.json()['msg'] != 'FlareSolverr is ready!':
            return pd.DataFrame()

        if compare_to_known(query=query, id=ref_list['ref_a']):
            return pd.DataFrame()

        new_data:Dict[str, str|bool] = USA.search(full_name=query, flaresolverr_proxy_url=proxy_url)
        new_df:pd.DataFrame = None

        if new_data is None or new_data == {}:
            return pd.DataFrame()

        new_data['query'] = query
        new_data['source_name'] = self.source_name

        new_df = pd.DataFrame([new_data])
        self.collector.insert(new_df)

        return new_df
        
