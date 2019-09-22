'''
Author: Víctor Ruiz Gómez
Description: This module defines the class System
'''


######## Imports ########

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
from inspect import Signature, Parameter
from operator import attrgetter




######## C helper methods, variables & types ########

# Type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list




######## Python helper methods & variables ########

# All numeric symbol types
_symbol_types = frozenset(map(str.encode, (
    'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration',
    'parameter', 'joint_unknown', 'input'
)))

# All symbol types that cannot be created by the user (they are generated
# automatically when other kind of symbols are spawned)
_derivable_symbol_types = frozenset(map(str.encode, (
    'velocity', 'acceleration', 'aux_velocity', 'aux_acceleration'
)))


def _parse_symbol_type(kind):
    if not isinstance(kind, (str, bytes)):
        raise TypeError(f'Symbol type must be a str or bytes object')

    if isinstance(kind, str):
        kind = kind.encode()

    if kind not in _symbol_types:
        raise ValueError(f'Invalid "{kind.decode()}" symbol type')

    return kind


def _parse_symbol_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Symbol name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name



######## Class definitions ########


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

    cdef c_symbol_numeric_list _get_c_symbols_by_type(self, c_string kind):
        '''
        Get all symbols of the given type defined within this system
        :param kind: Kind of symbols to retrieve. e.g: 'parameter'
        :type kind: std::string
        :rtype: std::vector[symbol_numeric*]
        '''
        if kind == b'coordinate':
            return self._c_handler.get_Coordinates()
        if kind == b'velocity':
            return self._c_handler.get_Velocities()
        if kind == b'acceleration':
            return self._c_handler.get_Accelerations()
        if kind == b'aux_coordinate':
            return self._c_handler.get_AuxCoordinates()
        if kind == b'aux_velocity':
            return self._c_handler.get_AuxVelocities()
        if kind == b'aux_acceleration':
            return self._c_handler.get_AuxAccelerations()
        if kind == b'parameter':
            return self._c_handler.get_Parameters()
        if kind == b'input':
            return self._c_handler.get_Inputs()
        if kind == b'joint_unknown':
            return self._c_handler.get_Joint_Unknowns()


    cdef c_symbol_numeric_list _get_c_symbols(self):
        '''
        Get all symbols within this system
        :rtype: std::vector[symbol_numeric*]
        '''
        cdef c_vector[c_symbol_numeric_list] containers
        containers.push_back(self._c_handler.get_Coordinates())
        containers.push_back(self._c_handler.get_Velocities())
        containers.push_back(self._c_handler.get_Accelerations())
        containers.push_back(self._c_handler.get_AuxCoordinates())
        containers.push_back(self._c_handler.get_AuxVelocities())
        containers.push_back(self._c_handler.get_AuxAccelerations())
        containers.push_back(self._c_handler.get_Parameters())
        containers.push_back(self._c_handler.get_Inputs())
        containers.push_back(self._c_handler.get_Joint_Unknowns())

        cdef c_symbol_numeric_list symbols
        cdef size_t num_symbols = 0

        for container in containers:
            num_symbols += container.size()
        symbols.reserve(num_symbols)

        for container in containers:
            symbols.insert(symbols.end(), container.begin(), container.end())

        return symbols



    cpdef get_symbol(self, name, kind=None):
        '''get_symbol(name: str[, kind: str]) -> SymbolNumeric
        Search a numeric symbol defined within this system with the given name and type.

        :param name: Name of the numeric symbol to fetch
        :param kind: Type of symbol.
            It can be one None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
            If set to None, the search is performed over all symbols defined by this system
            regarding their types.
        :type name: str
        :type kind: str
        :returns: The numeric symbol with that name & type if it exists
        :rtype: SymbolNumeric
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        :raises IndexError: If no symbol with the given name & type is defined in the system
        '''
        name = _parse_symbol_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)

        # Find a numeric symbol by name
        cdef c_symbol_numeric_list c_symbols
        if kind is None:
            c_symbols = self._get_c_symbols()
        else:
            c_symbols = self._get_c_symbols_by_type(kind)

        cdef c_symbol_numeric* c_symbol
        for c_symbol in c_symbols:
            if c_symbol.get_name() == <c_string>name:
                return SymbolNumeric(<Py_ssize_t>c_symbol)

        # No symbol with such name exists
        if kind is None:
            raise IndexError(f'Symbol "{name.decode()}" not created yet')
        raise IndexError(f'{kind.decode().title().replace("_", " ")} "{name.decode()}" not created yet')



    cpdef get_symbols(self):
        '''get_symbols() -> Dict[str, SymbolNumeric]
        Get all symbols defined within this system

        :returns: Returns all the symbols defined in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Dict[str, SymbolNumeric]
        '''

        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols()
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return dict(zip(map(attrgetter('name'), symbols), symbols))



    cpdef _get_symbols_by_type(self, kind):
        '''get_symbols_by_type(kind: str) -> Dict[str, SymbolNumeric]
        Get all symbols of the given type defined within this system

        :param kind: Must be one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
        :type kind: str
        :returns: All symbols with the given type in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Dict[str, SymbolNumeric]
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        '''
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols_by_type(_parse_symbol_type(kind))
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return dict(zip(map(attrgetter('name'), symbols), symbols))




    ######## Symbol constructors ########




## System class for Python (it emulates the class System in C++ but also provides additional features).
class System(_System):

    ######## Get/Set symbol value ########

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


    ######## Misc methods ########

    def has_symbol(self, *args, **kwargs):
        try:
            self.get_symbol(*args, **kwargs)
        except IndexError:
            return False
        return True


    ######## Metamethods ########

    def __contains__(self, symbol):
        pass

    def __str__(self):
        pass

    def __repr__(self):
        pass



# Autogenerate get_*, new_* and has_* methods
def _generate_methods(symbol_type):
    name = symbol_type.decode()
    pname = name + 's' if not name.endswith('y') else name[:-1] + 'ies'

    getter =  partialmethod(System.get_symbol, kind=symbol_type)
    checker = partialmethod(System.has_symbol, kind=symbol_type)
    pgetter = partialmethod(System._get_symbols_by_type, symbol_type)
    pgetterprop = property(lambda self: self._get_symbols_by_type(symbol_type))

    setattr(System, 'get_' + name, getter)
    setattr(System, 'has_' + name, checker)
    setattr(System, 'get_' + pname, pgetter)
    setattr(System, pname, pgetterprop)

for symbol_type in _symbol_types:
    _generate_methods(symbol_type)
