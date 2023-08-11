from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm.session import Session
from mud_parser.verb import Verb, VerbResponse

from data.models import Character, Room

if TYPE_CHECKING:
    from mud_parser import Phrase

class Emote(Verb):
    __ABSTRACT = True

    ADVERBS = [
        'accidentally',
        'angrily',
        'anxiously',
        'awkwardly',
        'badly',
        'beautifully',
        'blindly',
        'boldly',
        'bravely',
        'brightly',
        'busily',
        'calmly',
        'carefully',
        'carelessly',
        'cautiously',
        'cheerfully',
        'clearly',
        'closely',
        'correctly',
        'courageously',
        'cruelly',
        'daringly',
        'deliberately',
        'doubtfully',
        'eagerly',
        'easily',
        'elegantly',
        'enormously',
        'enthusiastically',
        'equally',
        'eventually',
        'exactly',
        'faithfully',
        'fiercely',
        'fondly',
        'foolishly',
        'fortunately',
        'frankly',
        'frantically',
        'generously',
        'gently',
        'gladly',
        'gracefully',
        'greedily',
        'happily',
        'hard',
        'hastily',
        'healthily',
        'honestly',
        'hungrily',
        'hurriedly',
        'inadequately',
        'ingeniously',
        'innocently',
        'inquisitively',
        'irritably',
        'joyously',
        'joyfully',
        'justly',
        'kindly',
        'lazily',
        'loosely',
        'loudly',
        'madly',
        'maniacally',
        'mysteriously',
        'neatly',
        'nervously',
        'noisily',
        'obediently',
        'openly',
        'painfully',
        'patiently',
        'perfectly',
        'politely',
        'poorly',
        'powerfully',
        'promptly',
        'punctually',
        'quickly',
        'quietly',
        'rapidly',
        'rarely',
        'really',
        'recklessly',
        'regularly',
        'reluctantly',
        'repeatedly',
        'rightfully',
        'roughly',
        'rudely',
        'sadly',
        'safely',
        'selfishly',
        'sensibly',
        'seriously',
        'sharply',
        'shyly',
        'silently',
        'sleepily',
        'slowly',
        'smoothly',
        'softly',
        'solemnly',
        'speedily',
        'stealthily',
        'sternly',
        'straight',
        'stupidly',
        'successfully',
        'suddenly',
        'suspiciously',
        'swiftly',
        'tenderly',
        'tensely',
        'thoughtfully',
        'tightly',
        'truthfully',
        'unexpectedly',
        'victoriously',
        'violently',
        'vivaciously',
        'warmly',
        'weakly',
        'wearily',
        'wildly',
        'wisely'
    ]

    BASE_STRING = None
    MODIFIED_STRING = None

    @staticmethod
    def validate_phrase_structure(noun_chunks, descriptors):
        if noun_chunks:
            assert(len(noun_chunks) == 1)
        if descriptors:
            assert(len(descriptors) == 1)

    @classmethod
    def complete_adverb(cls, word):
        if len(word) >= 3:
            for adverb in cls.ADVERBS:
                if word in adverb:
                    return adverb
        return None
    
    @classmethod
    def execute(cls, session: Session, character: Character, phrase: Phrase):
        descriptor = phrase.descriptors[0] if phrase.descriptors else None
        target_id = Room.get_character_id(session, _, character.room_id)
        if descriptor:
            return VerbResponse(message_i=cls.FIRST_STRING.format(descriptor),
                                character_id=character.id,
                                message_You=cls.SECOND_STRING)
        else:
            return VerbResponse(message_i=cls.FIRST_BASE_STRING,
                                character_id=character.id,
                                message_you=cls.SECOND_BASE_STRING,
                                target_id=target_id,
                                message_they=cls.THIRD_BASE_STRING,
                                room_id=character.room_id)
    
    
class Laugh(Emote):
    FIRST_BASE_STRING = 'You laugh out loud!'
    FIRST_STRING = 'You laugh {}!'
    SECOND_BASE_STRING = '{} laughs out you!'
    SECOND_STRING = '{} laughs {} at you!'
    THIRD_BASE_STRING = '{} laughs out loud!'
    THIRD_STRING = '{} laughs {}!'
