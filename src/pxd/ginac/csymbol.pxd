'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::symbol and all its methods that
are going to be used by this library
'''


######## Imports ########

# Imports from the standard library
from libcpp.string cimport string




######## Class GiNaC::symbol ########

cdef extern from "ginac/symbol.h" namespace "GiNaC":
    cdef cppclass symbol:
        void set_name(string& name)
        void set_TeX_name(string& tex_name)
