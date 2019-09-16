'''
Author: Víctor Ruiz Gómez

Unitary test for class System.
'''


import unittest
from unittest import TestCase
from operator import eq, attrgetter
from itertools import starmap, repeat

from src import *


class TestSystem(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._non_strings = (1, None, False, 1.0, b'')


    def test_multiple_system(self):
        '''
        Test that System can be instantiated multiple times.
        '''
        for i in range(0, 10):
            System()


    def test_new_parameter(self):
        '''
        Tests for System.new_parameter method
        '''
        sys = System()

        # new_parameter accepts a string (parameter name) as parameter, otherwise,
        # raises an exception
        for x in self._non_strings:
            self.assertRaises(TypeError, sys.new_parameter, x)

        a = sys.new_parameter('a')
        # You cant create two parameters with the same name
        self.assertRaises(ValueError, sys.new_parameter, 'a')

        # You can create different parameters with different names
        b, c = tuple(map(sys.new_parameter, ('b', 'c')))

        # Objects returnes by new_parameter are Parameter instances
        for param in (a, b, c):
            self.assertIsInstance(param, Parameter)

        # new_parameter accepts a 2nd string (name in Latex) which is optional
        for x in (1, False, b''):
            self.assertRaises(TypeError, sys.new_parameter, 'd', x)
        d = sys.new_parameter('d', '\\delta')
        e = sys.new_parameter('e', None)


    def test_get_parameter(self):
        '''
        Tests for System.get_parameter method
        '''
        # get_parameter raises an exception if no parameter with the given
        # name exists yet
        sys = System()
        self.assertRaises(ValueError, sys.get_parameter, 'a')

        # get_parameter returns Parameter instances
        a = sys.new_parameter('a')
        self.assertIsInstance(a, Parameter)


    def test_parameters(self):
        '''
        Tests for System.parameters property
        '''
        # Property parameters returns a dictionary.
        sys = System()
        for name in ('a', 'b', 'c'):
            sys.new_parameter(name)
        self.assertIsInstance(sys.parameters, dict)

        # All dict keys are strings and values, instances of the class Parameter
        self.assertTrue(all(starmap(isinstance, zip(sys.parameters.keys(), repeat(str)))))
        self.assertTrue(all(starmap(isinstance, zip(sys.parameters.values(), repeat(Parameter)))))

        # Dict keys are the parameter names
        for key, param in sys.parameters.items():
            self.assertEqual(key, param.name)

        # parameters property is consistent with get_parameter method.
        for key, param in sys.parameters.items():
            self.assertEqual(sys.get_parameter(key).name, param.name)

        # parameters is only-read property
        self.assertRaises(AttributeError, setattr, sys, 'parameters', {})
        self.assertRaises(AttributeError, delattr, sys, 'parameters')


    def test_predefined_symbols(self):
        '''
        Test predefined symbols in a System instance.
        '''
        sys = System()
        sys.get_symbol('g')
