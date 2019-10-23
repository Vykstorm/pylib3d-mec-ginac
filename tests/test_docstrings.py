'''
Author: Víctor Ruiz Gómez
Description:
This file add a test cases to check that all functions and classes of the public API
of the library are properly documented with docstrings
'''

import pytest
from utils import *
from functools import partial
from operator import eq, itemgetter



######## Tests ########

def test_classes_docstrings(classes, api):
    '''
    This test case check that all classes in the public API have a non-empty docstring
    '''
    for public_class in api['classes']:
        cls = next(filter(partial(eq, public_class), map(namegetter, classes)))
        if not cls.__doc__:
            raise AssertionError(f'Missing docstring on class "{public_class}"')


def test_methods_docstrings(methods, api):
    '''
    This test case check that all methods in classes in the public API have non-empty docstrings
    '''
    for public_class, public_methods in zip(api['classes'].keys(), map(itemgetter('methods'), api['classes'].values())):
        for public_method in public_methods:
            qualname = public_class + '.' + public_method
            method = next(filter(partial(eq, qualname), map(qualnamegetter, methods)))
            if not method.__doc__:
                raise AssertionError(f'Missing docstring on method "{public_method}" in class "{public_class}"')



def test_properties_docstrings(properties, api):
    '''
    This test case check that all properties defined in classes of the public API have non-empty docstrings
    '''
    for public_class, public_props in zip(api['classes'].keys(), map(itemgetter('properties'), api['classes'].values())):
        for public_prop in public_props:
            qualname = public_class + '.' + public_prop
            prop = next(filter(partial(eq, qualname), map(propqualnamegetter, properties)))
            if not prop.__doc__:
                raise AssertionError(f'Missing docstring on property "{public_method}" in class "{public_class}"')



def test_global_functions_docstrings(global_functions, api):
    '''
    This test case check that all global functions defined in the public API have non-empty docstrings
    '''
    for public_function in api['functions']:
        func = next(filter(partial(eq, public_function), map(qualnamegetter, global_functions)))
        if not func.__doc__:
            raise AssertionError(f'Missing docstring on global function "{public_function}"')
