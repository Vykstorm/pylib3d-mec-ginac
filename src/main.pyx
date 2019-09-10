
'''
Author: Víctor Ruiz Gómez
'''

# Import statements
from libcpp.string cimport string

cimport cython
from src.csymbol_numeric cimport symbol_numeric
from src.csystem cimport System as c_System


# Wrapper of the symbol_numeric class for Python when creating parameter objects.
cdef class Parameter:
    cdef symbol_numeric* handler

    def __cinit__(self, Py_ssize_t handler):
        self.handler = <symbol_numeric*>handler

    @property
    def name(self):
        return (<bytes>self.handler.get_name()).decode()

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.__repr__()




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


    cpdef Parameter new_parameter(self, unicode name):
        '''
        Creates a new parameter.
        @param name: Is the name of the parameter.
        '''
        return Parameter(<Py_ssize_t>self.system.new_Parameter(name.encode()))

    cpdef Parameter get_parameter(self, unicode name):
        '''
        Get a parameter by name
        @param name: Name of the parameter to fetch
        '''
        cdef Py_ssize_t handler = <Py_ssize_t>self.system.get_Parameter(name.encode())
        if handler == 0:
            raise AttributeError(f'Parameter {name} not created yet in the system')
        return Parameter(handler)
