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


def _parse_symbol_tex_name(tex_name):
    if not isinstance(tex_name, (str, bytes)):
        raise TypeError(f'Symbol latex name must be a str or bytes object')

    if isinstance(tex_name, str):
        tex_name = tex_name.encode()

    return tex_name


def _parse_symbol_value(value):
    if not isinstance(value, float):
        try:
            value = float(value)
        except:
            raise TypeError(f'Invalid symbol numeric value')
    return value


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



    cpdef has_symbol(self, name, kind=None):
        '''has_symbol(name: str[, kind: str]) -> bool
        Check if a symbol with the given name and type exists in this system

        :param name: Name of the symbol to check
        :param kind: Type of symbol.
            It can be one None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
            If set to None, it does not take into account the symbol type.
        :type name: str
        :type kind: str
        :returns: True if a symbol with the given name and type exists, False otherwise
        :rtype: bool
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        '''
        name = _parse_symbol_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)

        # Check if symbol exists
        cdef c_symbol_numeric_list c_symbols
        if kind is None:
            c_symbols = self._get_c_symbols()
        else:
            c_symbols = self._get_c_symbols_by_type(kind)

        for c_symbol in c_symbols:
            if c_symbol.get_name() == <c_string>name:
                return True
        return False



    cpdef get_symbols(self):
        '''get_symbols() -> Mapping[str, SymbolNumeric]
        Get all symbols defined within this system

        :returns: Returns all the symbols defined in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''

        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols()
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return dict(zip(map(attrgetter('name'), symbols), symbols))



    cpdef get_symbols_by_type(self, kind):
        '''get_symbols_by_type(kind: str) -> Mapping[str, SymbolNumeric]
        Get all symbols of the given type defined within this system

        :param kind: Must be one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
        :type kind: str
        :returns: All symbols with the given type in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        '''
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols_by_type(_parse_symbol_type(kind))
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return dict(zip(map(attrgetter('name'), symbols), symbols))




    ######## Symbol constructors ########

    cdef c_symbol_numeric* _new_c_parameter(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Parameter(name, tex_name, c_numeric(value))

    cdef c_symbol_numeric* _new_c_input(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Input(name, tex_name, c_numeric(value))

    cdef c_symbol_numeric* _new_c_joint_unknown(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Joint_Unknown(name, tex_name, c_numeric(value))

    cdef c_symbol_numeric* _new_c_aux_coordinate(self,
        c_string name,     c_string vel_name,     c_string acc_name,
        c_string tex_name, c_string vel_tex_name, c_string acc_tex_name,
        double   value,    double   vel_value,    double   acc_value):
        return self._c_handler.new_AuxCoordinate(
            name, vel_name, acc_name,
            tex_name, vel_tex_name, acc_tex_name,
            c_numeric(value), c_numeric(vel_value), c_numeric(acc_value))

    cdef c_symbol_numeric* _new_c_coordinate(self,
        c_string name,     c_string vel_name,     c_string acc_name,
        c_string tex_name, c_string vel_tex_name, c_string acc_tex_name,
        double   value,    double   vel_value,    double   acc_value):
        return self._c_handler.new_Coordinate(
            name, vel_name, acc_name,
            tex_name, vel_tex_name, acc_tex_name,
            c_numeric(value), c_numeric(vel_value), c_numeric(acc_value))



    cpdef _new_symbol(self, kind, args, kwargs):
        # Validate & parse input arguments
        args = list(args)
        kind = _parse_symbol_type(kind)
        if kind in _derivable_symbol_types:
            raise ValueError(f'You cant create a {kind.decode().replace("_", " ")} symbol by hand')

        cdef c_symbol_numeric* c_symbol

        # Signature of the method depends on the type of symbol
        if kind in (b'parameter', b'input', b'joint_unknown'):
            # Parse optional arguments
            if not kwargs and len(args) == 2:
                if not isinstance(args[-1], (str, bytes)):
                    kwargs['value'] = args.pop()

            params = [
                Parameter('name', Parameter.POSITIONAL_OR_KEYWORD),
                Parameter('tex_name', Parameter.POSITIONAL_OR_KEYWORD, default=b''),
                Parameter('value', Parameter.POSITIONAL_OR_KEYWORD, default=0.0)
            ]
            bounded = Signature(parameters=params).bind(*args, **kwargs)
            bounded.apply_defaults()
            name, tex_name, value = bounded.args
            name, tex_name, value = _parse_symbol_name(name), _parse_symbol_tex_name(tex_name), _parse_symbol_value(value)

            # Check if a symbol with the name specified already exists
            if self.has_symbol(name):
                raise IndexError(f'A symbol with the name "{name.decode()}" already exists')

            # Apply a different constructor for each symbol type
            if kind == b'parameter':
                c_symbol = self._new_c_parameter(name, tex_name, value)
            elif kind == b'input':
                c_symbol = self._new_c_input(name, tex_name, value)
            elif kind == b'joint_unknown':
                c_symbol = self._new_c_joint_unknown(name, tex_name, value)


        elif kind.endswith(b'coordinate'):
            # Parse optional arguments
            if not kwargs and len(args) in range(1, 10):
                kwargs['name'] = args.pop(0)

                params = ['vel_name', 'acc_name', 'tex_name', 'vel_tex_name', 'acc_tex_name']
                while args and params and isinstance(args[0], (str, bytes)):
                    kwargs[params.pop(0)] = args.pop(0)

                params = ['value', 'vel_value', 'acc_value']
                while args and params:
                    kwargs[params.pop(0)] = args.pop(0)

            params = [
                Parameter('name', Parameter.POSITIONAL_OR_KEYWORD),
                Parameter('vel_name', Parameter.POSITIONAL_OR_KEYWORD, default=None),
                Parameter('acc_name', Parameter.POSITIONAL_OR_KEYWORD, default=None),
                Parameter('tex_name', Parameter.POSITIONAL_OR_KEYWORD, default=None),
                Parameter('vel_tex_name', Parameter.POSITIONAL_OR_KEYWORD, default=None),
                Parameter('acc_tex_name', Parameter.POSITIONAL_OR_KEYWORD, default=None),
                Parameter('value', Parameter.POSITIONAL_OR_KEYWORD, default=0.0),
                Parameter('vel_value', Parameter.POSITIONAL_OR_KEYWORD, default=0.0),
                Parameter('acc_value', Parameter.POSITIONAL_OR_KEYWORD, default=0.0)
            ]
            bounded = Signature(parameters=params).bind(*args, **kwargs)
            bounded.apply_defaults()
            bounded_args = bounded.args

            names = [_parse_symbol_name(arg) if arg is not None else None for arg in bounded_args[:3]]
            tex_names = [_parse_symbol_tex_name(arg) if arg is not None else None for arg in bounded_args[3:6]]
            values = [_parse_symbol_value(arg) for arg in bounded_args[6:9]]

            names[1:] = [name or b'd'*k + names[0] for k, name in enumerate(names[1:], 1)]
            if tex_names[0]:
                tex_names[1:] = [tex_name or b'\\' + b'd'*k + b'ot{' + tex_names[0] + b'}' for k, tex_name in enumerate(tex_names[1:], 1)]
            else:
                tex_names = [tex_name or b'' for tex_name in tex_names]


            # Check if the name of the coordinate or its components is already in use by other symbol
            for name in names:
                if self.has_symbol(name):
                    raise IndexError(f'A symbol with the name "{name.decode()}" already exists')

            # Apply a different constructor for each symbol type
            if kind.startswith(b'aux_'):
                c_symbol = self._new_c_aux_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
            else:
                c_symbol = self._new_c_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
        else:
            raise RuntimeError

        return SymbolNumeric(<Py_ssize_t>c_symbol)



## System class for Python (it emulates the class System in C++ but also provides additional features).
class System(_System):

    ######## Get/Set symbol value ########

    def get_value(self, name):
        '''get_value(name: str) -> float
        Get the value of a numeric symbol

        :param name: Name of the symbol
        :type name: str
        :return: The value of the symbol on success
        :rtype: float
        :raises TypeError: If input argument is not a valid symbol name
        :raises IndexError: If there is no symbol with that name in the system
        '''
        return self.get_symbol(name).get_value()


    def set_value(self, name, value):
        '''get_value(name: str, value: Union[int, float]) -> float
        Changes the value of a numeric symbol

        :param name: Name of the symbol
        :type name: str
        :param value: New value for the symbol
        :type value: int, float
        :raises TypeError: If input arguments have invalid types
        :raises IndexError: If there is no symbol with that name in the system
        '''
        return self.get_symbol(name).set_value(value)


    ######## Symbol constructors ########

    def new_symbol(self, kind, *args, **kwargs):
        '''new_symbol(kind: str, name: str, ...) -> SymbolNumeric
        Creates a new symbol with the type and name specified. Additional options can be indicated
        as positional or keyword arguments after the 'name' argument.

        * If kind is 'parameter', 'input' or 'joint_unknown', the signature is:
        new_symbol(kind: str, name: str[, tex_name: str][, value: float)
        where tex_name is the name of the symbol in latex and value can be used to initialize its
        numeric value.
        e.g:
        new_symbol('parameter', 'a')
        new_symbol('parameter', 'a', '\\alpha', 1.0)
        new_symbol('input', 'x', 1.0)
        new_symbol('input', name='x', value=1.0)

        * For 'coordinate' or 'aux_coordinate' symbol types, the signature is:
        new_symbol(kind: str,
            name: str   [, vel_name: str     [, acc_name: str
        [, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]],
        [value: float,  [vel_value: float,  [acc_value: float]]])

        The first three optional arguments specify the name of the coordinate (or aux coordinate) and
        its derivatives (velocity and acceleration).
        The next three arguments indicates their names for latex.
        The last three inputs will be the initial numeric values to assign for each component.

        e.g:
        new_symbol('coordinate', 'v')
        new_symbol('coordinate', 'v', 'v2', 'v3')
        new_symbol('aux_coordinate', 'p', 'xp', 'xxp', value=1, vel_value=2, acc_value=3)
        new_symbol('aux_coordinate', 'a', 'da', 'dda', '\\alpha', '\\alpha^2', '\\alpha^3', value=2.5)


        If all the arguments are positional, it is possible to specify the initial numeric values
        for the components after the 'name' argument

        e.g:
        new_symbol('coordinate', 'v', 1, 2, 3)
        new_symbol('coordinate', 'v', 'v2', 1)
        new_symbol('coordinate', 't', 't2', 't3', 1, 2)



        :param kind: Type of the new symbol. Must be one of the next list:
            'coordinate', 'aux_coordinate', 'input', 'parameter', 'joint_unknown'
        :param name: Name of the new symbol
        :param kind: Additional positional and keyword argument indicating extra options for the
            numeric symbol creation and value initialization
        :type kind: str
        :type name: str

        :returns: The new symbol created on success
        :rtype: SymbolNumeric
        :raises TypeError: If input arguments have invalid types
        :raises ValueError: If input arguments have invalid values
        :raises IndexError: If a symbol with the name indicated is already created in the system
        '''
        return self._new_symbol(kind, args, kwargs)


    ######## Properties ########

    @property
    def symbols(self):
        '''
        Only read property that returns all the symbols defined within this system.

        :rtype: Mapping[str, SymbolNumeric]
        '''
        return self.get_symbols()



    ######## Metamethods ########

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()



######## Auto generation of System methods (get_*, new_*) ########

def _generate_methods(symbol_type):
    name = symbol_type.decode()
    pname = name + 's' if not name.endswith('y') else name[:-1] + 'ies'
    display_name, display_pname = name.replace('_', ' '), pname.replace('_', ' ')

    # get_* method
    def getter(self, name):
        '''get_{name}(name: str) -> SymbolNumeric
        Get a {name} defined in this system

        :param name: Name of the {display_name}
        :type name: str
        :returns: Return the {display_name} with the given name on success
        :rtype: SymbolNumeric
        :raises TypeError: If the input argument is not a valid symbol name
        :raises IndexError: If there not exists any {display_name} with the given name within this system
        '''
        return self.get_symbol(name, kind=symbol_type)

    # has_* method
    def checker(self, name):
        '''has_{name}(name: str) -> bool
        Check if a {display_name} is defined in this system

        :param name: Name of the {display_name}
        :type name: str
        :returns: Returns True if the {display_name} exists within this system. False otherwise
        :rtype: bool
        :raises TypeError: If the input argument is not a valid symbol name
        '''
        return self.has_symbol(name, kind=symbol_type)


    # get_* method (return all symbols for the given type)
    def pgetter(self):
        '''get_{pname}() -> Mapping[str, SymbolNumeric]
        Get all {display_pname} defined in the system

        :returns: Returns a dictionary where keys are {name} names and values,
            instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''
        return self.get_symbols_by_type(symbol_type)


    # only-read property that is equivalent to the method defined above
    @property
    def pgetterprop(self):
        '''
        Read only property that returns all {display_pname} defined in the system

        :returns: Returns a dictionary where keys are {name} names and values,
            instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''
        return self.get_symbols_by_type(symbol_type)



    methods = [getter, checker, pgetter, pgetterprop]

    # Format method docstrings
    for method in methods:
        for key, value in locals().items():
            if not isinstance(value, str):
                continue
            method.__doc__ = method.__doc__.replace('{' + key + '}', value)

    # Change method names
    getter.__name__ = 'get_' + name
    checker.__name__ = 'has_' + name
    pgetter.__name__ = 'get_' + pname
    pgetterprop.fget.__name__ = pname

    # Change method qualnames
    for method in methods:
        if isinstance(method, property):
            method = method.fget
        method.__qualname__ = f'{System.__name__}.{method.__name__}'


    # Add them to the System class
    for method in methods:
        setattr(System, getattr(method.fget if isinstance(method, property) else method, '__name__'), method)



for symbol_type in _symbol_types:
    _generate_methods(symbol_type)
