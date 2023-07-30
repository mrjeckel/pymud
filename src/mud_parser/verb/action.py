from abc import ABC, abstractmethod
from mud_parser.verb.verb import Verb

class Action(Verb, ABC):
    @staticmethod
    @abstractmethod
    def validate_phrase_structure(noun_chunks, ins):
        """
        """
        raise NotImplementedError('validate_phrase_structure was not implemented!')
    
    @staticmethod
    @abstractmethod
    def execute(phrase: str):
        """
        """
        raise NotImplementedError('execute was not implemented!')

class Kill(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        assert(len(noun_chunks) == 1)
        assert(len(ins) == 0)

    @staticmethod
    def execute(phrase: str):
        return 'Kill what?'

class Look(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        assert(len(noun_chunks) <= 1)
        assert(len(ins) <= 1)

    @staticmethod
    def execute(phrase: str):
        return 'You see nothing but darkness here in the void.'

class Put(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        assert(len(noun_chunks) > 1)
        assert(len(ins) > 0)
        assert(len(ins) == len(noun_chunks) - 1)

    @staticmethod
    def execute(phrase: str):
        return 'Put what?'
