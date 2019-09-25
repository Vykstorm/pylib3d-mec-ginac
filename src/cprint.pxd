'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the
C++ standard library headers ostream, sstream and ginac/print.h to be used for
this library
'''

# Imports from the standard library
from libcpp.string cimport string



## std::ostream
cdef extern from "<ostream>" namespace "std":
    cdef cppclass ostream:
        pass

## std::stringstream
cdef extern from "<sstream>" namespace "std":
    cdef cppclass stringstream(ostream):
        stringstream() except +
        string str()

## GiNaC::print_context, GiNaC::print_python
cdef extern from "ginac/print.h" namespace "GiNaC":
    cdef cppclass print_context:
        ostream& s

    cdef cppclass print_python(print_context):
        print_python(ostream& os) except +
