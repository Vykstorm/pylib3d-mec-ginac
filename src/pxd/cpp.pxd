'''
Author: Víctor Ruiz Gómez
Description: This file contains declarations of additional classes & methods
from the standard C++ library that are going to be used by this extension
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string
from src.pxd.cginac cimport basic



######## Class std::ostream ########

cdef extern from "<ostream>" namespace "std":
    cdef cppclass ostream:
        ostream& operator<<(long value)
        ostream& operator<<(double value)
        ostream& operator<<(string value)
        ostream& operator<<(const basic& ex)


######## Class std::stringstream ########

cdef extern from "<sstream>" namespace "std":
    cdef cppclass stringstream(ostream):
        stringstream() except +
        string str()
