'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the
C++ header ginac/ex.h to be used for this library
'''


# Imports from the standard library
from libcpp.string cimport string

# Imports from other .pxd definition files
from src.cprint cimport print_context


cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        ex() except +
        ex(const double value) except +
        void print(print_context&, unsigned level=0) const
