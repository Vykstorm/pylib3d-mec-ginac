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
    pass


if __name__ == '__main__':
    unittest.main()
