'''
Author: Víctor Ruiz Gómez
Description: This file defines the function autocomplete
'''

######## Import statements ########

from collections.abc import Mapping
from operator import methodcaller




######## autocomplete function ########

def autocomplete(text, context):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if not isinstance(context, Mapping):
        raise TypeError('context must be a mapping')

    return tuple(filter(methodcaller('startswith', text), context.keys()))
