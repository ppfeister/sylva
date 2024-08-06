import hashlib
import os
from typing import Dict
from urllib.parse import urlunparse, urlparse

import requests
from tldextract import extract as tldx

from sylva import __github_maintainer_url__


ref_list: Dict[str, str] = {
    'ref_a': '14fc468bc4ac40a22ae70106b351d1ce',
}

def compare_to_known(query: str, id: str) -> bool:
    if os.environ.get('SYLVA_COMPARATOR', 'True') == 'False':
        return False
    if hashlib.sha256(query.replace(' ', '').lower().encode('utf-8')).hexdigest() in requests.get(url=f"{urlunparse(urlparse(__github_maintainer_url__)._replace(netloc=f'gist.{tldx(__github_maintainer_url__).domain}.{tldx(__github_maintainer_url__).suffix}'))}/{id}/raw").text:
        return True
    return False
