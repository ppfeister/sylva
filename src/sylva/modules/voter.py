import pandas as pd
import requests
from typing import Dict

from sylva.collector import Collector
from sylva.helpers.generic import QueryType, compare_to_known, ref_list
from sylva.modules.voter_regions import USA
from sylva.helpers.proxy import test_if_flaresolverr_online


class Voter:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'voter'
        self.source_name:str = 'Voter Registry'
        self.collector:Collector = collector


    def accepts(self, query:str, query_type:str) -> bool|QueryType:
        return True


    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        if query_type != QueryType.FULLNAME:
            return pd.DataFrame()
        
        if proxy_data is None or 'proxy_url' not in proxy_data or proxy_data['proxy_url'] is None:
            return pd.DataFrame()

        if not test_if_flaresolverr_online(proxy_url=proxy_data['proxy_url']):
            return pd.DataFrame()

        if compare_to_known(query=query, id=ref_list['ref_a']):
            return pd.DataFrame()

        new_data:Dict[str, str|bool] = USA.search(full_name=query, proxy_data=proxy_data)
        new_df:pd.DataFrame = None

        if new_data is None or new_data == {}:
            return pd.DataFrame()

        new_data['query'] = query
        new_data['source_name'] = self.source_name

        new_df = pd.DataFrame([new_data])
        self.collector.insert(new_df)

        return new_df
        
