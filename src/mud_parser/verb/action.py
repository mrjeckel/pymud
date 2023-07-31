from abc import ABC, abstractmethod
from exceptions import BadArguments
from .verb import Verb

class Action(Verb, ABC):
    @staticmethod
    @abstractmethod
    def validate_phrase_structure(noun_chunks, ins):
        """
        """
        raise NotImplementedError('validate_phrase_structure was not implemented!')
    
    @staticmethod
    @abstractmethod
    def execute(phrase: str, character: str):
        """
        """
        raise NotImplementedError('execute was not implemented!')

class Kill(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if not noun_chunks:
            raise BadArguments('Kill what?\r\n')
        if ins:
            raise BadArguments('You can\'t reach that.\r\n')
        if len(noun_chunks) > 1:
            raise BadArguments('One thing at a time, bucko.\r\n')

    @staticmethod
    def execute(phrase: str, character: str):
        return 'Kill what?\r\n'

class Look(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if len(ins) > 1:
            raise BadArguments('You don\'t hage x-ray vision! Try taking stuff out first.\r\n')
        if len(noun_chunks) > 1:
            raise BadArguments('You don\'t have enough eyes for that!\r\n')

    @staticmethod
    def execute(phrase: str, character: str):
        return 'You see nothing but darkness here in the void.\r\n'

class Put(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if not noun_chunks:
            raise BadArguments('Put what?\r\n')
        if not ins or len(ins) != len(noun_chunks) - 1:
            raise BadArguments(f'Put {noun_chunks[0]} where?\r\n')

    @staticmethod
    def execute(phrase: str, character: str):
        return 'Put what?\r\n'
