'''
Author: Víctor Ruiz Gómez
Description: This file declares all classes, functions & methods of GiNaC
C++ library that are going to be used by this library.
'''


######## Imports ########


# Imports from the standard library


# Imports from other .pxd definition files
from src.cpp cimport ostream



######## Class GiNaC::print_context & its subclasses ########

cdef extern from "ginac/print.h" namespace "GiNaC":
    cdef cppclass print_context:
        ostream& s

    cdef cppclass print_python(print_context):
        print_python(ostream& os) except +


######## Class GiNaC::basic ########

cdef extern from "ginac/basic.h" namespace "GiNaC":
    cdef cppclass basic:
        pass


######## Class GiNaC::ex ########

cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        ex() except +
        ex(const double value) except +
        ex(const basic& value) except +
        void print(print_context&, unsigned level=0) const


######## Class GiNaC::numeric ########

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef cppclass numeric(basic):
        numeric(double value)

        double to_double() const
        const numeric real() const
        const numeric imag() const


######## Class GiNaC::matrix ########

cdef extern from "ginac/matrix.h" namespace "GiNaC":
    cdef cppclass matrix(basic):
        pass