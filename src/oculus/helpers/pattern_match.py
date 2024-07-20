import json
import pathlib
import re
from typing import Dict, List

from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
import pandas as pd
import requests
import tldextract

from ..config import config
from ..easy_logger import LogLevel, loglevel, NoColor
from ..helpers.helpers import RequestError


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor

class PatternMatch:
    def __init__(self):
        self.local_pattern_data = f'{pathlib.Path(__file__).parent.resolve()}/../data/site_patterns.json'
        self.pattern_data = None
        with open(self.local_pattern_data, 'r') as f:
            self.pattern_data = json.load(f)
        self.pattern_data = self.pattern_data['patterns']
        self._generic_desirables:List[Dict] = [
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?linkedin\\.com\\/in\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'LinkedIn'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?github\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'GitHub'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?(?:twitter|x)\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Twitter'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?instagram\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Instagram'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?facebook\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Facebook'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?xing\\.com\\/profile\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Xing'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?twitch\\.tv\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Twitch'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?snapchat\\.com\\/add\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Snapchat'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?telegram\\.me\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Telegram'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?gitlab\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'GitLab'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?pinterest\\.com\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'Pintrest'},
            {'pattern': '(?P<url>https?:\\/\\/(?:www\\.)?stackoverflow\\.com\\/users\\/[0-9]+?\\/(?P<uid>.+?))[\\\"|\\\'|&quot;]', 'validation_type': 'social', 'platform_name': 'StackOverflow'},
        ]
    def search(self, url:str, body:str=None, query:str=None) -> pd.DataFrame:
        def _search_patterns(pattern:str):
            captures = re.search(pattern['pattern'], body)
            if captures:
                new_item:Dict = {}

                if pattern['validation_type'] == 'social':
                    new_item['platform_name'] = pattern['platform_name']
                    platform_names_searched.append(pattern['platform_name'])
                if 'uid' in captures.groupdict():
                    if captures.group('uid') == 'f':
                        print(body)
                    new_item['username'] = captures.group('uid')
                if 'url' in captures.groupdict():
                    new_item['platform_url'] = captures.group('url')
                new_data.append(new_item)
            

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
            if self_scrape_data:
                new_data.append(self_scrape_data)

        platform_names_searched:List[str] = []
        if 'patterns' in self.pattern_data[root_domain]:
            for pattern in self.pattern_data[root_domain]['patterns']:
                _search_patterns(pattern)
        
        for desired_target in self._generic_desirables:
            if desired_target in platform_names_searched:
                continue
            soup = BeautifulSoup(body, 'html.parser')
            for a in soup.find_all('a', href=re.compile(desired_target['pattern'])):
                print(a['href'])
                pass


        new_df = pd.DataFrame(new_data)
        if new_data:
            new_df['source_name'] = "Discovered"

        return pd.DataFrame(new_df)
