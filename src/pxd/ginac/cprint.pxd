'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ print_context, print_python, print_latex
classes and the function set_print_func of GiNaC in order to be used by this
library
'''

######## Imports ########

from src.pxd.cpp cimport ostream



######## Class GiNaC::print_context & its subclasses ########

cdef extern from "ginac/print.h" namespace "GiNaC":
    cdef cppclass print_context:
        ostream& s

    cdef cppclass print_python(print_context):
        print_python(ostream&) except +

    cdef cppclass print_latex(print_context):
        print_latex(ostream&) except +



######## Function set_print_func ########

cdef extern from "ginac/registrar.h" namespace "GiNaC":
    cdef void set_print_func[T, C](void (*func)(const T&, const C&, unsigned))
