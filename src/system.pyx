
'''
Author: Víctor Ruiz Gómez
Description: This file defines all the functions and classes declared in cystem.pxd
'''

from src.csystem cimport System as c_System

# Define the wrapper of System class for Python
cdef class System:
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''
    cdef c_System* system

    def __cinit__(self):
        self.system = new c_System()

    def __dealloc__(self):
        del self.system
