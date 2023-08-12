from __future__ import annotations
from sqlalchemy.orm.session import Session
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union, Callable

from exceptions import BadArguments
from mud_parser.verb import Verb, VerbResponse

from data.models import MudObject, Room, Character

if TYPE_CHECKING:
    from mud_parser import Phrase

class Action(ABC, Verb):
    __ABSTRACT = True
    
    @staticmethod
    @abstractmethod
    def validate_phrase_structure(noun_chunks, ins):
        """
        Check that the requested command has valid arguments
        """
        raise NotImplementedError('validate_phrase_structure was not implemented!')
    
    @staticmethod
    @abstractmethod
    def execute(session: Session, character: Character, phrase: Phrase) -> Union[None, Callable]:
        """
        Execute the requested command
        """
        raise NotImplementedError('execute was not implemented!')

class Kill(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if not noun_chunks:
            raise BadArguments('Kill what?')
        if ins:
            raise BadArguments('You can\'t reach that.')
        if len(noun_chunks) > 1:
            raise BadArguments('One thing at a time, bucko.')

    @staticmethod
    def execute(session: Session, character: Character, phrase: Phrase):
        return VerbResponse(message_i='Kill what?', character_id=character.id)

class Look(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if len(ins) > 1:
            raise BadArguments('You don\'t hage x-ray vision! Try taking stuff out first.')
        if len(noun_chunks) > 1:
            raise BadArguments('You don\'t have enough eyes for that!')

    @staticmethod
    def execute(session: Session, character: Character, phrase: Phrase):
        if not phrase.target_id:
            desc = Room.get_desc(session, character.parent)
        else:
            desc = MudObject.get_desc(session, phrase.target_id)
        return VerbResponse(message_i=desc, character_id=character.id)

class Put(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        if not noun_chunks:
            raise BadArguments('Put what?')
        if not ins or len(ins) != len(noun_chunks) - 1:
            raise BadArguments(f'Put {noun_chunks[0]} where?')

    @staticmethod
    def execute(session: Session, character: Character, phrase: Phrase):
        return VerbResponse(message_i='Put what?', character_id=character.id)
