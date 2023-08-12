from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy.orm.session import Session
from mud_parser.verb import Verb, VerbResponse

from data.models import MudObject, Character

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
        target_name = MudObject.get_short_desc(session, phrase.target_id)
        if phrase.target_id and descriptor:
            return VerbResponse(message_i=cls.FIRST_TARGET_STRING,
                                character_id=character.id,
                                message_you=cls.SECOND_TARGET_STRING,
                                target_id=phrase.target_id,
                                message_they=cls.THIRD_TARGET_STRING,
                                room_id=character.parent)
        if phrase.target_id:
            return VerbResponse(message_i=cls.FIRST_BASE_TARGET_STRING,
                                character_id=character.id,
                                message_you=cls.SECOND_BASE_TARGET_STRING,
                                target_id=phrase.target_id,
                                message_they=cls.THIRD_BASE_TARGET_STRING,
                                room_id=character.parent)
        if descriptor:
            return VerbResponse(message_i=cls.FIRST_STRING.format(descriptor),
                                character_id=character.id,
                                message_they=cls.SECOND_STRING,
                                room_id=character.parent)
        return VerbResponse(message_i=cls.FIRST_BASE_STRING,
                            character_id=character.id,
                            message_they=cls.THIRD_BASE_STRING,
                            room_id=character.parent)
    
    
class Laugh(Emote):
    FIRST_STRING = 'You laugh {}!'
    FIRST_BASE_STRING = 'You laugh out loud!'
    FIRST_BASE_TARGET_STRING = 'You laugh at {}!'
    SECOND_TARGET_STRING = '{} laughs {} at you!'
    SECOND_BASE_STRING = '{} laughs out you!'
    THIRD_STRING = '{} laughs {}!'
    THIRD_TARGET_STRING = '{} laughs at {} {}!'
    THIRD_BASE_STRING = '{} laughs out loud!'
    THIRD_BASE_TARGET_STRING = '{} laughs at {}!'
    

class Poke(Emote):
    FIRST_STRING = 'You hold up your index finger {}!'
    FIRST_TARGET_STRING = 'You poke {} {}.'
    FIRST_BASE_STRING = 'You hold up your index finger.'
    FIRST_BASE_TARGET_STRING = 'You poke {} in the ribs.'
    SECOND_TARGET_STRING = '{} pokes you {}!'
    SECOND_BASE_TARGET_STRING = '{} pokes you in the ribs. Ouch!'
    THIRD_STRING = '{} laughs {}!'
    THIRD_TARGET_STRING = '{} pokes {} in the ribs {}.'
    THIRD_BASE_STRING = '{} laughs out loud!'
    THIRD_BASE_TARGET_STRING = '{} pokes {} in the ribs!'
    
