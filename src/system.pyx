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
from src.cginac cimport numeric as c_numeric
from src.cginac cimport ex as c_ex
from src.cbase cimport Base as c_Base
from src.cmatrix cimport Matrix as c_Matrix

# Python imports
from collections import OrderedDict
from collections.abc import Mapping, Iterable
from functools import partial, partialmethod, wraps
from inspect import Signature, Parameter
from operator import attrgetter
from asciitree import LeftAligned




######## C helper methods, variables & types ########


# Type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list

# Type alias representing a list of bases (std::vector[Base*])
ctypedef c_vector[c_Base*] c_base_list

# Same for std::vector[Matrix*]
ctypedef c_vector[c_Matrix*] c_matrix_list



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

# All geometric types
_geom_obj_types = frozenset(map(str.encode, (
    'base', 'matrix'
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


def _parse_geom_obj_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Base name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name

def _parse_geom_obj_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name


def _parse_geom_obj_type(kind):
    if not isinstance(kind, (str, bytes)):
        raise TypeError(f'Type must be a str or bytes object')

    if isinstance(kind, str):
        kind = kind.encode()

    if kind not in _geom_obj_types:
        raise ValueError(f'Invalid "{kind.decode()}" geometric object type')
    return kind


def _apply_signature(params, defaults, args, kwargs):
    assert isinstance(params, Iterable)
    assert isinstance(defaults, dict)

    sig = Signature(
        parameters=[Parameter(param, Parameter.POSITIONAL_OR_KEYWORD, default=defaults.get(param, Parameter.empty)) for param in params]
    )
    bounded_args = sig.bind(*args, **kwargs)
    bounded_args.apply_defaults()
    return bounded_args.args




######## Class System ########


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

        :param str name: Name of the numeric symbol to fetch
        :param str kind: Type of symbol.
            It can be one None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
            If set to None, the search is performed over all symbols defined by this system
            regarding their types.
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

        kind_title = kind.decode().replace("_", " ")
        if self.has_symbol(name):
            raise IndexError(f'Symbol "{name.decode()}" is not a {kind_title}')
        raise IndexError(f'{kind_title} "{name.decode()}" not created yet')



    cpdef has_symbol(self, name, kind=None):
        '''has_symbol(name: str[, kind: str]) -> bool
        Check if a symbol with the given name and type exists in this system

        :param str name: Name of the symbol to check
        :param str kind: Type of symbol.
            It can be one None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
            If set to None, it does not take into account the symbol type.
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
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols()
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return dict(zip(map(attrgetter('name'), symbols), symbols))



    cpdef get_symbols_by_type(self, kind=None):
        if kind is None:
            return _System.get_symbols(self)
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
        cdef c_symbol_numeric* vel_c_symbol
        cdef c_symbol_numeric* acc_c_symbol


        # Signature of the method depends on the type of symbol
        if kind in (b'parameter', b'input', b'joint_unknown'):
            # Parse optional arguments
            if not kwargs and len(args) == 2:
                if not isinstance(args[-1], (str, bytes)):
                    kwargs['value'] = args.pop()

            name, tex_name, value = _apply_signature(
                ['name', 'tex_name', 'value'],
                {'tex_name': b'', 'value': 0.0},
                args, kwargs
            )
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

            return SymbolNumeric(<Py_ssize_t>c_symbol)


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

            bounded_args = _apply_signature(
                ['name', 'vel_name', 'acc_name', 'tex_name', 'vel_tex_name', 'acc_tex_name', 'value', 'vel_value', 'acc_value'],
                {'vel_name': None, 'acc_name': None, 'tex_name': None, 'vel_tex_name': None, 'acc_tex_name': None,
                'value': 0.0, 'vel_value': 0.0, 'acc_value': 0.0},
                args, kwargs
            )

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
                vel_c_symbol, acc_c_symbol = self._c_handler.get_AuxVelocity(names[1]), self._c_handler.get_AuxAcceleration(names[2])
            else:
                c_symbol = self._new_c_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
                vel_c_symbol, acc_c_symbol = self._c_handler.get_Velocity(names[1]), self._c_handler.get_Acceleration(names[2])

            return SymbolNumeric(<Py_ssize_t>c_symbol), SymbolNumeric(<Py_ssize_t>vel_c_symbol), SymbolNumeric(<Py_ssize_t>acc_c_symbol)

        else:
            raise RuntimeError




    ######## Geometric objects getters ########


    cdef c_vector[c_Base*] _get_c_bases(self):
        return self._c_handler.get_Bases()


    cdef c_vector[c_Matrix*] _get_c_matrices(self):
        return self._c_handler.get_Matrixs()



    cpdef _get_geom_obj(self, name, kind):
        name, kind = _parse_geom_obj_name(name), _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix

        if kind == b'base':
            c_bases = self._get_c_bases()
            for c_base in c_bases:
                if c_base.get_name() == <c_string>name:
                    return Base(<Py_ssize_t>c_base)
            raise IndexError(f'Base "{name.decode()}" not created yet')
        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            for c_matrix in c_matrices:
                if c_matrix.get_name() == <c_string>name:
                    return Matrix(<Py_ssize_t>c_matrix)
            raise IndexError(f'Matrix "{name.decode()}" not created yet')
        else:
            raise RuntimeError




    cpdef _has_geom_obj(self, name, kind):
        name, kind =  _parse_geom_obj_name(name), _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix

        if kind == b'base':
            c_bases = self._get_c_bases()
            for c_base in c_bases:
                if c_base.get_name() == <c_string>name:
                    return True
        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            for c_matrix in c_matrices:
                if c_matrix.get_name() == <c_string>name:
                    return True
        else:
            raise RuntimeError

        return False



    cpdef _get_geom_objs(self, kind):
        kind = _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix

        if kind == b'base':
            c_bases = self._get_c_bases()
            objs = [Base(<Py_ssize_t>c_base) for c_base in c_bases]
        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            objs = [Matrix(<Py_ssize_t>c_matrix) for c_matrix in c_matrices]

        return dict(zip(map(attrgetter('name'), objs), objs))




    ######## Geomeric objects constructors ########


    cpdef _new_base(self, name, args, kwargs):
        # Validate & parse base name
        name = _parse_geom_obj_name(name)


        # Check if a base with the given name already exists
        if self.has_base(name):
            raise IndexError(f'Base "{name.decode()}" already exists')

        # Validate & parse previous base, rotation tupla and angle arguments
        args = list(args)

        if args:
            new_args = []
            if not isinstance(args[0], (str, bytes, Base)):
                new_args.append(None)
            else:
                new_args.append(args.pop(0))

            if len(args) > 2:
                rotation_tupla = args[:3]
                args = args[3:]
                new_args.append(rotation_tupla)
            new_args.extend(args)
            args = new_args

        previous, rotation_tupla, rotation_angle = _apply_signature(
            ['previous', 'rotation_tupla', 'rotation_angle'],
            {'previous': None, 'rotation_tupla': (0, 0, 0), 'rotation_angle': 0},
            args, kwargs
        )

        if previous is not None:
            if not isinstance(previous, Base):
                try:
                    previous = self.get_base(previous)
                except IndexError as e:
                    raise ValueError(*e.args)
        else:
            previous = self.get_base(b'xyz')

        if not isinstance(rotation_tupla, (Iterable, Matrix)):
            raise TypeError(f'Rotation tupla must be an iterable or a Matrix object')

        if len(rotation_tupla) != 3:
            raise ValueError(f'Rotation tupla must have exactly three components')

        rotation_tupla = tuple(rotation_tupla)
        rotation_tupla = tuple(map(Expr, rotation_tupla))
        rotation_angle = Expr(rotation_angle)

        # Finally create the base
        cdef c_ex a, b, c, d
        cdef c_Base* c_prev_base

        c_prev_base = (<Base>previous)._c_handler
        a = (<Expr>rotation_tupla[0])._c_handler
        b = (<Expr>rotation_tupla[1])._c_handler
        c = (<Expr>rotation_tupla[2])._c_handler
        d = (<Expr>rotation_angle)._c_handler

        return Base(<Py_ssize_t>self._c_handler.new_Base(name, c_prev_base.get_name(), a, b, c, d))



    cpdef _new_matrix(self, name, args, kwargs):
        num_rows, num_cols = args

        cdef c_Matrix* c_matrix = new c_Matrix(<int>num_rows, <int>num_cols)
        c_matrix.set_name(name)
        return Matrix(<Py_ssize_t>self._c_handler.new_Matrix(c_matrix))





## System class for Python (it emulates the class System in C++ but also provides additional features).
class System(_System):


    ######## Get/Set symbol value ########


    def get_value(self, name):
        '''get_value(name: str) -> float
        Get the value of a numeric symbol

        :param str name: Name of the symbol
        :return: The value of the symbol on success
        :rtype: float
        :raises TypeError: If input argument is not a valid symbol name
        :raises IndexError: If there is no symbol with that name in the system
        '''
        return self.get_symbol(name).get_value()



    def set_value(self, name, value):
        '''get_value(name: str, value: float) -> float
        Changes the value of a numeric symbol

        :param str name: Name of the symbol
        :param value: New value for the symbol
        :type value: int, float
        :raises TypeError: If input arguments have invalid types
        :raises IndexError: If there is no symbol with that name in the system
        '''
        return self.get_symbol(name).set_value(value)



    def get_symbols(self):
        '''get_symbols() -> Mapping[str, SymbolNumeric]
        Get all symbols defined within this system

        :returns: Returns all the symbols defined in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''
        return _SymbolsView(self)



    def get_symbols_by_type(self, kind):
        '''get_symbols_by_type([kind: str]) -> Mapping[str, SymbolNumeric]
        Get all symbols of the given type defined within this system

        :param str kind: Must be one of the next values if set:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'
            If not set, this call is the same as get_symbols
        :returns: All symbols with the given type in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        '''
        return _SymbolsView(self, kind)




    ######## Symbol constructors ########


    def _new_symbol(self, kind, *args, **kwargs):
        return super()._new_symbol(kind, args, kwargs)



    def new_coordinate(self, *args, **kwargs):
        '''new_coordinate(name: str[, vel_name: str[, acc_name: str[, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]], [value: float[, vel_value: float[, acc_value: float]]])) -> Tuple[SymbolNumeric, SymbolNumeric, SymbolNumeric]
        Creates a new coordinate symbol and its derivative components (velocity and acceleration)

        :param str name: Name of the coordinate
        :param str vel_name: Name of the first derivative
            By default its the name of the coordinate prefixed with 'd'
        :param str acc_name: Name of the second derivative
            By default its the name of the coordinate prefixed with 'dd'

        :param str tex_name: Name in latex of the coordinate
            By default its an empty string
        :param str vel_tex_name: Name in latex of the first derivative
            By default its \dot{tex_name} if tex_name argument is set. Otherwise, its an empty string
        :param str acc_tex_name: Name in latex of the second derivative
            By default its \ddot{tex_name} if tex_name argument is set. Otherwise, its an empty string

        :param float value: The initial numeric value of the coordinate. By default 0
        :param float vel_value: The intial numeric value of the first derivative. By default 0
        :param float acc_value: The initial numeric value of the first derivative. By default 0

        :returns: The new coordinate and its derivatives created on success
        :rtype: Tuple[SymbolNumeric, SymbolNumeric, SymbolNumeric]
        :raises TypeError: If any input argument has an invalid type
        :raises ValueError: If any input argument has an invalid value
        :raises IndexError: If a symbol with the name indicated for the new coordinate (or its derivatives)
            is already created in the system

        .. note::

            You can specify the initial values of the coordinate and its derivatives
            right after the first argument (name) or any other string parameter (if all arguments are positional):

            >>> new_coordinate('a', 1, 2, 3)
            >>> new_coordinate('a', 'a2', 'a3', 1, 2)

        '''
        return self._new_symbol('coordinate', *args, **kwargs)



    def new_aux_coordinate(self, *args, **kwargs):
        '''new_aux_coordinate(name: str[, vel_name: str[, acc_name: str[, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]], [value: float[, vel_value: float[, acc_value: float]]])) -> SymbolNumeric
        Creates a new "auxiliar" coordinate symbol and its derivative components (velocity and acceleration)
        The signature is the same as for new_coordinate method
        '''
        return self._new_symbol('aux_coordinate', *args, **kwargs)




    ######## Geometric object getters ########


    def get_bases(self):
        '''get_bases() -> Mapping[str, Base]
        Get all the bases defined within this system
        :returns: All the bases in a dictionary, where keys are base names and values,
            instances of the class Base
        :rtype: Mapping[str, Base]
        '''
        return _BasesView(self)



    def get_matrices(self):
        return None




    ######## Geometric object constructors ########


    def new_base(self, name, *args, **kwargs):
        '''new_base(name: str[, previous: Union[str, Base]][...][, rotation_angle: Expr]) -> Base
        Creates a new base in this system with the given name, rotation tupla & angle

        :param str name: Must be the name of the new base
        :param previous: Is the previous base of the new base.
            By default is the "xyz" base
        :type previous: str, Base
        :param rotation_angle: Must be the rotation angle
        :param rotation_tupla: A list of three components that represents the base rotation tupla.
            It can also be a Matrix 1x3 or 3x1
        :type rotation_angle: Expr
        :type rotation_tupla: Tuple[Expr, Expr, Expr], Matrix

        :returns: The new base created on success
        :rtype: Base
        :raises TypeError: If any argument supplied has an invalid type
        :raises ValueError: If any argument supplied has an incorrect value (e.g: previous base doesnt exist)
        :raises IndexError: If there is already a base with the name specified

        .. note::
            The rotation tupla can be specified with three positional arguments
            or a unique positional or keyword argument as a list with 3 items (all of them expressions or numbers) or
            a Matrix object

            :Example:

            >>> new_base('a', 'xyz', 0, 1, 2)
            >>> new_base('a', None, 0, 1, 2)
            >>> new_base('a', 0, 1, 2)
            >>> new_base('a', [0, 1, 2])
            >>> new_base('a', rotation_tupla=[0, 1, 2])
            >>> new_base('a', rotation_tupla=new_matrix(3))

        '''
        return self._new_base(name, args, kwargs)



    def new_matrix(self, name, *args, **kwargs):
        return self._new_matrix(name, args, kwargs)




    ######## Properties ########

    @property
    def symbols(self):
        '''
        Only read property that returns all the symbols defined within this system.

        :rtype: Mapping[str, SymbolNumeric]
        '''
        return self.get_symbols()



    @property
    def bases(self):
        '''
        Only read property that returns all the bases defined within this system.

        :rtype: Mapping[str, Base]
        '''
        return self.get_bases()




    @property
    def matrices(self):
        '''
        Only read property that returns all the matrices defined within this system
        :rtype: Mapping[str, Base]
        '''
        return self.get_matrices()




    ######## Metamethods ########


    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return self.__str__()




######## Auto generation of System class methods ########


def _generate_symbol_getter_methods(symbol_type):
    name = symbol_type.decode()
    pname = name + 's' if not name.endswith('y') else name[:-1] + 'ies'
    display_name, display_pname = name.replace('_', ' '), pname.replace('_', ' ')

    # get_* method
    def getter(self, name):
        '''get_{name}(name: str) -> SymbolNumeric
        Get a {name} defined in this system

        :param str name: Name of the {display_name}
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

        :param str name: Name of the {display_name}
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



def _generate_symbol_constructor_method(symbol_type):
    name = symbol_type.decode()
    display_name = name.replace('_', ' ')

    def constructor(self, *args, **kwargs):
        '''new_{name}(name: str[, tex_name: str][, value: float]) -> SymbolNumeric
        Create a new {display_name} symbol

        :param str name: Name of the new {display_name}
        :param str tex_name: Name of the new {display_name} in latex.
            By default is an empty string if not specified.
        :param float value: Initial value for the new {dislpay_name}.
            By default is 0

        :returns: The new {display_name} symbol
        :rtype: SymbolNumeric
        :raises TypeError: If any input argument has an incorrect type.
        :raises ValueError: If any input argument has an incorrect value.
        :raises IndexError: If a numeric symbol with the specified name already
            exists in the system

        .. note::

            You can specify the initial value right after the name if
            both arguments are positional.
            e.g:
            new_{name}('x', 1)

        '''
        return self._new_symbol(symbol_type, *args, **kwargs)

    for key, value in locals().items():
        if not isinstance(value, str):
            continue
        constructor.__doc__ = constructor.__doc__.replace('{' + key + '}', value)
    constructor.__name__ = 'new_' + name
    constructor.__qualname__ = f'{System.__name__}.{constructor.__name__}'
    setattr(System, constructor.__name__, constructor)



for symbol_type in _symbol_types:
    _generate_symbol_getter_methods(symbol_type)
    if b'coordinate' not in symbol_type and symbol_type not in _derivable_symbol_types:
        _generate_symbol_constructor_method(symbol_type)





def _generate_geom_obj_getter_methods(kind):
    name = kind.decode()
    cls = name.title()
    pname = name + 's' if name != 'matrix' else 'matrices'

    # get_* method
    def getter(self, name):
        '''get_{name}(name: str) -> {cls}
        Get a {name} by name

        :param str name: Name of the {name} to find
        :returns: The {name} with the given name on success
        :rtype: {cls}
        :raises TypeError: If the input argument has an invalid type
        :raises IndexError: If no {name} exists with the given name
        '''
        return self._get_geom_obj(name, kind)

    # has_* method
    def checker(self, name):
        '''check_{name}(name: str) -> bool
        Check if a {name} exists with the given name within this system

        :param str name: Name of the {name}
        :returns: True if the {name} exists, False otherwise
        :rtype: bool
        :raises TypeError: If the input argument has an invalid type
        '''
        return self._has_geom_obj(name, kind)


    methods = [getter, checker]

    # Format method docstrings
    for method in methods:
        for key, value in locals().items():
            if not isinstance(value, str):
                continue
            method.__doc__ = method.__doc__.replace('{' + key + '}', value)

    # Change method names
    getter.__name__ = 'get_' + name
    checker.__name__ = 'has_' + name

    # Change method qualnames
    for method in methods:
        if isinstance(method, property):
            method = method.fget
        method.__qualname__ = f'{System.__name__}.{method.__name__}'

    # Add them to the System class
    for method in methods:
        setattr(System, getattr(method.fget if isinstance(method, property) else method, '__name__'), method)



for geom_obj_type in _geom_obj_types:
    _generate_geom_obj_getter_methods(geom_obj_type)







######## Helper class SymbolsView ########

class _SymbolsView(Mapping):
    '''
    Objects of this class emulates a dictionary which maps string names to numeric symbols.
    They are returned by the methods System.get_symbols and System.get_symbols_by_type.
    This class is not intentended to be instantiated by the user manually.
    '''
    def __init__(self, system, kind=None):
        '''
        Constructor.
        :param System system: An instance of the class System to fetch the numeric symbols from
        :param str kind: The kind of symbols to fetch
            By default is None (get all symbols)
        '''
        assert isinstance(system, System) and (kind is None or kind in _symbol_types)
        self.system, self.kind = system, kind

    @property
    def _symbols(self):
        return _System.get_symbols_by_type(self.system, self.kind)

    def __iter__(self):
        return iter(self._symbols)

    def __len__(self):
        return len(self._symbols)

    def __getitem__(self, name):
        return self.system.get_symbol(name, self.kind)

    def __contains__(self, name):
        return self.system.has_symbol(name, self.kind)

    def __bool__(self):
        return len(self) > 0

    def __str__(self):
        if not self:
            # No symbols at all
            return 'No symbols yet'

        # Get symbol types
        if self.kind is None:
            symbol_types = {}
            for symbol_type in _symbol_types:
                for symbol in _System.get_symbols_by_type(self.system, symbol_type).values():
                    symbol_types[symbol] = symbol_type.decode()
        else:
            symbol_types = None

        lines = []
        for name, symbol in self.items():
            line = ''
            # Print the symbol type
            if symbol_types:
                line += symbol_types[symbol].replace('_', ' ').ljust(18) + ' '

            # Print the symbol name
            line += name.ljust(12) + ' '

            # Print the symbol value
            line += str(round(symbol.value, 4)).ljust(12)

            lines.append(line)

        return '\n'.join(lines)


    def __repr__(self):
        return self.__str__()




######## Helper class BasesView ########

class _BasesView(Mapping):
    '''
    Objects of this class are instantiated and returned by System get_bases() method
    and its 'bases' property, and provides better visualization of geometric bases
    when printing them in the python console.
    This class is not intentended to be instantiated by the user manually.
    '''

    def __init__(self, system):
        self.system = system

    @property
    def _bases(self):
        return _System.get_bases(self.system)

    def __iter__(self):
        return iter(self._bases)

    def __len__(self):
        return len(self._bases)

    def __getitem__(self, name):
        return self.system.get_base(name)

    def __contains__(self, name):
        return self.system.has_base(name)

    def __bool__(self):
        return len(self) == 0

    def __str__(self):
        bases = frozenset(self._bases.values())
        roots = frozenset([base for base in bases if not base.has_previous()])

        def get_tree(base):
            children = [x for x in bases - roots if x.previous == base]
            return dict(zip(map(attrgetter('name'), children), map(get_tree, children)))

        tree = {}
        for base in roots:
            tree[base.name] = get_tree(base)

        return LeftAligned()(tree)

    def __repr__(self):
        return self.__str__()
