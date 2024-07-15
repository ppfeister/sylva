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

    if not body and query:
        response = requests.get(url.format(query))
        if response.status_code != 200:
            return pd.DataFrame()
        body = response.text
    elif not body and not query:
        raise RequestError(f'Sherlock did not return enough information for pattern matching {pattern_data[root_domain]["friendly_name"]}')

    if not pattern_data[root_domain]['wildcard_subdomain']:
        # TODO add support for subdomain differentials
        return pd.DataFrame()

    patterns = pattern_data[root_domain]['patterns']

    new_data:List[Dict] = []
    for pattern in patterns:
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
    return pd.DataFrame(new_data)
