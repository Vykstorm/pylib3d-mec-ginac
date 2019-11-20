'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Color
'''

from .object import Object
from array import array
from collections.abc import Iterable
from functools import partial
from itertools import repeat, chain
from copy import copy



class Color(Object):
    '''
    Instances of this class represents a color with components red, green, blue and alpha
    '''
    def __init__(self, *args):
        super().__init__()
        self._values = array('f', repeat(1.0, 4))


    def __iter__(self):
        with self.lock:
            values = tuple(self._values)
            return iter(values)


    def __getitem__(self, index):
        with self.lock:
            return self._values.__getitem__(index)


    def __setitem__(self, index, value):
        if not isinstance(index, (int, slice)):
            raise TypeError('Index must be an integer or slice')


        try:
            if isinstance(index, int):
                value = float(value)
                if value < 0 or value > 1:
                    raise TypeError
            else:
                value = array('f', map(float, value))
                for x in value:
                    if x < 0 or x > 1:
                        raise TypeError
        except TypeError:
            raise TypeError('Color components must be numbers in the range [0, 1]')

        with self.lock:
            x = copy(self._values)
            x.__setitem__(index, value)
            if len(x) != 4:
                raise ValueError('Invalid number of color components specified')
            self._values = x
            self.fire_event('color_changed')


    def set(self, *args):
        if len(args) not in (0, 3, 4):
            raise TypeError('Invalid number of arguments specified')
        if len(args) == 3:
            self.rgba = chain(args, [1])
        elif len(args) == 4:
            self.rgba = args


    @property
    def rgba(self):
        with self.lock:
            return tuple(self._values)

    @rgba.setter
    def rgba(self, values):
        self.__setitem__(slice(0, 4), values)


    @property
    def rgb(self):
        return tuple(self.__getitem__(slice(0, 3)))

    @rgb.setter
    def rgb(self, values):
        self.__setitem__(slice(0, 3), values)


    @property
    def r(self):
        return self.__getitem__(0)

    @r.setter
    def r(self, value):
        self.__setitem__(0, value)


    @property
    def g(self):
        return self.__getitem__(1)

    @g.setter
    def g(self, value):
        self.__setitem__(1, value)


    @property
    def b(self):
        return self.__getitem__(2)

    @b.setter
    def b(self, value):
        self.__setitem__(2, value)


    @property
    def a(self):
        return self.__getitem__(3)

    @a.setter
    def a(self, value):
        self.__setitem__(3, value)


    red, green, blue, alpha = r, g, b, a
    opacity = a


    def __repr__(self):
        return repr(list(map(partial(round, ndigits=3), self._values)))
