import pandas as pd
from typing import Dict

from .. import Collector
from ..types import QueryType, SearchArgs
from ..helpers.generic import compare_to_known, ref_list
from ..modules.voter_regions import USA
from ..helpers.proxy import test_if_flaresolverr_online


class Voter:
    def __init__(self, collector:Collector):
        """Initialize the Voter module

        Keyword Arguments:
            collector {Collector} -- The collector callback to use for results
        """
        self.__debug_disable_tag:str = 'voter'
        self.source_name:str = 'Voter Registry'
        self.collector:Collector = collector


    def accepts(self, search_args:SearchArgs) -> bool:
        """Determine if the search is supported by the module

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            bool -- True if the search is supported, False otherwise
        """
        # TODO Address proper acceptability checks
        if search_args.query_type != QueryType.FULLNAME:
            if ' ' not in search_args.query:
                return False

        return True


    def search(self, search_args:SearchArgs) -> pd.DataFrame:
        """Initiate a search of known voter rolls

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            pd.DataFrame -- The results of the search
        """
        if search_args.query_type != QueryType.FULLNAME:
            return pd.DataFrame()

        if search_args.proxy_data is None or 'proxy_url' not in search_args.proxy_data or search_args.proxy_data['proxy_url'] is None:
            return pd.DataFrame()

        if not test_if_flaresolverr_online(proxy_url=search_args.proxy_data['proxy_url']):
            return pd.DataFrame()

        if compare_to_known(query=search_args.query, id=ref_list['ref_a']):
            return pd.DataFrame()

        new_data:Dict[str, str|bool] = USA.search(full_name=search_args.query, proxy_data=search_args.proxy_data)
        new_df:pd.DataFrame = None

        if new_data is None or new_data == {}:
            return pd.DataFrame()

        new_data['query'] = search_args.query
        new_data['source_name'] = self.source_name

        new_df = pd.DataFrame([new_data])
        self.collector.insert(new_df)

        return new_df

