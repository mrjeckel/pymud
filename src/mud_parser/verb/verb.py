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
            else:
                class_dict.update({subclass.__name__.lower(): subclass})

        return class_dict
