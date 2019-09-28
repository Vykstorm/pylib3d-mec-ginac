'''
Author: Víctor Ruiz Gómez
Description: This file contains declarations of additional classes & methods
from the standard C++ library that are going to be used by this extension
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string




######## Class std::ostream ########

cdef extern from "<ostream>" namespace "std":
    cdef cppclass ostream:
        pass


######## Class std::stringstream ########

cdef extern from "<sstream>" namespace "std":
    cdef cppclass stringstream(ostream):
        stringstream() except +
        string str()
