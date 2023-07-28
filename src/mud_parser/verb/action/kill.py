from mud_parser.verb.action import Action

class Kill(Action):
    @staticmethod
    def validate_phrase_structure(noun_chunks, ins):
        assert(len(noun_chunks) == 1)
        assert(len(ins) == 0)
