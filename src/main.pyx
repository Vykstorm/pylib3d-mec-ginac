
'''
Author: Víctor Ruiz Gómez
'''

# Import statements
from src.csymbol_numeric cimport symbol_numeric
from src.csystem cimport System as c_System


# Wrapper of the symbol_numeric class for Python when creating parameter objects.
cdef class Parameter:
    cdef symbol_numeric* handler



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
