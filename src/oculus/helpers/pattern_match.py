import json
import pathlib
import re
from typing import Dict, List

from colorama import Fore, Back, Style
import pandas as pd
import requests
import tldextract

from ..config import config
from ..easy_logger import LogLevel, loglevel, NoColor
from ..helpers.helpers import RequestError


if config['General']['colorful'] == 'False': # no better way since distutils deprecation?
    Fore = Back = Style = NoColor


def search(url:str, body:str=None, query:str=None) -> pd.DataFrame:
    local_pattern_data = f'{pathlib.Path(__file__).parent.resolve()}/../data/site_patterns.json'
    pattern_data = None
    with open(local_pattern_data, 'r') as f:
        pattern_data = json.load(f)
    pattern_data = pattern_data['patterns']
    split_url = tldextract.extract(url)
    root_domain = f'{split_url.domain}.{split_url.suffix}'

    if root_domain not in pattern_data:
        return pd.DataFrame()

    if (not body and query) or 'custom_url' in pattern_data[root_domain]:
        if 'custom_url' in pattern_data[root_domain]:
            url = pattern_data[root_domain]['custom_url'].format(QUERY=query)
        else:
            url = url.format(query)
        response = requests.get(url)
        if response.status_code != 200:
            return pd.DataFrame()
        body = response.text
    elif not body and not query:
        raise RequestError(f'Not enough information for pattern matching {pattern_data[root_domain]["friendly_name"]}')

    if not pattern_data[root_domain]['wildcard_subdomain']:
        # TODO add support for subdomain differentials
        return pd.DataFrame()

    new_data:List[Dict] = []

    if 'self' in pattern_data[root_domain]:
        self_scrape_data:Dict = {}
        for pattern in pattern_data[root_domain]['self']:
            captures = re.search(pattern, body, re.MULTILINE)
            if captures:
                self_scrape_data['platform_name'] = pattern_data[root_domain]['friendly_name']
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

    if 'patterns' in pattern_data[root_domain]:
        for pattern in pattern_data[root_domain]['patterns']:
            captures = re.search(pattern['pattern'], body)
            if captures:
                new_item:Dict = {}

                if pattern['validation_type'] == 'social':
                    new_item['platform_name'] = pattern['platform_name']
                if 'uid' in captures.groupdict():
                    new_item['username'] = captures.group('uid')
                if 'url' in captures.groupdict():
                    new_item['platform_url'] = captures.group('url')
                new_data.append(new_item)

    new_df = pd.DataFrame(new_data)
    if new_data:
        new_df['source_name'] = "Discovered"

    return pd.DataFrame(new_df)
