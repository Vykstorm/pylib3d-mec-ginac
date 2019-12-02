'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Vector, Vector2
'''



######## Import statements ########


from array import array
from itertools import repeat
from functools import partial
from collections.abc import Iterable
from copy import copy
from .object import Object



######## class Vector ########

class Vector(Object):
    def __init__(self, n):
        super().__init__()
        self._values = array('f', repeat(0.0, n))


    def __iter__(self):
        with self:
            values = tuple(self._values)
            return iter(values)

    def __getitem__(self, index):
        with self:
            return self._values.__getitem__(index)

    def __len__(self):
        return len(self._values)

    def __setitem__(self, index, value):
        if not isinstance(index, (int, slice)):
            raise TypeError('Index must be an integer or slice')
        if isinstance(value, Iterable):
            value = array('f', value)

        with self:
            x = copy(self._values)
            x.__setitem__(index, value)
            if len(x) != len(self):
                raise ValueError('Invalid number of values passed')
            self._values = x
            self.fire_event('changed')

    def __repr__(self):
        return repr(list(map(partial(round, ndigits=3), self._values)))





######## class Vector2 ########


class Vector2(Vector):
    def __init__(self, *args):
        super().__init__(n=2)
        if args:
            self.set(*args)

    def set(self, *args):
        if len(args) not in (1, 2):
            raise TypeError('Invalid number of arguments specified')
        if len(args) == 1:
            args = args[0]
        self.__setitem__(slice(0,2), args)


    @property
    def x(self):
        return self.__getitem__(0)

    @x.setter
    def x(self, value):
        self.__setitem__(0, value)

    @property
    def y(self):
        return self.__getitem__(1)

    @y.setter
    def y(self, value):
        self.__setitem__(1, value)