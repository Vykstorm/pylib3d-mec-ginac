'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Color
'''

######## Import statements ########

# Standard imports
from array import array
from collections.abc import Iterable
from functools import partial
from itertools import repeat, chain
from copy import copy

# Imports from other modules
from .object import Object
from .vector import Vector




# a string -> color mapping

_colors = {
    'black':    [0, 0, 0],
    'white':    [1, 1, 1],
    'red':      [1, 0, 0],
    'green':    [0, 1, 0],
    'blue':     [0, 0, 1],
    'yellow':   [1, 1, 0],
    'cyan':     [0, 1, 1],
    'magenta':  [1, 0, 1],
    'silver':   [.75]*3,
    'gray':     [.5]*3,
    'maroon':   [.5, 0, 0],
    'olive':    [.5, .5, 0],
    'purple':   [.5, 0, .5],
    'teal':     [0, .5, .5],
    'navy':     [0, 0, .5]
}



######## class Color ########

class Color(Vector):
    '''
    Instances of this class represents a color with components red, green, blue and alpha
    '''
    def __init__(self, *args):
        super().__init__(4)
        self.set(*args)

    def __setitem__(self, index, value):
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

        super().__setitem__(index, value)



    def set(self, *args):
        if len(args) not in (0, 1, 3, 4):
            raise TypeError('Invalid number of arguments specified')
        if len(args) == 1:
            if isinstance(args[0], str):
                name = args[0].lower()
                if name not in _colors:
                    raise TypeError('Invalid color name')
                args = _colors[name]
            else:
                args = args[0]
        if len(args) == 3:
            self.rgba = chain(args, [1])
        elif len(args) == 4:
            self.rgba = args


    @property
    def rgba(self):
        with self:
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
