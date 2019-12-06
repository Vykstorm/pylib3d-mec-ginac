'''
Author: Víctor Ruiz Gómez
Description: This file defines the function autocomplete
'''

######## Import statements ########

from collections.abc import Mapping
from collections import ChainMap
from operator import methodcaller
from re import match
import builtins
import keyword
from itertools import chain, filterfalse



######## autocomplete function ########

def autocomplete(text, context):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if not isinstance(context, Mapping):
        raise TypeError('context must be a mapping')

    m = match('(\w+)\.(\w*)$', text)
    if m:
        try:
            obj = eval(m.group(1))
            text, context = m.group(2), obj.__dict__
        except:
            pass
    else:
        context = ChainMap(context, builtins.__dict__)

    if text:
        names = filter(methodcaller('startswith', text), context.keys())
    else:
        names = filterfalse(methodcaller('startswith', '_'), context.keys())
    names = tuple(names)


    results = [name+'(' if callable(value) else name for name, value in zip(names, map(context.__getitem__, names))]
    return results
