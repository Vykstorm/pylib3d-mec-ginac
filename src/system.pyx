'''
Author: Víctor Ruiz Gómez
Description: This module defines the class System
'''


## Import statements

# Import cython internal library
cimport cython

# C++ standard library imports
from libcpp.string cimport string as c_string
from libcpp.vector cimport vector as c_vector
from libcpp.map cimport map as c_map
from libcpp.utility cimport pair as c_pair

# Import .pxd declarations
from src.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.csystem cimport System as c_System
from src.cnumeric cimport numeric as c_numeric

# Python imports
from collections.abc import Mapping
from functools import partial, partialmethod


## C Type aliases

ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list



## Helper variables, methods and types

# All numeric symbol types
_symbol_types = tuple(map(str.encode, (
    'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration',
    'parameter', 'joint_unknown', 'input'
)))



## Class which acts like a bridge between Python and C++ System class
cdef class _System:
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''
    ######## C Attributes ########

    cdef c_System* _c_handler


    ######## Constructor & Destructor ########

    def __cinit__(self):
        # Initialize C++ System object
        self._c_handler = new c_System()

    def __dealloc__(self):
        del self._c_handler


    ######## Symbol getters ########

    cdef c_map[c_string, c_symbol_numeric_list] _get_c_symbols_by_type(self):
        ## This method returns C++ map where each entry value is a vector of pointers to symbol_numeric objects
        # and keys are symbol types.
        cdef c_map[c_string, c_symbol_numeric_list] symbols_by_type
        symbols_by_type[b'coordinate'] = self._c_handler.get_Coordinates()
        symbols_by_type[b'velocity'] = self._c_handler.get_Velocities()
        symbols_by_type[b'acceleration'] = self._c_handler.get_Accelerations()
        symbols_by_type[b'aux_coordinate'] = self._c_handler.get_AuxCoordinates()
        symbols_by_type[b'aux_velocity'] = self._c_handler.get_AuxVelocities()
        symbols_by_type[b'aux_acceleration'] = self._c_handler.get_AuxAccelerations()
        symbols_by_type[b'parameter'] = self._c_handler.get_Parameters()
        symbols_by_type[b'input'] = self._c_handler.get_Inputs()
        symbols_by_type[b'joint_unknown'] = self._c_handler.get_Joint_Unknowns()
        return symbols_by_type


    cpdef get_symbols(self):
        symbols = []
        cdef c_symbol_numeric_list c_symbols
        cdef c_map[c_string, c_symbol_numeric_list] c_symbols_by_type
        cdef c_pair[c_string, c_symbol_numeric_list] c_map_entry

        c_symbols_by_type = self._get_c_symbols_by_type()
        for c_map_entry in c_symbols_by_type:
            c_symbols = c_map_entry.second
            symbols.extend([SymbolNumeric(<Py_ssize_t>c_symbol, (<bytes>c_map_entry.first).decode(), self) for c_symbol in c_symbols])

        return symbols



    cpdef get_symbol(self, name, kind=None):
        # Validate input argument types
        if not isinstance(name, (str, bytes)):
            raise TypeError('Symbol name must be a string or bytes sequence')

        if kind is not None and not isinstance(kind, (str, bytes)):
            raise TypeError('Symbol type must be a string or bytes sequence')

        # Convert input arguments to bytes
        if isinstance(name, str):
            name = name.encode()

        if isinstance(kind, str):
            kind = kind.encode()

        # Validate input argument values
        if kind is not None and kind not in _symbol_types:
            raise ValueError(f'Invalid "{kind}" symbol type')

        # Find the numeric symbol by name
        cdef c_map[c_string, c_symbol_numeric_list] c_symbols_by_type = self._get_c_symbols_by_type()
        cdef c_pair[c_string, c_symbol_numeric_list] c_map_entry
        cdef c_symbol_numeric_list c_symbols
        cdef c_symbol_numeric* c_symbol

        if kind is None:
            for c_map_entry in c_symbols_by_type:
                for c_symbol in c_map_entry.second:
                    if c_symbol.get_name() == <c_string>name:
                        return SymbolNumeric(<Py_ssize_t>c_symbol, (<bytes>c_map_entry.first).decode(), self)
        else:
            # Get symbols of an specific type
            c_symbols = c_symbols_by_type[<c_string>kind]
            for c_symbol in c_symbols:
                if c_symbol.get_name() == <c_string>name:
                    return SymbolNumeric(<Py_ssize_t>c_symbol, kind.decode(), self)

        # No symbol with such name exists
        if kind is None:
            raise IndexError(f'Symbol "{name.decode()}" not created yet')
        raise IndexError(f'{kind.decode().title().replace("_", " ")} "{name.decode()}" not created yet')




## System class for Python (it emulates the class System in C++ but also provides additional features).
class System(_System):
    def get_value(self, symbol):
        if not isinstance(symbol, (SymbolNumeric, str, bytes)):
            raise TypeError(f'Input argument must be a string or an instance of the class {SymbolNumeric.__name__}')

        if not isinstance(symbol, SymbolNumeric):
            symbol = self.get_symbol(symbol)
        return symbol.get_value()


    def set_value(self, symbol, value):
        if not isinstance(symbol, (SymbolNumeric, str, bytes)):
            raise TypeError(f'Input argument must be a string or an instance of the class {SymbolNumeric.__name__}')

        if not isinstance(symbol, SymbolNumeric):
            symbol = self.get_symbol(symbol)
        symbol.set_value(value)


    def has_symbol(self, *args, **kwargs):
        try:
            self.get_symbol(*args, **kwargs)
        except IndexError:
            return False
        return True


# Autogenerate getter_* and has_* methods
for symbol_type in _symbol_types:
    name = symbol_type.decode()
    setattr(System, 'get_' + name, partialmethod(System.get_symbol, kind=symbol_type))
    setattr(System, 'has_' + name, partialmethod(System.has_symbol, kind=symbol_type))
