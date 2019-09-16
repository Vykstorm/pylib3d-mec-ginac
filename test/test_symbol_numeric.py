'''
Author: Víctor Ruiz Gómez

Unitary test for class SymbolNumeric.
'''


import unittest
from unittest import TestCase
from src import *


class TestSymbolNumeric(TestCase):
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
