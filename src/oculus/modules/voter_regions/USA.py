from datetime import datetime
import re
from typing import Dict, List
import urllib.parse

import pandas as pd
import requests


__us_state_to_abbrev:Dict[str, str] = {
    "alaska": "ak",
    "arkansas": "ar",
    "colorado": "co",
    "connecticut": "ct",
    "florida": "fl",
    "idaho": "id",
    "louisiana": "la",
    "michigan": "mi",
    "mississippi": "ms",
    "nevada": "nv",
    "new jersey": "nj",
    "north carolina": "nc",
    "ohio": "oh",
    "oklahoma": "ok",
    "rhode island": "ri",
    "utah": "ut",
    "washington": "wa",
    "district of columbia": "dc",
}
__supported_states:List[str] = list(__us_state_to_abbrev.values())

__base_proxy_headers:Dict[str, str] = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}



__voter_data_url:str = 'https://voterrecords.com'

def search(
        proxy_data:dict[str, str],
        first_name:str|None=None,
        middle_name:str|None=None,
        last_name:str|None=None,
        full_name:str|None=None,
        state:str|None=None,
        city:str|None=None,
        age:int|None=None,
) -> Dict[str, str|bool]:
    """Search for voter information in the United States
    
    Keyword Arguments:
        first_name {str} -- The first name of the voter (default: {None})
        middle_name {str} -- The middle name of the voter (default: {None})
        last_name {str} -- The last name of the voter (default: {None})
        full_name {str} -- The full name of the voter (default: {None})
        state {str} -- The state of the voter (default: {None})
        city {str} -- The city of the voter (default: {None})
        age {int} -- The age of the voter (default: {None})

    Note that at least one name related argument MUST be provided.
    State should be full proper name or two letter abbreviation.
    
    Returns:
        pd.DataFrame -- A DataFrame containing the results of the search
    """
    if (
        first_name is None
        and middle_name is None
        and last_name is None
        and full_name is None
    ):
        return {}
    
    if (
        (
            first_name is not None
            or middle_name is not None
            or last_name is not None
        )
        and full_name is not None
    ):
        raise ValueError('Cannot provide either first_name, middle_name, or last_name with full_name')
    
    query_name:str = ''
    if full_name is not None:
        query_name = urllib.parse.quote_plus(full_name)
    else:
        if first_name is not None:
            query_name += urllib.parse.quote(first_name)
        if middle_name is not None:
            if query_name != '':
                query_name += '+'
            query_name += urllib.parse.quote(middle_name)
        if last_name is not None:
            if query_name != '':
                query_name += '+'
            query_name += urllib.parse.quote(last_name)
    
    if state is not None:
        state = state.lower()
        if state in __us_state_to_abbrev:
            state = __us_state_to_abbrev[state]
        elif state not in __supported_states:
            raise ValueError(f'State {state} is not supported')
    else:
        state = 'us'

    location:str = state
    if city is not None:
        city = city.lower()
        location = f'{city}-{state}'

    birth_year_range:str|None = None
    if age is not None:
        current_year:int = datetime.now().year
        birth_year:int = current_year - age
        # TODO Check in which direction years are inclusive if not both
        if birth_year > 2000:
            birth_year_range = 'after+2000'
        elif birth_year > 1990:
            birth_year_range = '1991to2000'
        elif birth_year > 1980:
            birth_year_range = '1981to1990'
        elif birth_year > 1970:
            birth_year_range = '1971to1980'
        elif birth_year > 1960:
            birth_year_range = '1961to1970'
        elif birth_year > 1950:
            birth_year_range = '1951to1960'
        elif birth_year > 1940:
            birth_year_range = '1941to1950'
        elif birth_year > 1930:
            birth_year_range = '1931to1940'
        elif birth_year <= 1930:
            birth_year_range = 'before+1930'

    query_url:str = f'{__voter_data_url}/voters'
    
    if location:
        query_url += f'/{location}'
    if query_name:
        query_url += f'/{query_name.lower()}'
    if birth_year_range:
        if query_name:
            query_url += '-'
        query_url += f'/{birth_year_range}'
    query_url += '/1'

    request_data:dict = {
        'cmd': 'request.get',
        'url': query_url,
        'session': proxy_data['flaresolverr_session_id'],
        'maxTimeout': 30000,
    }

    response = requests.post(url=proxy_data["proxy_url"], json=request_data, headers=__base_proxy_headers)

    if response.status_code != 200:
        # FlareSolverr proxy failed directly
        return {}
    
    if response.json()['solution']['status'] != 200:
        # FlareSolverr proxy failed to get a valid response from target
        return {}
    
    # Matching expected indicator or new rows (shown below). More than one is low confidence.
    # <tr data-href="/voter/<id number>/<name>" itemscope itemtype="http://schema.org/Person">
    if response.text.count('tr data-href') != 1:
        return {}
    
    urlpart_pattern = r'tr data-href="(?P<URL_PART>\/voter\/\d+\/[a-z\-]+)\" itemscope'
    fullname_pattern = r'span itemprop="name">(?P<FULLNAME>.+?) ?<\/span>'
    rawaddr_pattern = r'span itemprop="address">(?P<ADDRESS>.+?)<\/span>'
    age_pattern = r'<strong>Age:&nbsp;<\/strong>(?P<AGE>\d{1,3})<br\/>'

    try:
        # TODO First name, middle initial, and last name can be guessed based on values on the profile's page (compare with/without middle initial)
        urlpart: str = re.search(urlpart_pattern, response.json()['solution']['response']).group('URL_PART')
        profile_url: str = f'{__voter_data_url}{urlpart}'
        fullname: str = re.search(fullname_pattern, response.json()['solution']['response']).group('FULLNAME')
        rawaddr: str = re.search(rawaddr_pattern, response.json()['solution']['response']).group('ADDRESS')
        age: int = int(re.search(age_pattern, response.json()['solution']['response']).group('AGE'))
    except KeyError as e:
        # Important expected data not found. Possibly a false positive.
        # TODO Make this better for handling redacted/excluded data
        return {}
    
    new_data:Dict = {
            'spider_recommended': True,
            'platform_name': "VoterRecords.com",
            'platform_url': profile_url,
            'full_name': fullname,
            'raw_address': rawaddr,
            'age': age,
        }

    return new_data
    