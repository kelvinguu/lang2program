from abc import ABCMeta, abstractproperty


class ExampleFactory(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def examples(self):
        """Return an iterable of Examples."""
        raise NotImplementedError
