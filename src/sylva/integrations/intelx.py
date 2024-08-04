import pandas as pd

from sylva import __user_agent__, Collector
from sylva.config import config
from sylva.errors import APIKeyError
from sylva.integrations.intelxapi import IntelX_API
from sylva.types import QueryType


# TODO IntelX needs quite a bit of work

class IntelX:
    def __init__(self, collector:Collector, api_key:str):
        self.__api_url:str = 'https://3.intelx.io'
        self.__debug_disable_tag:str = 'intelx'
        self.__api_key:str = api_key
        self.__base_headers:dict[str, str] = {
            'X-Key': api_key,
            'User-Agent': __user_agent__,
        }
        self.source_obtain_keys_url:str = 'https://intelx.io/account?tab=developer'
        self.source_name:str = 'IntelX'
        self.collector:Collector = collector
    def search(self, query:str, limit:int=2, buckets=["leaks.public", "leaks.private", "pastes", "darknet"], timeout:int=5, datefrom:str=None, dateto:str=None, sort:int=2, media:int=24, terminate=[], in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        if in_recursion and not config['Target Options']['intelx-branch-in']:
            return pd.DataFrame()

        if (not config['Keys']['intelx-key']):
            raise APIKeyError(key_not_provided=True)

        intelxapi = IntelX_API(key=config['Keys']['intelx-key'], ua=__user_agent__)
        capabilities = intelxapi.GET_CAPABILITIES()
        queried_buckets:list[str] = []
        for permitted_bucket in capabilities['buckets']:
            if any(permitted_bucket in bucket for bucket in buckets):
                queried_buckets.append(permitted_bucket)
        results = intelxapi.search(term=query, maxresults=limit, buckets=buckets, timeout=timeout, datefrom=datefrom, dateto=dateto, sort=sort, media=media, terminate=terminate)
        for record in results['records']:
            print(f"Found media type {record['media']} in {record['bucket']}\n\n{record}\n\n########")
        return pd.DataFrame(results['records'])
