import calendar
from difflib import SequenceMatcher
import json
import pathlib
import re
from typing import Dict, List

from bs4 import BeautifulSoup
import pandas as pd
import requests
import tldextract

from .. import __url_normalization_pattern__
from .generic import RequestError


class PatternMatch:
    def __init__(self):
        self.__module_name:str = 'Discovered'
        self.local_pattern_data = f'{pathlib.Path(__file__).parent.resolve()}/../data/site_patterns.json'
        self.pattern_data = None
        with open(self.local_pattern_data, 'r') as f:
            self.pattern_data = json.load(f)
        self.pattern_data = self.pattern_data['patterns']
        self._generic_desirables:List[Dict] = [
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?behance\\.net\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Behance'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?dribbble\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Dribbble'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?flickr\\.com\\/people\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Flickr'},
            {'pattern': '^(?P<url>https?:\\/\\/(?P<uid>.+?)\\.tumblr\\.com\\/?)$', 'platform_name': 'Tumblr'},
            {'pattern': r'^(?P<url>https?:\/\/(?:www\.)?youtube\.com\/channel\/(?:@(?P<uid>[^\s]+?)|.+?))(?:\/.*)?$', 'platform_name': 'YouTube', 'scrape_to_resolve': True},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?vimeo\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Vimeo'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?soundcloud\\.com\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'SoundCloud'},
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
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?pinterest\\.(?:com|fr)\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Pintrest'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?stackoverflow\\.com\\/users\\/[0-9]+?\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'StackOverflow'},
            {'pattern': '^(?P<url>https?:\\/\\/(?:www\\.)?crowdin\\.com\\/profile\\/(?P<uid>[^\\/\\s]+\\/?))$', 'platform_name': 'Crowdin'},
        ]
        self._known_redirects_by_query_string:List[str] = [
            r'https?:\/\/(?:www\.)youtube\.com\/redirect\?.+?q=(?P<url>https?%3A%2F%2F.+)' # YouTube has problems.. FIXME?
        ]
    def search(self, url:str, body:str=None, query:str=None, preexisting:pd.DataFrame=None, recursion_depth: int=0) -> pd.DataFrame:
        """Searches for patterns in the given URL and body.

        Keyword Arguments:
            url {str} -- The URL to search probe and pattern match body)
            body {str} -- The body of the URL to search for patterns in (default: {None})
            query {str} -- The query to search for (default: {None})
            preexisting {pd.DataFrame} -- Optional dataframe containing alreayd scraped items to avoid duplicate results (read only) (default: {None})
            recursion_depth {int} -- The new recursion depth (default: {0}) - Rarely used, normally to avoid infinite recursion
        Returns:
            pd.DataFrame -- A DataFrame containing the results of the search
        """
        url = re.sub(__url_normalization_pattern__, '', url)


        def _search_patterns(pattern:Dict):
            if 'sequence' in pattern:
                steps = len(pattern['sequence'])
                last_match = body
                for step in range(1, steps):
                    last_match = re.search(pattern['sequence'][f'{step}'], body)['next']
                    if last_match is None or last_match == '':
                        return
                else:
                    if last_match:
                        captures = re.search(pattern['sequence'][f'{steps}'], last_match)
            
            else:
                captures = re.search(pattern['pattern'], body)
            
            if captures:
                new_item:Dict = {}

                if pattern['validation_type'] == 'social':
                    new_item['platform_name'] = pattern['platform_name']
                if 'uid' in captures.groupdict():
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
        

        def _search_desirables(url:str) -> Dict[str, str]:
            # Normalize the URL by removing www, tailing slash, and query string
            target_url = re.sub(__url_normalization_pattern__, '', a['href'])

            if 'validation_string' in desired_target or 'validation_pattern' in desired_target:
                target_response = requests.get(target_url)
                if target_response.status_code != 200:
                    return {}
                target_body = target_response.text

            if 'validation_string' in desired_target:
                if desired_target['validation_string'] not in target_body:
                    return {}
            if 'validation_pattern' in desired_target:
                if not re.match(desired_target['validation_pattern'], target_body):
                    return {}

            found_desirable: Dict[str, str] = {
                'platform_name': desired_target['platform_name'],
                'platform_url': target_url,
                'source_name': "Discovered",
            }

            captured_groups = re.search(desired_target['pattern'], target_url)
            if 'uid' in captured_groups.groupdict() and captured_groups.group('uid') is not None:
                # Skip if username is too similar to the domain is was discovered on
                # TODO Matching can likely be improved with some secondary library
                similarity = SequenceMatcher(None, split_url.domain, captured_groups.group('uid')).ratio()
                if similarity >= 0.75:
                    return {}

                found_desirable['username'] = captured_groups.group('uid')
            
            return found_desirable


        if _already_discovered(url):
            return pd.DataFrame()
            

        split_url = tldextract.extract(url)
        root_domain = f'{split_url.domain}.{split_url.suffix}'

        if root_domain not in self.pattern_data:
            return pd.DataFrame()
        
        current_pattern_data = self.pattern_data[root_domain]

        if (not body and query) or 'custom_url' in current_pattern_data:
            if 'custom_url' in current_pattern_data:
                url = current_pattern_data['custom_url'].format(QUERY=query)
            else:
                url = url.format(query)

            headers: Dict[str, str] = {}
            if 'headers' in current_pattern_data:
                for header, value in current_pattern_data['headers'].items():
                    # Must iterate so as to not overwrite possibly pre-existing headers
                    headers[header] = value

            response = requests.get(url=url, headers=headers)
            if response.status_code != 200:
                return pd.DataFrame()
            body = response.text
        elif not body and not query:
            raise RequestError(f'Not enough information for pattern matching {current_pattern_data["friendly_name"]}')

        if not current_pattern_data['wildcard_subdomain']:
            if 'subdomains' not in current_pattern_data:
                raise json.JSONDecodeError(f'Domain {root_domain} set as not wildcard but has no subdomains', '', 0)
            if split_url.subdomain not in current_pattern_data['subdomains']:
                pass # TODO Should we default to root patterns or just skip?
            else:
                current_pattern_data = current_pattern_data['subdomains'][split_url.subdomain]

        new_data:List[Dict] = []

        if 'self' in current_pattern_data:
            self_scrape_data:Dict = {}
            for pattern in current_pattern_data['self']:
                captures = re.search(pattern, body, re.MULTILINE)
                if captures:
                    self_scrape_data['platform_name'] = current_pattern_data['friendly_name']
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
                    if 'country' in captures.groupdict():
                        self_scrape_data['country'] = captures.group('country')
                    if 'birth_day' in captures.groupdict():
                        self_scrape_data['birth_day'] = captures.group('birth_day')
                    if 'birth_month' in captures.groupdict():
                        birth_month = captures.group('birth_month')
                        if birth_month in calendar.month_name:
                            self_scrape_data['birth_month'] = str(list(calendar.month_name).index(birth_month))
                        elif birth_month in calendar.month_abbr:
                            self_scrape_data['birth_month'] = str(list(calendar.month_abbr).index(birth_month))
                        elif birth_month.isdigit():
                            if int(birth_month) in range(1, 13):
                                self_scrape_data['birth_month'] = birth_month
                    if 'birth_year' in captures.groupdict():
                        self_scrape_data['birth_year'] = captures.group('birth_year')
                    self_scrape_data['source_name'] = "Scraped"
            if self_scrape_data:
                new_data.append(self_scrape_data)

        if 'patterns' in current_pattern_data:
            for pattern in current_pattern_data['patterns']:
                _search_patterns(pattern)
        
        soup = BeautifulSoup(body, 'html.parser')

        for desired_target in self._generic_desirables:
            for a in soup.find_all('a', href=re.compile(desired_target['pattern'])):
                if (
                    'scrape_to_resolve' in desired_target
                    and desired_target['scrape_to_resolve']
                    and not recursion_depth
                ):
                    scraped_data:List[Dict] = self.search(url=a['href'], query='filler data to pass checks', recursion_depth=recursion_depth+1).to_dict(orient='records')
                    new_data.extend(scraped_data)
                else:
                    new_data.append(_search_desirables(url=a['href']))
            
        for known_redirect_pattern in self._known_redirects_by_query_string:
            for a in soup.find_all('a', href=re.compile(known_redirect_pattern)):
                matched_groups = re.search(known_redirect_pattern, a['href'])
                if 'url' in matched_groups.groupdict():
                    print(f'Found redirect {matched_groups.group("url")}\n\n')
                    new_data.append(_search_desirables(url=matched_groups.group('url')))

        return pd.DataFrame(new_data)
