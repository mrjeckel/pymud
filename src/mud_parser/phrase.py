import logging
import spacy

from typing import List, Tuple
from exceptions import UnknownVerb
from .verb import Emote, EMOTE_DICT
from .verb import ACTION_DICT

NLP = spacy.load("en_core_web_sm")

class Phrase:
    """
    Encapsulates a command sent from a client
    """
    EXCLUDE_FROM_NOUN_CHUNKS = ['DET']

    def __init__(self, phrase: str):
        self.is_emote = False
        self.is_action = False
        self.verb, self.ins, self.noun_chunks, self.descriptors = self._parse(phrase)

    def _parse(self, phrase: str) -> Tuple[str, List[str], List[str]]:
        """
        Parse parts of speech from a string phrase - skip articles
        """
        doc = NLP(phrase)
        verb = doc[0].text

        ins = [token.text for token in doc[1:] if token.pos_ == 'ADP']
        descriptors = []
        noun_chunks = self._build_noun_chunks(doc)

        if verb in ACTION_DICT.keys():
            self.is_action = True
            ACTION_DICT[verb].validate_phrase_structure(noun_chunks, ins)
        elif verb in EMOTE_DICT.keys():
            self.is_emote = True
            descriptors = [Emote.complete_adverb(doc[1].text)] if len(doc) > 1 else []
            Emote.validate_phrase_structure(noun_chunks, descriptors)
        else:
            raise UnknownVerb
            
        return verb, ins, noun_chunks, descriptors
    
    def _build_noun_chunks(self, doc: spacy.tokens.doc.Doc) -> List[str]:
        """
        Construct noun phrases with adjectives and nouns
        """
        noun_chunks = []
        for chunk in doc[1:].noun_chunks:
            noun_chunk = [token.text for token in chunk if token.pos_ not in self.EXCLUDE_FROM_NOUN_CHUNKS]
            noun_chunks.append(' '.join(noun_chunk))
        return noun_chunks
    
    def __iter__(self):
        """
        Builds a list with seperate parts of speech as elements
        """
        pos_list = [self.verb]

        if self.is_emote:
            pos_list.append(self.descriptors[0])
            pos_list.append(self.noun_chunks[0])
        elif self.is_action:
            for chunk_index, chunk in enumerate(self.noun_chunks):
                pos_list.append(chunk)
                try:
                    pos_list.append(self.ins[chunk_index])
                except IndexError:
                    pass        

        logging.debug(f'Phrase.__iter__: {pos_list}')
        self.pos_list = pos_list
        return self
    
    def __next__(self):
        try:
            return self.pos_list.pop(0)
        except IndexError:
            raise StopIteration
