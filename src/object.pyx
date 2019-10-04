'''
Author: Víctor Ruiz Gómez
Description: This method represents the
'''

from abc import ABC
from types import MethodType


class NamedObject(ABC):
    pass

class LatexRenderable(ABC):
    def print_latex(self):
        try:
            from IPython.display import display, Math
        except ImportError:
            raise ImportError('You must have installed IPython to use print_latex function')
        display(Math(self.to_latex()))



cdef class Object:
    def __getattr__(self, key):
        if isinstance(self, NamedObject):
            if key == 'name':
                return self.get_name()

        if isinstance(self, LatexRenderable):
            if key == 'latex':
                return self.to_latex()
            if key == 'print_latex':
                return MethodType(LatexRenderable.print_latex, self)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


    def __dir__(self):
        entries = super().__dir__()
        if isinstance(self, NamedObject):
            entries.append('name')
        if isinstance(self, LatexRenderable):
            entries.extend(['latex', 'print_latex'])
        return entries


    def __repr__(self):
        return self.__str__()
