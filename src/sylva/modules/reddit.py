from dataclasses import dataclass, field
import os
import re
import shutil
import tempfile
import time

import pandas as pd
import requests
import spacy
import spacy.lang.en
import spacy.tokens

from .. import __user_agent__
from .. import Collector
from ..errors import RequestError
from ..helpers.generic import compare_to_known, ref_list
from ..types import SearchArgs, QueryType


RM_SUBREDDIT_CSV_URL = 'https://raw.githubusercontent.com/jibalio/redditmetis/master/backend/libraries/metis_core/subreddits.csv'
LOCATION_HINTS: list[str] = [
    'i live',
    'i grew up',
    'i was born',
    'hailing from',
    'i reside',
    'my hometown is',
    'i am from',
    'my city is',
    'i moved to',
    'i am moving to',
    'i\'m moving to'
    'currently in',
    'based in',
    'i am living in',
    'i\'m living in',
    'i was living in',
    ]


@dataclass
class UserComment:
    """Dataclass to store information about a Reddit comment

    Attributes:
        url (str): The URL of the comment
        body (str): The body of the comment
        normalized_body (str): The body of the comment, normalized
        subreddit (str): The subreddit the comment was made in
    """
    url: str
    body: str
    normalized_body: str
    subreddit: str


class Reddit:
    def __init__(self, collector:Collector):
        self.__debug_disable_tag:str = 'reddit'
        self.source_name:str = 'Reddit'
        self.collector:Collector = collector
        self.__base_headers:dict[str, str] = {
            'Accept': 'application/json',
            'User-Agent': __user_agent__,
        }

        RM_SUBREDDIT_CSV_COLUMNS = [
            'name',            # Subreddit name
            'topic_level1',    # Level 1 topic. For instance, Entertainment.
            'topic_level2',    # Level 2 topic. For instance, TV Shows.
            'topic_level3',    # Level 2 topic. For instance, Sherlock.
            'default',         # Y if default sub, blank otherwise.
            'ignore_text',     # Y if text in sub needs to be ignored, blank otherwise.
            'sub_attribute',   # An attribute we can derive from this subreddit. i.e. sex, religion, gadget, etc.
            'sub_value',       # Value for the above attribute. i.e. male, atheism, iPhone, etc.
        ]

        self.RM_SUBREDDIT_DATA: pd.DataFrame = pd.read_csv(RM_SUBREDDIT_CSV_URL, names=RM_SUBREDDIT_CSV_COLUMNS)

        current_file_path = os.path.dirname(__file__)
        spacy_model_path_en = os.path.join(current_file_path, '../nlp/en_core_web_sm')

        self._nlp_en: spacy.lang.en.English = spacy.load(spacy_model_path_en)


    @dataclass
    class __hints:
        """Dataclass to simplify data transfer between methods within the parent class

        Attributes:
            locations (list[str], optional): List of locations mentioned in the comments. Defaults to None.
        """
        locations: list[dict[str, str]] = field(default_factory=list)


    def accepts(self, search_args:SearchArgs) -> bool:
        if search_args.query_type not in [
            QueryType.TEXT,
            QueryType.USERNAME,
        ]:
            return False

        if ' ' in search_args.query:
            return False

        return True


    def fetch_messages_by_username(self, username:str, type:str='comments') -> list[UserComment]:
        """Fetch comments made by a given username in order of novelty

        It's assumed that the Reddit API will make available only the most recent 1000 comments.

        Example:
            ```python
            comments = fetch_comments_by_username('user123')
            for comment in comments:
                print(comment.body)
            ```

        Keyword Arguments:
            username {str} -- The username to fetch comments for
            type {str} -- The type of message to fetch (default: {'comments'})
                Options:
                    - comments
                    - submitted

        Returns:
            list[UserComment] -- A list of UserComment objects
        """
        if type not in ['comments', 'submitted']:
            raise ValueError(f'Invalid type {type}')

        body_key = 'body'
        if type == 'submitted':
            body_key = 'selftext'

        communities_to_ignore: list[str] = self.RM_SUBREDDIT_DATA.loc[self.RM_SUBREDDIT_DATA['ignore_text'] == 'Y', 'name'].tolist()

        request_url_base: str = f'https://reddit.com/user/{username}/{type}.json?t=all&limit=100&sort=new'
        request_url: str = request_url_base
        comments: list[UserComment] = []

        while True:
            response = requests.get(url=request_url, headers=self.__base_headers, timeout=5)

            if response.status_code == 404:
                return []

            if response.status_code == 429:
                print("REDDIT RATE LIMITED --- PLEASE REPORT THIS TO THE DEVELOPER\n")
                raise RequestError(rate_limit_exceeded=True)

            if response.status_code != 200:
                print("REDDIT ENCOUNTERED AN ERROR --- PLEASE REPORT THIS TO THE DEVELOPER (STATUS CODE: {})\n".format(response.status_code))
                raise RequestError(message=f'Something unexpected happened with Reddit, leading to response code {response.status_code}')

            response_json = response.json()

            for child in response_json['data']['children']:
                if child['data']['subreddit'] in communities_to_ignore:
                    continue

                new_comment: UserComment = UserComment(
                    url=f'https://old.reddit.com{child['data']['permalink']}',
                    body=child['data'][body_key],
                    normalized_body=self.__normalize_text(text=child['data'][body_key]),
                    subreddit=child['data']['subreddit'],
                )

                comments.append(new_comment)

            if 'after' in response_json['data'] and response_json['data']['after'] is not None:
                request_url = f'{request_url_base}&after={response_json["data"]["after"]}'
            else:
                return comments

            time.sleep(0.3) # Helps prevent hyperactive rate limiting


    def __normalize_text(self, text:str) -> str:
        MAX_WORD_LENGTH = 255

        # Remove leading and trailing whitespace on each line
        # Remove lines that begin with > indicating quote blocks
        # Remove newlines (collapse to single line)
        # This may also remove some lines that begin with spoilers. Could be fixed up.
        text = " ".join([
            line for line in text.strip().split("\n") if (
                not line.strip().startswith("&gt;")
            )
        ])

        substitutions = [
            (r"\[(.*?)\]\((.*?)\)", r""),     # Remove links from Markdown
            (r"[\"](.*?)[\"]", r""),          # Remove text within quotes
            (r" \'(.*?)\ '", r""),            # Remove text within quotes
            (r"\.+", r". "),                  # Remove ellipses
            (r"\(.*?\)", r""),                # Remove text within round brackets
            (r"&amp;", r"&"),                 # Decode HTML entities
            (r"http.?:\S+\b", r" ")           # Remove URLs
        ]
        for pattern, replacement in substitutions:
            _text = re.sub(pattern, replacement, text, flags=re.I)

        # Remove words longer than the MAX_WORD_LENGTH
        text = " ".join(
            [word for word in _text.split(" ") if len(word) <= MAX_WORD_LENGTH]
        )

        return text


    def search_for_interesting_hints(self, search_args:SearchArgs) -> __hints:
        # Retrieve comments and submissions
        comments: list[UserComment] = self.fetch_messages_by_username(username=search_args.query, type='comments')
        submissions: list[UserComment] = self.fetch_messages_by_username(username=search_args.query, type='submitted')

        hints: self.__hints = self.__hints()

        for comment in comments + submissions:
            doc: spacy.tokens.doc.Doc = self._nlp_en(comment.normalized_body)

            if any(hint in comment.normalized_body.lower() for hint in LOCATION_HINTS):
                for ent in doc.ents:
                    if ent.label_ == 'GPE': # GPE = Geopolitical Entity
                        hints.locations.append({
                            'location': ent.text,
                            'content_url': comment.url,
                            'comment': comment.body,
                        })

        return hints


    def __check_if_exists(self, username:str) -> bool:
        request_url: str = f'https://reddit.com/user/{username}/comments.json?sort=new&limit=1'
        response = requests.get(url=request_url, headers=self.__base_headers, timeout=5)
        if response.status_code == 404:
            return False
        return True


    def search(self, search_args:SearchArgs) -> pd.DataFrame:
        if not self.__check_if_exists(username=search_args.query):
            return pd.DataFrame()

        new_data: list[dict[str, str]] = []

        if compare_to_known(query=search_args.query, id=ref_list['ref_a']):
            return pd.DataFrame()

        hints: self.__hints = self.search_for_interesting_hints(search_args=search_args)

        for location in hints.locations:
            new_data.append({
                'query': search_args.query,
                'username': search_args.query,
                'source_name': 'Reddit NLP',
                'branch_recommended': False,
                'platform_name': 'Reddit',
                'platform_url': location['content_url'],
                'raw_address': location['location'],
                'comment': location['comment'],
            })

        new_df: pd.DataFrame = pd.DataFrame(new_data)
        self.collector.insert(new_df)
        return new_df
