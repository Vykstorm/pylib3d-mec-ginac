
from itertools import filterfalse



class Signature:
    def __init__(self, s):
        assert isinstance(s, str) and s
        # Compile the signature with the given string
        self._nodes = ('a', ('b'))


    def bind(self, *args, **kwargs):
        pass

        
        return args, kwargs


class use_signature:
    def __init__(self, s):
        self.sig = Signature(s)

    def __call__(self, func):
        def new_func(*args, **kwargs):
            args, kwargs = self.sig.bind(*args, **kwargs)
            return func(*args, **kwargs)
        return new_func


@use_signature('a, b')
def foo(*args, **kwargs):
    print(args)
    print(kwargs)


foo(1,2)
