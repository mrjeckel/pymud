import logging
import random

from exceptions import (UnknownVerb,
                        BadArguments)

from .verb import ACTION_DICT
from .verb import EMOTE_DICT
from .phrase import Phrase

class MudParser:
    PHRASE_ERROR = [
        'I\'m sorry, what?\r\n',
        'I don\'t understand what you want.\r\n',
        'Come again?\r\n',
        'Please try to be more coherent.\r\n'
    ]
    
    @classmethod
    def parse_data(cls, data, character):
        """
        """
        try:
            input = data.decode('utf-8').strip().lower()
            if not input:
                return b'\n'
            phrase = Phrase(input)
        except UnknownVerb:
            logging.info(f'Unable to parse data: {input} - {character}')
            return random.choice(cls.PHRASE_ERROR).encode('utf-8')
        except BadArguments as e:
            return str(e).encode('utf-8')
        
        if phrase.is_action:
            response = ACTION_DICT[phrase.verb].execute(phrase, character)
        elif phrase.is_emote:
            response = EMOTE_DICT[phrase.verb].execute(phrase, character)
        return response.encode('utf-8')
