
import re
from typing import Dict, List

import pandas as pd
from sherlock_project.sherlock import sherlock
from sherlock_project.sites import SitesInformation
from sherlock_project.notify import QueryNotify
from sherlock_project.result import QueryStatus

from .. import __url_normalization_pattern__
from ..helpers.generic import QueryType, RequestError
from ..helpers import pattern_match
from ..collector import Collector

class Sherlock:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'sherlock'
        self.source_name:str = 'Sherlock'
        self.collector:Collector = collector
        self.pattern_match = pattern_match.PatternMatch()

    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        if (
            query_type == QueryType.TEXT
            or query_type == QueryType.USERNAME
        ):
            return True
        return False
    
    def search(self, query:str, timeout:int=3, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        try:
            sites = SitesInformation()
        except FileNotFoundError as e:
            raise RequestError(f'Failed to get results from Sherlock: {e}')
        sites_data = { site.name: site.information for site in sites }
        results:List[Dict] = sherlock(
            username=query,
            site_data=sites_data,
            query_notify=QueryNotify(),
            timeout=timeout,
        )

        exists:List[Dict] = []
        matched_patterns = pd.DataFrame()
        for site in sites:
            if results[site.name]['status'].status == QueryStatus.CLAIMED:
                new_item:Dict = {
                    'query': query,
                    'source_name': self.source_name,
                    'spider_recommended': True,
                    'platform_name': site.name,
                    'platform_url': re.sub(__url_normalization_pattern__, '', results[site.name]['url_user']),
                    'username': query,
                }

                send_body:bool = True
                if (
                    'urlProbe' in sites_data[site.name]
                    or sites_data[site.name]['errorType'] != 'message'
                    or (
                        'request_method' in sites_data[site.name]
                        and sites_data[site.name]['request_method'] != 'GET'
                    )
                ):
                    send_body = False

                try:
                    body_placeholder = results[site.name]['response_text'].decode('utf-8')
                except UnicodeDecodeError:
                    body_placeholder = None
                    send_body = False

                if send_body:
                    matched_patterns = pd.concat([matched_patterns, self.pattern_match.search(url=sites_data[site.name]['url'], body=body_placeholder, query=query, preexisting=self.collector.get_data())], ignore_index=True)
                else:
                    matched_patterns = pd.concat([matched_patterns, self.pattern_match.search(url=sites_data[site.name]['url'], query=query, preexisting=self.collector.get_data())], ignore_index=True)

                if not matched_patterns.empty:
                    matched_patterns['query'] = query
                    matched_patterns['spider_recommended'] = True

                if (
                    matched_patterns.empty
                    or new_item['platform_url'] not in matched_patterns['platform_url'].values
                ):
                    exists.append(new_item)

        new_data = pd.DataFrame(exists)

        if not matched_patterns.empty:
            new_data = pd.concat([new_data, matched_patterns], ignore_index=True)

        self.collector.insert(new_data)
        return new_data
