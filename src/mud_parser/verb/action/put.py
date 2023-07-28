from mud_parser.verb.action import Action

class Put(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        assert(len(noun_chunks) > 1)
        assert(len(ins) > 0)
        assert(len(ins) == len(noun_chunks) - 1)
