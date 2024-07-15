
from typing import Dict, List
import json

import pandas as pd
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus

from ..helpers.helpers import RequestError
from ..collector import Collector

class Sherlock:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'sherlock'
        self.source_name:str = 'Sherlock'
        self.collector:Collector = collector

    def accepts(self, query:str) -> bool:
        return True
    
    def search(self, query:str) -> pd.DataFrame:
        try:
            sites = SitesInformation()
        except FileNotFoundError as e:
            raise RequestError(f'Failed to get results from Sherlock: {e}')
        sites_data = { site.name: site.information for site in sites }
        results:List[Dict] = sherlock(username=query, site_data=sites_data, query_notify=QueryNotify())

        exists:List[Dict] = []
        for site in sites:
            if results[site.name]['status'].status == QueryStatus.CLAIMED:
                exists.append({
                    'query': query,
                    'source_name': self.source_name,
                    'spider_recommended': True,
                    'platform_name': site.name,
                    'platform_url': results[site.name]['url_user'],
                    'username': query,
                })

        new_data = pd.DataFrame(exists)
        self.collector.insert(new_data)
        return new_data
