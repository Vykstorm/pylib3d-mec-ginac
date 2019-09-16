'''
Author: Víctor Ruiz Gómez

Execute all the tests for this library.
The current working directory must be the same as the parent folder of this script.

First you need to install this library with the setup.py script:
python setup.py install
Its also possible to run the tests only building Cython extension:
python setup.py build_ext --inplace
'''

# Append proyect root directory to sys path
import sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))


import unittest

# Import unitary tests
from test_system import TestSystem
from test_parameter import TestParameter


if __name__ == '__main__':
    # Run all the tests
    unittest.main()
