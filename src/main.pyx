
'''
Author: Víctor Ruiz Gómez
'''

## Import statements

# C++ standard library imports
from libcpp.string cimport string
from libcpp.vector cimport vector

# Import cython internal library
cimport cython

# Import .pxd declarations
from src.csymbol_numeric cimport symbol_numeric
from src.csystem cimport System as c_System

# Python imports
from collections.abc import Mapping
from operator import attrgetter


## Wrapper of the symbol_numeric class for Python
cdef class NumericSymbol:
    cdef symbol_numeric* handler

    def __cinit__(self, Py_ssize_t handler):
        self.handler = <symbol_numeric*>handler

    @property
    def name(self):
        return (<bytes>self.handler.get_name()).decode()

    @property
    def tex_name(self):
        return (<bytes>self.handler.print_TeX_name()).decode()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()



## Wrapper of the symbol_numeric class for Python for parameters
cdef class Parameter(NumericSymbol):
    def __str__(self):
        return f'Parameter {self.name}'




## Wrapper of System class for Python
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
        Creates a new parameter with the given name
        '''
        if self.has_parameter(name):
            raise ValueError(f'Parameter "{name}" already created')
        return Parameter(<Py_ssize_t>self.system.new_Parameter(name.encode()))


    cpdef Parameter get_parameter(self, unicode name):
        '''
        Get a parameter by name
        '''
        if not self.has_parameter(name):
            raise ValueError(f'Parameter "{name}" not created yet')
        return Parameter(<Py_ssize_t>self.system.get_Parameter(name.encode()))


    cdef bint has_parameter(self, unicode name):
        '''
        Check if a parameter with the given name exists.
        '''
        cdef vector[symbol_numeric*] ptrs = self.system.get_Parameters()
        cdef symbol_numeric* ptr
        for ptr in ptrs:
            if ptr.get_name() == <string>name.encode():
                return 1
        return 0


    cpdef object get_parameters(self):
        '''
        Retrieve a list with all the parameters created in the system.
        '''
        params = []
        cdef vector[symbol_numeric*] ptrs = self.system.get_Parameters()
        cdef symbol_numeric* ptr
        for ptr in ptrs:
            params.append(Parameter(<Py_ssize_t>ptr))
        return params


    @property
    def parameters(self):
        '''
        This property (read only) retrieves all the parameters created in a dictionary
        where keys are the parameter names and the values, instances of the class Parameter.
        '''
        params = self.get_parameters()
        return dict(zip(map(attrgetter('name'), params), params))
