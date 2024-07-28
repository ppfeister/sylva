import pandas as pd
import requests

from oculus.collector import Collector
from oculus.helpers.generic import QueryType
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

        USA.search(full_name=query, flaresolverr_proxy_url=proxy_url)

        return pd.DataFrame()
        
