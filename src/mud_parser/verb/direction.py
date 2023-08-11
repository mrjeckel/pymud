from __future__ import annotations
from sqlalchemy.orm.session import Session
from typing import TYPE_CHECKING

from mud_parser.verb import Action, VerbResponse
from exceptions import BadArguments, BadRoomConnection

from data.models import Room, Character

if TYPE_CHECKING:
    from mud_parser import Phrase

class Direction(Action):
    __ABSTRACT = True

    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if noun_chunks or ins:
            raise BadArguments('Go where?')
        
    @staticmethod
    def execute(session: Session, character: Character, phrase: Phrase):
        return Direction.execute_direction(session, character, phrase.verb)

    @staticmethod
    def execute_direction(session: Session, character: Character, direction: str):
        try:
            Character.move(session, character, direction)
            room_desc = Room.get_desc(session, character.parent)
            return VerbResponse(message_i=room_desc, character_id=character.id)
        except BadRoomConnection:
            return VerbResponse(message_i='There\'s no exit in that direction.', character_id=character.id)


class North(Direction):
    pass

class East(Direction):
    pass

class NorthEast(Direction):
    pass

class NorthWest(Direction):
    pass

class South(Direction):
    pass

class West(Direction):
    pass

class SouthEast(Direction):
    pass

class SouthWest(Direction):
    pass

class N(North):
    pass

class E(East):
    pass

class NE(NorthEast):
    pass

class NW(NorthWest):
    pass

class S(South):
    pass

class W(West):
    pass

class SE(SouthEast):
    pass

class SW(SouthWest):
    pass
