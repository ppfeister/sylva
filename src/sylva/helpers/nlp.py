import os
import spacy
from spacy.matcher import Matcher


LANGUAGE_RESOURCES: dict = {
    'en': {
        'model': 'en_core_web_md',
        'patterns': [
            [{"LEMMA": {"IN": ["live", "reside", "move"]}}, {"POS": "ADP"}, {"ENT_TYPE": "GPE"}],
            [{"LEMMA": {"IN": ["hail"]}}, {"LOWER": "from"}, {"ENT_TYPE": "GPE"}],
            [{"LOWER": {"IN": ["moved", "relocated", "shifted"]}}, {"LOWER": "to"}, {"ENT_TYPE": "GPE"}],
            [{"LOWER": "based"}, {"LOWER": {"IN": ["out", "in"]}}, {"OP": "?", "LOWER": {"IN": ["of", "from", "in"]}}, {"ENT_TYPE": "GPE"}],
            [{"LOWER": {"IN": ["born"]}}, {"LOWER": "in"}, {"ENT_TYPE": "GPE"}],
            [{"LEMMA": "grow"}, {"LOWER": "up"}, {"LOWER": "in"}, {"ENT_TYPE": "GPE"}]
        ],
        'lemmas': {'live', 'reside', 'move', 'hail', 'grow', 'born'},
        'alternate_lemmas': {'base', 'in', 'of'}, # NLP is a PITA and this is the best way so far to get things like "based out of"
        'first_person_pronouns': ['i', 'me', 'my', 'mine', 'myself'],
    }
}

class NatLangProcessor:
    """Basic natural language processor for Sylva data collection"""
    def __init__(self):
        current_file_path = os.path.dirname(__file__)
        spacy_model_base_path = os.path.join(current_file_path, '../data/nlp/spacy_models')

        if os.environ.get('LANG', 'en') == 'en' or True: # TODO Add additional language support
            language_code = 'en'

        self.nlp = spacy.load(f'{spacy_model_base_path}/{LANGUAGE_RESOURCES[language_code]["model"]}')
        self.matcher: Matcher = Matcher(self.nlp.vocab)

        patterns = LANGUAGE_RESOURCES[language_code]['patterns']
        self.matcher.add(f"RESIDENCY_PATTERN_{language_code.upper()}", patterns)

        self.lemmas = LANGUAGE_RESOURCES[language_code]['lemmas']
        self.alternate_lemmas = LANGUAGE_RESOURCES[language_code]['alternate_lemmas']
        self.first_person_pronouns = LANGUAGE_RESOURCES[language_code]['first_person_pronouns']


    def get_residences(self, message) -> list[str]:
        """Get likely residences from a given message

        Keyword Arguments:
            message {str} -- The message to search for residences in

        Returns:
            list[str] -- A list of likely residences
        """
        if not isinstance(message, str):
            raise TypeError('Message to parse must be a string')

        discovered_locations: list[str] = []

        doc = self.nlp(message)
        matches = self.matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]

            # Skip if no indication of first person
            if not any(token.lemma_.lower() in self.first_person_pronouns for token in span.sent):
                continue

            for token in span:
                if token.dep_ == 'pobj' and token.ent_type_ == "GPE" and (token.head.lemma_ in self.lemmas or token.head.lemma_ in self.alternate_lemmas):
                    discovered_locations.append(token.text)

                # Check for prepositional phrases that include residency-related lemmas
                elif token.dep_ == 'prep' and (token.head.lemma_ in self.lemmas or token.head.lemma_ in self.alternate_lemmas):
                    discovered_locations.extend(
                        child.text for child in token.children if child.dep_ == "pobj" and child.ent_type_ == "GPE"
                    )

        return list(set(discovered_locations))  # Remove duplicates, if any


