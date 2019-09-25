'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Expr, a basic wrapper of
the C++ class GiNac::ex
'''


######## Imports ########

# Cython imports
from cython.operator import dereference as c_deref

# C++ standard library imports
from libcpp.string cimport string as c_string

# Import .pxd declarations
from src.cexpression cimport ex as c_ex
from src.cprint cimport stringstream as c_sstream
from src.cprint cimport print_python as c_print_context

# Python imports




######## Helper methods ########


cdef Expr _expr_from_c(c_ex x):
    # Converts GiNac::ex to Python class Expr instance
    expr = Expr()
    expr._c_handler = x
    return expr




######## Class Expr ########

cdef class Expr:
    '''
    This class represents a symbolic expression.
    It implements a subset of the features provided by the C++ class GiNac::ex
    '''

    ######## C Attributes ########


    cdef c_ex _c_handler



    ######## Constructor ########


    def __cinit__(self, value=None):
        if value is not None:
            if not isinstance(value, (int, float)):
                raise TypeError
            self._c_handler = c_ex(value)




    ######## Metamethods ########


    def __str__(self):
        # Use GiNac print method
        cdef c_print_context* c_printer = new c_print_context(c_sstream())
        self._c_handler.print(c_deref(c_printer))
        cdef c_string s = (<c_sstream*>&c_printer.s).str()
        del c_printer
        return (<bytes>s).decode()

    def __repr__(self):
        return self.__str__()
