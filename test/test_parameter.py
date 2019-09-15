'''
Author: Víctor Ruiz Gómez

Unitary test for class Parameter.
To execute this test, you need first:
- Build the library extension locally with:
python setup.py build_ext --inplace
- Set PYTHONPATH to the root directory of the library (parent directory of test)
'''


import unittest
from unittest import TestCase
from src import *


class TestParameter(TestCase):
    def test_name(self):
        # Parameter instances have the attribute 'name' which is a string with their names.
        sys = System()
        a = sys.new_parameter('a')
        self.assertEqual(a.name, 'a')

        # Property name is only-read
        self.assertRaises(AttributeError, setattr, a, 'name', 'b')
        self.assertRaises(AttributeError, delattr, a, 'name')


    def test_tex_name(self):
        # Parameter instances have the attribute 'tex_name' which is a string with their names in latex
        sys = System()
        a = sys.new_parameter('a', '\\alpha')
        self.assertEqual(a.tex_name, '\\alpha')

        # Property tex_name is only-read
        self.assertRaises(AttributeError, setattr, a, 'tex_name', 'theta')
        self.assertRaises(AttributeError, delattr, a, 'tex_name')


    def test_mro(self):
        # Parameter inherits from class SymbolNumeric
        self.assertEqual(Parameter.__mro__[1], SymbolNumeric)


if __name__ == '__main__':
    unittest.main()
