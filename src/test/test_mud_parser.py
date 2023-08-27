import unittest

from unittest.mock import patch
from mud_parser import Phrase
from data.models import MudObject, Room
from exceptions import BadArguments

MUDOBJECT_ID = 1
ROOM_DESC = 'You are in the void.'
TARGET_DESC = 'a stinky green goblin'

#class TestMudParser(unittest.TestCase):
#    def test_response(self):
#        """
#        """
#        print(Room.match_short_desc())

@patch.object(Room, 'match_short_desc', lambda x, y, z: [MUDOBJECT_ID])
@patch.object(Room, 'get_desc', lambda x, y: ROOM_DESC)
class TestPhrase(unittest.TestCase):
    def test_action(self):
        """
        Test verb and noun phrase
        """
        test_phrase = Phrase(None, 'kill slimy green goblin', 1)
        self.assertEqual(test_phrase.verb, 'kill')
        self.assertEqual(test_phrase.noun_chunks[-1], 'slimy green goblin')

    def test_action_with_preposition(self):
        """
        Test verb, noun phrase, and joining preposition
        """
        test_phrase = Phrase(None, 'put big blue cracker in shiny gold chest', 1)
        self.assertEqual(test_phrase.verb, 'put')
        self.assertEqual(test_phrase.noun_chunks[0], 'big blue cracker')
        self.assertEqual(test_phrase.ins[-1], 'in')
        self.assertEqual(test_phrase.noun_chunks[-1], 'shiny gold chest')

    def test_action_with_too_many_prepositions(self):
        """
        Test that we error if noun_chunks != ins + 1
        """
        with self.assertRaises(BadArguments):
            Phrase(None, 'kill slimy green goblin at', 1)

    def test_action_without_preposition(self):
        """
        Test that we error without a preopositional modifier
        """
        with self.assertRaises(BadArguments):
            Phrase(None, 'put big blue cracker shiny gold chest', 1)
        # we need our verb lookup for this to work

    def test_emote(self):
        """
        Test emote verb
        """
        test_phrase = Phrase(None, 'laugh', 1)
        self.assertEqual(test_phrase.verb, 'laugh')

    def test_emote_with_adverb(self):
        """
        Test emote verb, adverb modifier
        """
        test_phrase = Phrase(None, 'laugh maniacally', 1)
        self.assertEqual(test_phrase.verb, 'laugh')
        self.assertEqual(test_phrase.descriptors[-1], 'maniacally', 1)

    def test_emote_with_adjective(self):
        """
        Test emote verb, adjective modifier
        """
        test_phrase = Phrase(None, 'laugh maniac', 1)
        self.assertEqual(test_phrase.verb, 'laugh')
        self.assertEqual(test_phrase.descriptors[-1], 'maniacally', 1)

    def test_emote_with_two_modifiers(self):
        """
        Test emote with two modifiers
        """
        test_phrase = Phrase(None, 'laugh joyfully maniacally', 1)
        self.assertEqual(test_phrase.verb, 'laugh')
        self.assertEqual(test_phrase.descriptors[-1], 'joyfully')

    def test_action_iteration(self):
        """
        Test iterator over an action phrase
        """
        mapping = {
            0: 'put',
            1: 'big blue cracker',
            2: 'in',
            3: 'shiny golden chest'
        }
        test_phrase = Phrase(None, ' '.join(mapping.values()), 1)

        for index, part_of_speech in enumerate(test_phrase):
            self.assertEqual(mapping[index], part_of_speech)

    def test_emote_iteration(self):
        """
        Test iterator over an emote phrase
        """
        mapping = {
            0: 'laugh',
            1: 'maniacally',
            2: 'at',
            3: 'George'
        }
        test_phrase = Phrase(None, ' '.join(mapping.values()), 1)

        for index, part_of_speech in enumerate(test_phrase):
            # we drop prepositions from emotes
            if index == 2:
                index = 3
            self.assertEqual(mapping[index], part_of_speech)
