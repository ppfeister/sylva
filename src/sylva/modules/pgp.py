import json
import pathlib
import re
from typing import Dict, List

import pandas as pd
import pgpy
import requests

from .. import __github_raw_data_url__, __short_name__
from ..config import config
from ..helpers.generic import IncompatibleQueryType, QueryType
from ..collector import Collector


# FIXME GitLab PGP API seems to be broken. Documentation indicates no auth
# is required, but that may be incorrect...

prefer_local_manifest = True

class TargetInformation:
    def __init__(self):
        self._local_manifest_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/pgp.json'
        self._local_schema_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/pgp.schema.json'
        self._remote_manifest_uri = __github_raw_data_url__

        r = requests.get(self._remote_manifest_uri)
        if r.status_code != 200 or prefer_local_manifest:
            with open(self._local_manifest_uri, 'r') as f:
                manifest_data:Dict = json.load(f)
        else:
            # TODO add validation against discovered schema version number
            manifest_data:Dict = json.loads(r.text)

        self.targets:Dict = manifest_data['targets']

        for target in self.targets:
            target['validation_pattern'] = target.get('validation_pattern', None)
            target['validation_type'] = target.get('validation_type', None)


class PGPModule:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'pgp'
        self.source_name:str = 'Sylva PGP'
        self.collector:Collector = collector
        self.targets:TargetInformation = TargetInformation()
        self.__simple_email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.__fingerprint_regex = r'^(?:[A-Fa-f0-9]{40}(?:[A-Fa-f0-9]{24})?)$'
        self.__keyid_regex = r'^(?:[A-Fa-f0-9]{16})$'
    # TODO add validation for username, email, password
    def _extract_data_from_pgp_block(self, block:str) -> List[Dict]:
        raw_rows:List[Dict] = []
        key, _ = pgpy.PGPKey.from_blob(block)
        for uid in key._uids:
            email = uid.email or pd.NA
            comment = uid.comment or pd.NA
            raw_rows.append({
                'email': email,
                'comment': comment,
            })
        return raw_rows
    
    def accepts(self, query:str, query_type:QueryType=QueryType.TEXT) -> bool:
        if query_type != QueryType.TEXT:
            return False
        return True
        # TODO Adapt to properly support fingerprint queries against keyservers
        if (
            not re.match(self.__simple_email_regex, query)
            and not re.match(self.__fingerprint_regex, query)
            and not re.match(self.__keyid_regex, query)
        ):
            return False

    def search(self, query:str, in_recursion:bool=False, query_type:QueryType=QueryType.TEXT, proxy_data:dict[str, str]|None=None) -> pd.DataFrame:
        if not self.accepts(query):
            raise IncompatibleQueryType(f'Query type not supported by {self.source_name}')

        new_data:pd.DataFrame = pd.DataFrame()
        for target in self.targets.targets:
            sanitized_query: str = None
            if target['validation_pattern']:
                if not re.match(target['validation_pattern'], query):
                    continue
            elif target['validation_type'] == 'encoded-email':
                if not re.match(self.__simple_email_regex, query):
                    continue
                else:
                    sanitized_query = requests.utils.requote_uri(query)
            elif target['validation_type'] == 'fingerprint':
                sanitized_query = query.replace(' ', '')
                if sanitized_query.startswith('0x'):
                    sanitized_query = sanitized_query[2:]
                if not re.match(self.__fingerprint_regex, sanitized_query):
                    continue
            elif target['validation_type'] == 'keyid':
                sanitized_query = query.replace(' ', '')
                if sanitized_query.startswith('0x'):
                    sanitized_query = sanitized_query[2:]
                if not re.match(self.__keyid_regex, sanitized_query):
                    continue
            if 'config_opts' in target:
                for header, value in target['headers'].items():
                    for config_substitution in target['config_opts'].items():
                        section, key = config_substitution
                        target['headers'][header] = value.format(config[section][key])
            if not sanitized_query:
                sanitized_query = query
            if 'headers' in target:
                response = requests.get(target['simple_url'].format(query=sanitized_query), headers=target['headers'])
            else:
                response = requests.get(target['simple_url'].format(query=sanitized_query))
            if response.status_code != 200:
                continue
            raw_rows:List[Dict] = []
            if target['simple_url'].startswith('https://api.github.com'):
                data = json.loads(response.text)
                if data:
                    for email in data[0]['emails']:
                        raw_rows.append({'email': email['email']})
            else:
                raw_rows = self._extract_data_from_pgp_block(response.text)
            new_rows:List[Dict] = []
            for row in raw_rows:
                new_rows.append({'email': row['email']} )
                row['platform_name'] = target['friendly_name']
                row['query'] = query
                row['source_name'] = f"{__short_name__} PGP"
                row['spider_recommended'] = True

            new_rows = pd.DataFrame(new_rows)
            new_rows['query'] = query
            new_rows['platform_name'] = target['friendly_name']
            new_rows['platform_url'] = target['profile_url'].format(query=query)
            new_rows['source_name'] = f"{__short_name__} PGP"
            new_rows['spider_recommended'] = True
            new_data = pd.concat([new_data, new_rows], ignore_index=True)

        self.collector.insert(new_data)
        return new_data
