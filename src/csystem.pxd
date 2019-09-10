
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac System.h header which are going to be used by this library.
'''

from libcpp.vector cimport vector
from src.csymbol_numeric cimport symbol_numeric

cdef extern from "System.h":

    # Public API for System class
    cdef cppclass System:
        System() except +

        vector[symbol_numeric*] parameters
