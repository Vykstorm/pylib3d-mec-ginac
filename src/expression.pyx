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
from src.cginac cimport basic as c_basic
from src.cginac cimport ex as c_ex
from src.cginac cimport print_python as c_print_context
from src.cpp cimport stringstream as c_sstream
from src.csymbol_numeric cimport symbol_numeric as c_symbol_numeric

# Python imports
from math import floor



######## Helper methods ########


cdef Expr _expr_from_c(c_ex x):
    # Converts GiNac::ex to Python class Expr instance
    # This is used instead
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
            if not isinstance(value, (int, float, SymbolNumeric, Expr)):
                raise TypeError

            if isinstance(value, (int, float)):
                self._c_handler = c_ex(<double>float(value))
            elif isinstance(value, SymbolNumeric):
                self._c_handler = c_ex(c_deref(<c_basic*>((<SymbolNumeric>value)._c_handler)))
            else:
                self._c_handler = (<Expr>value)._c_handler



    ######## Metamethods ########


    def __str__(self):
        # Use GiNac print method
        cdef c_print_context* c_printer = new c_print_context(c_sstream())
        self._c_handler.print(c_deref(c_printer))
        cdef c_string s = (<c_sstream*>&c_printer.s).str()
        del c_printer

        x = (<bytes>s).decode()

        # Try to format the expression as a number (remove decimals if its integer)
        try:
            x = float(x)
            if floor(x) == x:
                x = floor(x)
            else:
                x = round(x, 4)
            return str(x)
        except:
            return x



    def __repr__(self):
        return self.__str__()
