import json
import pathlib
import re
from typing import Dict, List

from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
import pandas as pd
import requests
import tldextract

from .. import __url_normalization_pattern__
from ..config import config
from ..easy_logger import LogLevel, loglevel, NoColor
from .generic import RequestError


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor

class PatternMatch:
    def __init__(self):
        self.__module_name:str = 'Discovered'
        self.local_pattern_data = f'{pathlib.Path(__file__).parent.resolve()}/../data/site_patterns.json'
        self.pattern_data = None
        with open(self.local_pattern_data, 'r') as f:
            self.pattern_data = json.load(f)
        self.pattern_data = self.pattern_data['patterns']
        self._generic_desirables:List[Dict] = [
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?linkedin\\.com\\/in\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'LinkedIn'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?github\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'GitHub', 'validation_string': 'itemprop="additionalName"'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?(?:twitter|x)\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Twitter'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?instagram\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Instagram'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?facebook\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Facebook'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?xing\\.com\\/profile\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Xing'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?twitch\\.tv\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Twitch'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?snapchat\\.com\\/add\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Snapchat'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?telegram\\.me\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Telegram'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?gitlab\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'GitLab'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?pinterest\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Pintrest'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?stackoverflow\\.com\\/users\\/[0-9]+?\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'StackOverflow'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?crowdin\\.com\\/profile\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Crowdin'},
        ]
    def search(self, url:str, body:str=None, query:str=None, preexisting:pd.DataFrame=None) -> pd.DataFrame:
        """Searches for patterns in the given URL and body.

        Keyword Arguments:
            url {str} -- The URL to search probe and pattern match body)
            body {str} -- The body of the URL to search for patterns in (default: {None})
            query {str} -- The query to search for (default: {None})
            preexisting {pd.DataFrame} -- Optional dataframe containing alreayd scraped items to avoid duplicate results (read only) (default: {None})
        Returns:
            pd.DataFrame -- A DataFrame containing the results of the search
        """
        url = re.sub(__url_normalization_pattern__, '', url)


        def _search_patterns(pattern:str):
            captures = re.search(pattern['pattern'], body)
            if captures:
                new_item:Dict = {}

                if pattern['validation_type'] == 'social':
                    new_item['platform_name'] = pattern['platform_name']
                if 'uid' in captures.groupdict():
                    if captures.group('uid') == 'f':
                        print(body)
                    new_item['username'] = captures.group('uid')
                if 'url' in captures.groupdict():
                    normalized_url = re.sub(__url_normalization_pattern__, '', captures.group('url'))
                    new_item['platform_url'] = normalized_url
                new_item['source_name'] = "Discovered"
                new_data.append(new_item)


        def _already_discovered(url:str) -> bool:
            if preexisting is None:
                return False
            discovered_data = preexisting[preexisting['source_name'].isin(["Discovered", "Scraped"])]
            if url in discovered_data['platform_url'].values:
                print(f'MATHCING: Already discovered {url}')
                return True
            return False


        if _already_discovered(url):
            return pd.DataFrame()
            

        split_url = tldextract.extract(url)
        root_domain = f'{split_url.domain}.{split_url.suffix}'

        if root_domain not in self.pattern_data:
            return pd.DataFrame()

        if (not body and query) or 'custom_url' in self.pattern_data[root_domain]:
            if 'custom_url' in self.pattern_data[root_domain]:
                url = self.pattern_data[root_domain]['custom_url'].format(QUERY=query)
            else:
                url = url.format(query)
            response = requests.get(url)
            if response.status_code != 200:
                return pd.DataFrame()
            body = response.text
        elif not body and not query:
            raise RequestError(f'Not enough information for pattern matching {self.pattern_data[root_domain]["friendly_name"]}')

        if not self.pattern_data[root_domain]['wildcard_subdomain']:
            # TODO add support for subdomain differentials
            return pd.DataFrame()

        new_data:List[Dict] = []

        if 'self' in self.pattern_data[root_domain]:
            self_scrape_data:Dict = {}
            for pattern in self.pattern_data[root_domain]['self']:
                captures = re.search(pattern, body, re.MULTILINE)
                if captures:
                    self_scrape_data['platform_name'] = self.pattern_data[root_domain]['friendly_name']
                    self_scrape_data['platform_url'] = url
                    if 'uid' in captures.groupdict():
                        self_scrape_data['username'] = captures.group('uid')
                    if 'fullname' in captures.groupdict():
                        self_scrape_data['full_name'] = captures.group('fullname')
                    if 'firstname' in captures.groupdict():
                        self_scrape_data['first_name'] = captures.group('firstname')
                    if 'lastname' in captures.groupdict():
                        self_scrape_data['last_name'] = captures.group('lastname')
                    if 'rawaddress' in captures.groupdict():
                        self_scrape_data['raw_address'] = captures.group('rawaddress')
                    if 'comment' in captures.groupdict():
                        self_scrape_data['comment'] = captures.group('comment')
                    self_scrape_data['source_name'] = "Scraped"
            if self_scrape_data:
                new_data.append(self_scrape_data)

        if 'patterns' in self.pattern_data[root_domain]:
            for pattern in self.pattern_data[root_domain]['patterns']:
                _search_patterns(pattern)
        
        for desired_target in self._generic_desirables:
            soup = BeautifulSoup(body, 'html.parser')
            for a in soup.find_all('a', href=re.compile(desired_target['pattern'])):

                # Normalize the URL by removing 
                target_url = re.sub(__url_normalization_pattern__, '', a['href'])

                target_body = requests.get(target_url).text
                if 'validation_string' in desired_target:
                    if desired_target['validation_string'] not in target_body:
                        continue
                if 'validation_pattern' in desired_target:
                    if not re.match(desired_target['validation_pattern'], target_body):
                        continue
                pass


        new_df = pd.DataFrame(new_data)

        return pd.DataFrame(new_df)
