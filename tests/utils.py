'''
Author: Víctor Ruiz Gómez
Description:
This file defines helper functions used by the test cases.
'''

from operator import attrgetter




######## Helper functions ########


namegetter = attrgetter('__name__')
qualnamegetter = attrgetter('__qualname__')


def propnamegetter(prop):
    assert isinstance(prop, property) or type(prop).__name__ == 'getset_descriptor'
    if isinstance(prop, property):
        return prop.fget.__name__
    return prop.__name__

def propqualnamegetter(prop):
    assert isinstance(prop, property) or type(prop).__name__ == 'getset_descriptor'
    if isinstance(prop, property):
        return prop.fget.__qualname__
    return prop.__qualname__

docgetter = attrgetter('__doc__')

def propdocgetter(prop):
    assert isinstance(prop, property) or type(prop).__name__ == 'getset_descriptor'
    if isinstance(prop, property):
        return prop.fget.__doc__
    return prop.__doc__
