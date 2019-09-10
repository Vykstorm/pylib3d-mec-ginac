
'''
Author: Víctor Ruiz Gómez
Description: This file defines all the functions and classes declared in cystem.pxd
'''

from src.csystem cimport System
from src.csymbol_numeric cimport symbol_numeric


# Define the wrapper of System class for Python
cdef class SystemWrapper:
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''
    cdef System* system

    def __cinit__(self):
        self.system = new System()

    def __dealloc__(self):
        del self.system
