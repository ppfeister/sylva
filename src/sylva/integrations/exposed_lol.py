import pandas as pd
import requests

from sylva.collector import Collector
from sylva.helpers.generic import QueryType
from sylva.helpers.proxy import test_if_flaresolverr_online


class Voter:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'exposed'
        self.source_name:str = 'Exposed'
        self.collector:Collector = collector


    def accepts(self, query:str, query_type:str) -> bool|QueryType:
        return True


    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_url:str|None=None) -> pd.DataFrame:
        if query_type != QueryType.FULLNAME:
            return pd.DataFrame()
        
        if proxy_url is None:
            return pd.DataFrame()

        if not test_if_flaresolverr_online(proxy_url):
            return pd.DataFrame()
        
        query_url:str = 'https://exposed.lol/'
        flare_payload:dict = {
            'cmd': 'request.get',
            'url': query_url,
            'maxTimeout': 120000,
        }

        flare_response = requests.post(url=f'{proxy_url}v1', json=flare_payload)
        flare_json = flare_response.json()

        if flare_response.status_code != 200:
            return pd.DataFrame()
        
        print(flare_json)

        

        return pd.DataFrame()