import logging
import random

from .verb import ACTION_DICT
from .verb import EMOTE_DICT
from .phrase import Phrase

class MudParser:
    PHRASE_ERROR = [
        'I\'m sorry, what?',
        'I don\'t understand what you want.',
        'Come again?',
        'Please try to be more coherent.'
    ]
    
    @classmethod
    def parse_data(cls, data, character):
        """
        """
        try:
            phrase = Phrase(data.decode('utf-8'))
        except AssertionError as e:
            logging.info(f'Unable to parse data: {data} - {e} - {character}')
            return random.choice(cls.PHRASE_ERROR)
        
        if phrase.is_action:
            response = ACTION_DICT[phrase.verb].execute(phrase, character)
        elif phrase.is_emote:
            response = EMOTE_DICT[phrase.verb].execute(phrase, character)

        return response
