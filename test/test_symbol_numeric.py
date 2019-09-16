'''
Author: Víctor Ruiz Gómez

Unitary test for class SymbolNumeric.
'''


import unittest
from unittest import TestCase
from itertools import chain
from random import random, randint
from src import *




class TestSymbolNumeric(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._float_values = [random() for i in range(0, 100)]
        self._int_values = [randint(-100, 100) for i in range(0, 100)]
        self._numeric_values = self._float_values + self._int_values
        self._non_numeric_values = [None, '', b'']


    def test_name(self):
        # SymbolNumeric instances have the attribute 'name' which is a string with their names.
        sys = System()
        a = sys.new_parameter('a')
        self.assertEqual(a.name, 'a')

        # Property name is only-read
        self.assertRaises(AttributeError, setattr, a, 'name', 'b')
        self.assertRaises(AttributeError, delattr, a, 'name')


    def test_tex_name(self):
        # SymbolNumeric instances have the attribute 'tex_name' which is a string with their names in latex
        sys = System()
        a = sys.new_parameter('a', '\\alpha')
        self.assertEqual(a.tex_name, '\\alpha')

        # Property tex_name is only-read
        self.assertRaises(AttributeError, setattr, a, 'tex_name', 'theta')
        self.assertRaises(AttributeError, delattr, a, 'tex_name')


    def test_value(self):
        # set_value(x) changes the numeric value of a symbol to x and get_value() returns
        # its current value
        sys = System()
        a = sys.new_parameter('a')

        # set_value accepts int or float
        for value in self._numeric_values:
            a.set_value(value)
            # get_value always returns a float object
            self.assertIsInstance(a.get_value(), float)

            # get_value returns the current numeric value
            if isinstance(value, float):
                # Precision loss between C-Python floats. Why?
                # TODO
                self.assertAlmostEqual(a.get_value(), value)
            else:
                self.assertEqual(int(a.get_value()), value)

        # set_value raises TypeError if value is not float nor int
        for value in self._non_numeric_values:
            self.assertRaises(TypeError, a.set_value,  value)


    def test_value_property(self):
        # 'value' is a property on the class SymbolNumeric (it has setter and getter but
        # not deleter)
        sys = System()
        a = sys.new_parameter('a')
        self.assertRaises(Exception, delattr, a, 'value')

        # 'value' property setter accepts int & floats as arguments
        for value in self._numeric_values:
            a.value = value

            # 'value' getter is consistent with get_value() method
            self.assertEqual(a.value, a.get_value())

        # 'value' property setter raises TypeError if input argument is not int or float
        for value in self._non_numeric_values:
            self.assertRaises(TypeError, setattr, a, 'value', value)
