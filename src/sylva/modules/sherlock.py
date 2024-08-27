
import re
from typing import Dict, List

import pandas as pd
from sherlock_project.sherlock import (
    QueryNotify,
    QueryStatus,
    SitesInformation,
    sherlock,
)

from .. import __url_normalization_pattern__
from ..collector import Collector
from ..errors import RequestError
from ..helpers import pattern_match
from ..types import QueryType, SearchArgs


class Sherlock:
    def __init__(self, collector:Collector):
        """Initialize the Sherlock module

        Keyword Arguments:
            collector {Collector} -- The collector callback to use for results
        """
        self.__debug_disable_tag:str = 'sherlock'
        self.source_name:str = 'Sherlock'
        self.collector:Collector = collector
        self.pattern_match = pattern_match.PatternMatch()

    def accepts(self, search_args:SearchArgs) -> bool:
        """Determine if the search is supported by the module

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search

        Returns:
            bool -- True if the search is supported, False otherwise
        """
        if (
            search_args.query_type == QueryType.TEXT
            or search_args.query_type == QueryType.USERNAME
        ):
            return True
        return False

    def search(self, search_args:SearchArgs, timeout:int=3) -> pd.DataFrame:
        """Initiate a search via Sherlock

        Keyword Arguments:
            search_args {SearchArgs} -- The arguments to use for the search
            timeout {int} -- The timeout to use for the search (default: {3})

        Returns:
            pd.DataFrame -- The results of the search
        """
        try:
            sites = SitesInformation()
        except FileNotFoundError as e:
            raise RequestError(f'Failed to get results from Sherlock: {e}')
        sites_data = { site.name: site.information for site in sites }
        results:List[Dict] = sherlock(
            username=search_args.query,
            site_data=sites_data,
            query_notify=QueryNotify(),
            timeout=timeout,
        )

        exists:List[Dict] = []
        matched_patterns = pd.DataFrame()
        for site in sites:
            if results[site.name]['status'].status == QueryStatus.CLAIMED:
                new_item:Dict = {
                    'query': search_args.query,
                    'source_name': self.source_name,
                    'branch_recommended': True,
                    'platform_name': site.name,
                    'platform_url': re.sub(__url_normalization_pattern__, '', results[site.name]['url_user']),
                    'username': search_args.query,
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

                pattern_match_args = pattern_match.PatternMatchQueryArgs(
                    url=sites_data[site.name]['url'],
                    body=body_placeholder if send_body else None,
                    query=search_args.query,
                    preexisting=self.collector.get_data(),
                )

                matched_patterns = pd.concat(
                    [matched_patterns, self.pattern_match.search(pattern_match_args)],
                    ignore_index=True,
                )

                if not matched_patterns.empty:
                    matched_patterns['query'] = search_args.query
                    matched_patterns['branch_recommended'] = True

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
