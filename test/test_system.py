'''
Author: Víctor Ruiz Gómez

Unitary test for class System.
To execute this test, you need first:
- Build the library extension locally with:
python setup.py build_ext --inplace
- Set PYTHONPATH to the root directory of the library (parent directory of test)
'''


import unittest
from unittest import TestCase
from operator import eq, attrgetter
from itertools import starmap, repeat

from src import *


class TestSystem(TestCase):
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
        for x in (1, None, False, b'a'):
            self.assertRaises(TypeError, sys.new_parameter, x)

        a = sys.new_parameter('a')
        # You cant create two parameters with the same name
        self.assertRaises(ValueError, sys.new_parameter, 'a')

        # You can create different parameters with different names
        b, c = tuple(map(sys.new_parameter, ('b', 'c')))

        # Objects returnes by new_parameter are Parameter instances
        for param in (a, b, c):
            self.assertIsInstance(param, Parameter)



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


    def test_predefined_parameters(self):
        '''
        Parameter 'g' is defined by default in the system
        '''
        sys = System()
        sys.get_parameter('g')
        self.assertIn('g', sys.parameters)


if __name__ == '__main__':
    unittest.main()
