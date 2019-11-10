'''
Author: Víctor Ruiz Gómez
Description:
This file provides test cases to check that all public functions & classes of
the library are avaliable for the user (can be imported from the API)
'''

import pytest
from operator import itemgetter
from functools import partial
from utils import *


######## Tests ########


def test_classes(classes, api):
    '''
    This test checks that the next classes are avaliable:
    SymbolNumeric, Expr, Base, Matrix, Vector3D, Tensor3D, Wrench3D,
    Point, Frame, Solid, Object, System
    '''

    for public_class in api['classes']:
        if public_class not in map(namegetter, classes):
            raise TypeError(f'Missing class "{public_class}"')



def test_methods(methods, api):
    '''
    This test checks that all the methods of the classes in the public API
    are avaliable
    '''
    for public_class, public_methods in zip(api['classes'].keys(), map(itemgetter('methods'), api['classes'].values())):
        for public_method in public_methods:
            if public_class + '.' + public_method not in map(qualnamegetter, methods):
                raise TypeError(f'Missing method "{public_method}" in class "{public_class}"')



def test_system_properties(properties, api):
    '''
    This method checks that all properties defined by any of the API of the classes of this
    library are avaliable
    '''
    for public_class, public_properties in zip(api['classes'].keys(), map(itemgetter('properties'), api['classes'].values())):
        for public_prop in public_properties:
            if public_class + '.' + public_prop not in map(propqualnamegetter, properties):
                raise TypeError(f'Missing method "{public_prop}" in class "{public_class}"')




def test_global_functions(global_functions, api):
    '''
    This test checks that all global functions in the public API are avaliable in the
    library
    '''
    for public_function in api['functions']:
        if public_function not in map(namegetter, global_functions):
            raise TypeError(f'Missing global function "{public_function}"')
