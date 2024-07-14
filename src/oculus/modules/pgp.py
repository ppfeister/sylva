import json
import pathlib
import re
from typing import Dict, List

import pandas as pd
import pgpy
import requests

from .. import __github_raw_data_url__
from ..config import config
from ..helpers.helpers import RequestError
from ..collector import Collector


# FIXME GitLab PGP API seems to be broken. Documentation indicates no auth
# is required, but that may be incorrect...

class TargetInformation:
    def __init__(self):
        self._local_manifest_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/pgp.json'
        self._local_schema_uri = f'{pathlib.Path(__file__).parent.resolve()}/../data/pgp.schema.json'
        self._remote_manifest_uri = __github_raw_data_url__

        r = requests.get(self._remote_manifest_uri)
        if r.status_code != 200:
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
        self.source_name:str = 'GPG'
        self.collector:Collector = collector
        self.targets:TargetInformation = TargetInformation()
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

    def search(self, query:str) -> pd.DataFrame:
        __simple_email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        __fingerprint_regex = r'^(?:[A-Fa-f0-9]{40}(?:[A-Fa-f0-9]{24})?)$'
        __keyid_regex = r'^(?:[A-Fa-f0-9]{16})$'
        if self.__debug_disable_tag in config['Debug']['disabled_modules']:
            return
        for target in self.targets.targets:
            sanitized_query: str = None
            if target['validation_pattern']:
                if not re.match(target['validation_pattern'], query):
                    continue
            elif target['validation_type'] == 'encoded-email':
                if not re.match(__simple_email_regex, query):
                    continue
                else:
                    sanitized_query = requests.utils.requote_uri(query)
            elif target['validation_type'] == 'fingerprint':
                sanitized_query = query.replace(' ', '')
                if sanitized_query.startswith('0x'):
                    sanitized_query = sanitized_query[2:]
                if not re.match(__fingerprint_regex, sanitized_query):
                    continue
            elif target['validation_type'] == 'keyid':
                sanitized_query = query.replace(' ', '')
                if sanitized_query.startswith('0x'):
                    sanitized_query = sanitized_query[2:]
                if not re.match(__keyid_regex, sanitized_query):
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
            if target['simple_url'].startswith('https://api.github.com'):
                emails:List[str] = []
                raw_rows:List[Dict] = []
                data = json.loads(response.text)
                if data:
                    for email in data[0]['emails']:
                        raw_rows.append({'email': email['email']})
            else:
                raw_rows = self._extract_data_from_pgp_block(response.text)
            for row in raw_rows:
                row['query'] = query
                row['source_name'] = target['friendly_name']
                row['spider_recommended'] = True
            self.collector.insert(pd.DataFrame(raw_rows))
