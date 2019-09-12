'''
Author: Víctor Ruiz Gómez

Execute all the tests for this library.

But first, you need to:
- Build the library extension locally with:
python setup.py build_ext --inplace
- Set PYTHONPATH to the root directory of the library (parent directory of test)
'''


import unittest

# Import unitary tests
from test_system import TestSystem
from test_parameter import TestParameter

unittest.main()
