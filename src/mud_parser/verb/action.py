from sqlalchemy.orm.session import Session
from abc import ABC, abstractmethod

from exceptions import BadArguments, BadRoomConnection
from .verb import Verb
# TODO: we want to type-hint Phrase, but need to resolve circular dependencies

from data.models import Room, Character

class Action(Verb, ABC):
    @staticmethod
    @abstractmethod
    def validate_phrase_structure(noun_chunks, ins):
        """
        """
        raise NotImplementedError('validate_phrase_structure was not implemented!')
    
    @staticmethod
    @abstractmethod
    def execute(session: Session, character: Character, phrase: object):
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
    def execute(session: Session, character: Character, phrase: object):
        return 'Kill what?\r\n'

class Look(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if len(ins) > 1:
            raise BadArguments('You don\'t hage x-ray vision! Try taking stuff out first.\r\n')
        if len(noun_chunks) > 1:
            raise BadArguments('You don\'t have enough eyes for that!\r\n')

    @staticmethod
    def execute(session: Session, character: Character, phrase: object):
        if not phrase.noun_chunks:
            result = Room.get_desc(session, character)
        else:
            result = 'You see nothing.'
        return result

class Put(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if not noun_chunks:
            raise BadArguments('Put what?\r\n')
        if not ins or len(ins) != len(noun_chunks) - 1:
            raise BadArguments(f'Put {noun_chunks[0]} where?\r\n')

    @staticmethod
    def execute(session: Session, character: Character, phrase: object):
        return 'Put what?\r\n'

class Direction(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if noun_chunks or ins:
            raise BadArguments('Go where?\r\n')

    @staticmethod
    def execute(session: Session, character: Character, direction: str):
        try:
            Character.move(session, character, direction)
            return Look.execute(session, character, 'look')
        except BadRoomConnection:
            return 'There\'s no exit in that direction.'
    
class East(Direction):
    @staticmethod
    def execute(session: Session, character: Character, phrase: object):
        Direction.execute(session, character, phrase.verb)
