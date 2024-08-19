import os

import pandas as pd
import spacy
import spacy.lang.en
import spacy.tokens



RM_SUBREDDIT_CSV_URL = 'https://raw.githubusercontent.com/jibalio/redditmetis/master/backend/libraries/metis_core/subreddits.csv'

RESIDENCY_HINTS: list[str] = [
    'i live',
    'i lived'
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


class nlp:
    def __init__(self):
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


    def get_residences(self, message) -> list[str]:
        """Get likely residences from a given message

        Keyword Arguments:
            message {str} -- The message to search for residences in

        Returns:
            list[str] -- A list of likely residences
        """
        return []
