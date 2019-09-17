
'''
Author: Víctor Ruiz Gómez
Description: This is the Cython module for the extension (it merges the source
code of all .pyx definition files)
It also performs all needed import statements to the C++ standard library and the .pxd
declaration files.
'''

## Import statements

# C++ standard library imports
from libcpp.string cimport string
from libcpp.vector cimport vector

# Import cython internal library
cimport cython

# Import .pxd declarations
from src.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.csystem cimport System as c_System
from src.cnumeric cimport numeric as c_numeric

## Include all modules
include "src/system.pyx"
include "src/symbol_numeric.pyx"
