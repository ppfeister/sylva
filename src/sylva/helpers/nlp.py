import os
import spacy
from spacy.matcher import Matcher

PRINT_TOKENS_FOR_DEBUG: bool = False

LANGUAGE_RESOURCES: dict = {
    'en': {
        'model': 'en_core_web_md',
        'patterns': [
            [{"LEMMA": {"IN": ["live", "reside", "move"]}}, {"POS": "ADP"}, {"ENT_TYPE": "GPE", "OP": "+"}],
            [{"LEMMA": {"IN": ["hail"]}}, {"LOWER": "from"}, {"ENT_TYPE": "GPE", "OP": "+"}],
            [{"LOWER": {"IN": ["moved", "relocated", "shifted"]}}, {"LOWER": "to"}, {"ENT_TYPE": "GPE", "OP": "+"}],
            [{"LOWER": "based"}, {"LOWER": {"IN": ["out", "in"]}}, {"OP": "?", "LOWER": {"IN": ["of", "from", "in"]}}, {"ENT_TYPE": "GPE", "OP": "+"}],
            [{"LOWER": {"IN": ["born"]}}, {"LOWER": "in"}, {"ENT_TYPE": "GPE", "OP": "+"}],
            [{"LEMMA": "grow"}, {"LOWER": "up"}, {"LOWER": "in"}, {"ENT_TYPE": "GPE", "OP": "+"}]
        ],
        'lemmas': {'live', 'reside', 'move', 'hail', 'grow', 'born'},
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
        self.matcher.add(f"RESIDENCY_PATTERN_{language_code.upper()}", patterns, greedy="LONGEST")

        self.lemmas = LANGUAGE_RESOURCES[language_code]['lemmas']
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
        matches = self.matcher(doc, with_alignments=True)

        assembled_location: str = ''
        for match_id, start, end, alignments in matches:
            span = doc[start:end]

            # Skip if no indication of first person
            if not any(token.lemma_.lower() in self.first_person_pronouns for token in span.sent):
                continue

            for token in span:
                if PRINT_TOKENS_FOR_DEBUG:
                    print("++++++++++++++++++++++++++++++++++++++++++")
                    print(f'New token: {token.text}')
                    print(f'DEP: {token.dep_}')
                    print(f'TYPE: {token.ent_type_}')
                    print(f'HEAD LEMMA: {token.head.lemma_}')
                    print(f'HEAD TYPE: {token.head.ent_type_}')
                    print(f'HEAD DEP: {token.head.dep_}')
                    print(f'HEAD POS: {token.head.pos_}')
                    print(f'HEAD SHAPE: {token.head.shape_}')
                    print(f'HEAD TAG: {token.head.tag_}')
                    print(f'HEAD TEXT: {token.head.text}')
                if (
                    token.dep_  == 'pobj'
                    and token.ent_type_ == "GPE"
                    and token.head.ent_type_ == 'prep'
                ) or (
                    token.ent_type_ == 'GPE'
                    and token.dep_ in ['pobj', 'compound']
                ):
                    if PRINT_TOKENS_FOR_DEBUG:
                        print(f'Found GPE token: {token.text}')
                    assembled_location += token.text + ' '

                else:
                    if assembled_location:
                        discovered_locations.append(assembled_location.strip())
                        assembled_location = ''

            if assembled_location:
                discovered_locations.append(assembled_location.strip())

        return list(set(discovered_locations))  # Remove duplicates, if any


