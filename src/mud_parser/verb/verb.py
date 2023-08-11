from exceptions import BadResponse

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
        self.message_i = message_i
        self.message_you = message_you
        self.message_they = message_they
        self.character_id = character_id
        self.target_id = target_id
        self.room_id = room_id

        self._validate_response()

    def _validate_response(self):
        if (self.message_i is not None) != (self.character_id is not None):
            raise BadResponse("Either set both response.message_i and response.character_id, or leave both unset")
        elif (self.message_you is not None) != (self.target_id is not None):
            raise BadResponse("Either set both response.message_you and response.target_id, or leave both unset")
        elif self.message_they is None:
            raise BadResponse("response.message_they must be set for global and/or room messaging")
