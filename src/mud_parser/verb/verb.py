from sqlalchemy.orm.session import Session
from typing import Union, Tuple, List
from exceptions import BadResponse
from data.models import MudObject, Room, Character

class Verb:
    @classmethod
    def get_subclass_dict(cls):
        """
        Retreives a dictionary of subclasses - {class_name: class_object}
        """
        class_dict = {}

        for subclass in cls.__subclasses__():
            if subclass.__subclasses__():
                class_dict.update(subclass.get_subclass_dict())
            if getattr(subclass, f'_{subclass.__name__}__ABSTRACT', False) is False:
                class_dict.update({subclass.__name__.lower(): subclass})

        return class_dict

    @staticmethod
    def find_targets(session: Session, character: Character, noun_chunks: List[str]) -> List[MudObject]:
        """
        Matches noun_chunks to MudObjects with a matching short description
        """
        targets = []
        for chunk in noun_chunks:
            target_matches = Room.match_short_desc(session, chunk, character.parent)
            if target_matches:
                targets.append(target_matches[0])
        return targets
    
class VerbResponse:
    """
    Container for command response information
    """
    def __init__(self,
                 message_i: str = None,
                 character_id: int=None,
                 message_you: str = None,
                 target_id: int = None,
                 message_they: str = None,
                 room_id: int = None):
        self.message_i = self._parse(message_i)
        self.message_you = self._parse(message_you)
        self.message_they = self._parse(message_they)
        self.character_id = character_id
        self.target_id = target_id
        self.room_id = room_id

        self._validate_response()

    def _validate_response(self):
        if (self.message_i != None) != (self.character_id != None):
            raise BadResponse("Either set both response.message_i and response.character_id, or leave both unset")
        elif (self.message_you != None) != (self.target_id != None):
            raise BadResponse("Either set both response.message_you and response.target_id, or leave both unset")
        elif (self.message_they == None) == (self.message_i == None) == (self.message_you == None):
            raise BadResponse("response.message_they must be set for global and/or room messaging")
        
    def _parse(self, message: Union[Tuple[str], str]) -> str:
        """
        Converts a tuple into a multiline message
        """
        import logging
        try:
            if isinstance(message, tuple):
                return b'\r\n'.join([m.encode('utf-8') for m in message])
            return message.encode('utf-8')
        except AttributeError as e:
            logging.debug(e)
            return None
