from .verb import Verb
from .action import Action
from .emote import Emote

ACTION_DICT = Action.get_subclass_dict()
EMOTE_DICT = Emote.get_subclass_dict()
