'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac symbol_numeric.h that will be used by this library
'''

from libcpp.string cimport string

cdef extern from "symbol_numeric.h":
    cdef cppclass symbol_numeric:
        string get_name()
