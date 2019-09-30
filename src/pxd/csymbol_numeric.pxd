'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac symbol_numeric.h that will be used by this library
'''



######## Imports ########

# Imports from the standard library
from libcpp.string cimport string

# Imports from other .pxd files
from src.pxd.cginac cimport numeric, symbol



######## Class symbol_numeric ########

cdef extern from "symbol_numeric.h":
    cdef cppclass symbol_numeric(symbol):
        symbol_numeric(string name)

        string get_name()
        string print_TeX_name()
        numeric get_value()
        void set_value(numeric value)
