from typing import List, Tuple
import logging
import spacy
NLP = spacy.load("en_core_web_sm")

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

class Phrase:
    """
    Encapsulates a command sent from a client
    """
    def __init__(self, phrase: str):
        self.verb, self.ins, self.noun_chunks, self.descriptors = self._parse(phrase)

    def _parse(self, phrase: str) -> Tuple[str, List[str], List[str]]:
        """
        Parse parts of speech from a string phrase - skip articles
        """
        doc = NLP(phrase)
        ins = [token.text for token in doc if token.pos_ == 'ADP']
        descriptors = [token.text for token in doc if token.pos_ in ('ADJ', 'ADV')]

        verbs = [token.text for token in doc if token.pos_ == 'VERB']
        assert(len(verbs) == 1)

        noun_count = len([token.text for token in doc if token.pos_ == 'NOUN'])
        if noun_count:
            noun_chunks = self._build_noun_chunks(doc)
            assert(len(ins) == noun_count - 1)
            assert(noun_count == len(noun_chunks))
        else:
            noun_chunks = []
            assert(len(ins) == 0)

        return verbs[0], ins, noun_chunks, descriptors
    
    def _build_noun_chunks(self, doc: spacy.tokens.doc.Doc) -> List[str]:
        """
        Construct noun phrases with adjectives and nouns
        """
        noun_chunks = []
        noun_chunk = None
        for token in doc:
            if token.pos_ in ('ADJ', 'NOUN'):
                if noun_chunk:
                    noun_chunk = noun_chunk + ' ' + token.text
                else:
                    noun_chunk = token.text
            if token.pos_ == 'NOUN':
                noun_chunks.append(noun_chunk)
                noun_chunk = None
        return noun_chunks
    
    def __iter__(self):
        """
        Builds a list with seperate parts of speech as elements
        """
        self.pos = self.verb
        pos_list = [self.verb]

        for chunk_index, chunk in enumerate(self.noun_chunks):
            pos_list.append(chunk)
            try:
                pos_list.append(self.ins[chunk_index])
            except IndexError:
                pass

        logging.debug(f'phrase parser iterating over: {pos_list}')
        self.pos_list = pos_list
        return self
    
    def __next__(self):
        try:
            return self.pos_list.pop(0)
        except IndexError:
            raise StopIteration
