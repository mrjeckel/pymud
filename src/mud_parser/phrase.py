from typing import List, Tuple
import logging
import spacy
NLP = spacy.load("en_core_web_sm")

class Phrase:
    """
    Encapsulates a command sent from a client
    """
    EXCLUDE_FROM_NOUN_CHUNKS = ['DET']

    def __init__(self, phrase: str):
        self.verb, self.ins, self.noun_chunks, self.descriptors = self._parse(phrase)

    def _parse(self, phrase: str) -> Tuple[str, List[str], List[str]]:
        """
        Parse parts of speech from a string phrase - skip articles
        """
        doc = NLP(phrase)
        ins = [token.text for token in doc if token.pos_ == 'ADP']
        # TODO: support JJ form for emote descriptors; we'll add a class to handle this
        descriptors = [token.text for token in doc if token.pos_ in ('ADV')]

        verbs = [token.text for token in doc if token.pos_ == 'VERB']
        assert(len(verbs) == 1)
        assert(0 <= len(descriptors) <= 1)

        # TODO: add a verb lookup to determine the appropriate number of noun_chunks , descriptors and ins
        noun_chunks = self._build_noun_chunks(doc)
        if noun_chunks and descriptors:
            assert(len(ins) == len(noun_chunks) == 1)
        elif noun_chunks:
            assert(len(ins) == len(noun_chunks) - 1)
        else:
            assert(len(ins) == 0)

        return verbs[0], ins, noun_chunks, descriptors
    
    def _build_noun_chunks(self, doc: spacy.tokens.doc.Doc) -> List[str]:
        """
        Construct noun phrases with adjectives and nouns
        """
        noun_chunks = []
        for chunk in doc.noun_chunks:
            noun_chunk = [token.text for token in chunk if token.pos_ not in self.EXCLUDE_FROM_NOUN_CHUNKS]
            noun_chunks.append(' '.join(noun_chunk))
        return noun_chunks
    
    def __iter__(self):
        """
        Builds a list with seperate parts of speech as elements
        """
        self.pos = self.verb
        pos_list = [self.verb]

        if len(self.noun_chunks) == 1 and len(self.descriptors) == 1:
            pos_list.append(self.descriptors[0])
            pos_list.append(self.noun_chunks[0])
        else:
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
