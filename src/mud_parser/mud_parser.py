import logging
import random

from mud_parser.verb.action import ACTION_DICT
from mud_parser.verb.emote import EMOTE_DICT
from mud_parser import Phrase


class MudParser:
    PHRASE_ERROR = [
        'I\'m sorry, what?',
        'I don\'t understand what you want.',
        'Come again?',
        'Please try to be more coherent.'
    ]
    @classmethod
    def parse_data(cls, data):
        """
        """
        try:
            phrase = Phrase(data.decode('utf-8'))
        except AssertionError as e:
            logging.info(f'Unable to parse data: {data} - {e}')
            return random.choice(cls.PHRASE_ERROR)
        
        try:
            ACTION_DICT[phrase.verb].execute(phrase)
        except KeyError:
            EMOTE_DICT[phrase.verb].execute(phrase)
