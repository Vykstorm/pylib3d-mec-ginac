'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the
C++ header ginac/ex.h to be used for this library
'''



# Imports from the standard library
from libcpp.string cimport string


cdef extern from "<ostream>" namespace "std":
    cdef cppclass ostream:
        pass


cdef extern from "<sstream>" namespace "std":
    cdef cppclass stringstream(ostream):
        stringstream() except +
        string str()


cdef extern from "ginac/print.h" namespace "GiNaC":
    cdef cppclass print_context:
        ostream& s

    cdef cppclass print_python(print_context):
        print_python(ostream& os) except +


cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        ex() except +
        ex(const double value) except +
        void print(print_context&, unsigned level=0) const
