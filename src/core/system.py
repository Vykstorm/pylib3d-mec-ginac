'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class System
'''


######## Import statements ########


# From the Cython extension
from lib3d_mec_ginac_ext import _System, _symbol_types, _geom_types, _parse_symbol_type, _parse_numeric_value
from lib3d_mec_ginac_ext import *

# From other modules
from ..utils.events import EventProducer

# Standard imports
import math
from collections.abc import MutableMapping
from types import SimpleNamespace
from functools import partial, lru_cache
from operator import methodcaller
import numpy as np
from tabulate import tabulate






######## System class ########


class System(_System, EventProducer):
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''


    ######## Constructor ########


    def __init__(self):
        _System.__init__(self)
        EventProducer.__init__(self)

        # This will store the symbol numeric values (1 vector per symbol type)
        symbols_values = {}
        for symbol_type in map(methodcaller('decode'), _symbol_types):
            symbols_values[symbol_type] = SymbolsValuesMapping()
        self._symbols_values = symbols_values
        self._time_value = self.get_time()._get_value()

        # Initialize predefined symbol values
        for symbol in self._get_symbols():
            if symbol == self.get_time():
                continue
            symbols_values[symbol.get_type()][symbol.get_name()] = symbol._get_value()

        # This variable is used to store the init symbols values ( as a numpy array )
        # to restore them when the simulation is restarted.
        self._state = None

        try:
            from ..drawing.scene import Scene
            # Create scene visualizer (to show drawings)
            self._scene = Scene(self)
        except ImportError as e:
            # No problem, it means the GUI is not installed
            self._scene = None


    ######## Get/Set symbol value ########


    def get_value(self, symbol):
        '''get_value(symbol: str | SymbolNumeric) -> numeric
        Get the value of a numeric symbol

        :param symbol: The symbol to get its numeric value
        :type symbol: str, SymbolNumeric
        :return: The value of the symbol on success
        :rtype: numeric
        :raises TypeError: If input argument is not a valid symbol name
        :raises IndexError: If there is no symbol with that name in the system
        '''
        if not isinstance(symbol, SymbolNumeric):
            symbol = self.get_symbol(symbol)

        if symbol == self.get_time():
            return self._time_value
        values = self._symbols_values[symbol.get_type()]
        return values[symbol.get_name()]



    def set_value(self, symbol, value):
        '''set_value(symbol: str | SymbolNumeric, value: numeric) -> numeric
        Changes the value of a numeric symbol

        :param symbol: The symbol to change its value
        :param value: New value for the symbol
        :type symbol: str, SymbolNumeric
        :type value: numeric
        :raises TypeError: If input arguments have invalid types
        :raises IndexError: If there is no symbol with that name in the system
        '''
        if not isinstance(symbol, SymbolNumeric):
            symbol = self.get_symbol(symbol)
        value = _parse_numeric_value(value)

        if symbol == self.get_time():
            self._time_value = value
        else:
            values = self._symbols_values[symbol.get_type()]
            values[symbol.get_name()] = value
        self.fire_event('symbol_value_changed', symbol)



    ######## Getters ########


    def get_symbol(self, name, kind=None):
        '''get_symbol(name: str[, kind: str]) -> SymbolNumeric
        Search a numeric symbol defined within this system with the given name and type.

            :Example:

            >>> new_param('a', 1)
            a = 1
            >>> new_input('b', 2)
            b = 2

            >>> get_symbol('a')
            a = 1
            >>> get_symbol('b')
            b = 2

            >>> get_symbol('a', 'parameter')
            a = 1
            >>> get_symbol('b', 'input')
            b = 2

            >>> get_symbol('a', 'joint_unknown')
            IndexError: Symbol "a" is not a joint unknown

            >>> get_symbol('x')
            IndexError: Symbol "x" not created yet




        :param str name: Name of the numeric symbol to fetch
        :param str kind: Type of symbol.
            It can be None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'

            .. note::
                If set to None, the search is performed over all symbols defined by this system
                regarding their types.

        :returns: The numeric symbol with that name & type if it exists
        :rtype: SymbolNumeric
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        :raises IndexError: If no symbol with the given name & type is defined in the system
        '''
        return self._get_symbol(name, kind)


    def get_time(self):
        '''get_time() -> SymbolNumeric
        Get the time symbol.

        :rtype: SymbolNumeric
        '''
        return self._get_time()


    def get_coordinate(self, name):
        return self.get_symbol(name, b'coordinate')

    def get_velocity(self, name):
        return self.get_symbol(name, b'velocity')

    def get_acceleration(self, name):
        return self.get_symbol(name, b'acceleration')

    def get_aux_coordinate(self, name):
        return self.get_symbol(name, b'aux_coordinate')

    def get_aux_velocity(self, name):
        return self.get_symbol(name, b'aux_velocity')

    def get_aux_acceleration(self, name):
        return self.get_symbol(name, b'aux_acceleration')

    def get_parameter(self, name):
        return self.get_symbol(name, b'parameter')

    def get_joint_unknown(self, name):
        return self.get_symbol(name, b'joint_unknown')

    def get_input(self, name):
        return self.get_symbol(name, b'input')

    def get_base(self, name):
        return self._get_base(name)

    def get_matrix(self, name):
        return self._get_matrix(name)

    def get_vector(self, name):
        return self._get_vector(name)

    def get_tensor(self, name):
        return self._get_tensor(name)

    def get_point(self, name):
        return self._get_point(name)

    def get_frame(self, name):
        return self._get_frame(name)

    def get_solid(self, name):
        return self._get_solid(name)

    def get_wrench(self, name):
        return self._get_wrench(name)



    get_coord = get_coordinate
    get_vel = get_velocity
    get_acc = get_acceleration

    get_aux_coord = get_aux_coordinate
    get_aux_vel = get_aux_velocity
    get_aux_acc = get_aux_acceleration

    get_param = get_parameter
    get_unknown = get_joint_unknown




    def has_symbol(self, name, kind=None):
        '''has_symbol(name: str[, kind: str]) -> bool
        Check if a symbol with the given name and type exists in this system

            :Example:

            >>> a, b = new_param('a'), new_input('b')
            >>> has_symbol('a')
            True
            >>> has_symbol('b')
            True
            >>> has_symbol('a', 'parameter')
            True
            >>> has_symbol('b', 'parameter')
            False


        :param str name: Name of the symbol to check
        :param str kind: Type of symbol.
            It can be one None (by default) or one of the next values:
            'coordinate', 'velocity', 'acceleration',
            'aux_coordinate', 'aux_velocity', 'aux_acceleration',
            'parameter', 'input', 'joint_unknown'

            .. note::
                If set to None, it does not take into account the symbol type.
        :returns: True if a symbol with the given name and type exists, False otherwise
        :rtype: bool
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If input arguments have incorrect values
        '''
        return self._has_symbol(name, kind)



    def has_coordinate(self, name):
        return self.has_symbol(name, b'coordinate')

    def has_velocity(self, name):
        return self.has_symbol(name, b'velocity')

    def has_acceleration(self, name):
        return self.has_symbol(name, b'acceleration')

    def has_aux_coordinate(self, name):
        return self.has_symbol(name, b'aux_coordinate')

    def has_aux_velocity(self, name):
        return self.has_symbol(name, b'aux_velocity')

    def has_aux_acceleration(self, name):
        return self.has_symbol(name, b'aux_acceleration')

    def has_parameter(self, name):
        return self.has_symbol(name, b'parameter')

    def has_joint_unknown(self, name):
        return self.has_symbol(name, b'joint_unknown')

    def has_input(self, name):
        return self.has_symbol(name, b'input')


    def has_base(self, name):
        return self._has_base(name)

    def has_matrix(self, name):
        return self._has_matrix(name)

    def has_vector(self, name):
        return self._has_vector(name)

    def has_tensor(self, name):
        return self._has_tensor(name)

    def has_point(self, name):
        return self._has_point(name)

    def has_frame(self, name):
        return self._has_frame(name)

    def has_solid(self, name):
        return self._has_solid(name)

    def has_wrench(self, name):
        return self._has_wrench(name)


    has_coord = has_coordinate
    has_vel = has_velocity
    has_acc = has_acceleration

    has_aux_coord = has_aux_coordinate
    has_aux_vel = has_aux_velocity
    has_aux_acc = has_aux_acceleration

    has_param = has_parameter
    has_unknown = has_joint_unknown




    def get_symbols(self, kind=None):
        '''get_symbols([kind: str]) -> Mapping[str, SymbolNumeric]
        Get all symbols defined within this system with the given type.

            :Example:

            >>> a, b, c = new_param('a', 1), new_joint_unknown('b', 2), new_input('c', 3)
            >>> symbols = get_symbols()
            >>> list(symbols)
            ['a', 'b', 'c']
            >>> symbols['a'].value
            3
            >>> 'b' in symbols
            True

            >>> inputs = get_symbols('input')
            >>> list(inputs)
            ['c']
            >>> inputs['c'].value
            3
            >>> 'b' in inputs
            False



        :param str kind: Its an optional argument that can be used to retrieve
            only symbols with the given type. Must be one of the next values:
            ‘coordinate’, ‘velocity’, ‘acceleration’, ‘aux_coordinate’,
            ‘aux_velocity’, ‘aux_acceleration’, ‘parameter’, ‘input’, ‘joint_unknown’

            .. note::
                If set to None (by default), return all numeric symbols regarding
                their types

        :returns: Returns all the symbols defined in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''
        return SymbolsMapping(self, kind)


    def get_coordinates(self):
        return self.get_symbols(b'coordinate')

    def get_velocities(self):
        return self.get_symbols(b'velocity')

    def get_accelerations(self):
        return self.get_symbols(b'acceleration')

    def get_aux_coordinates(self):
        return self.get_symbols(b'aux_coordinate')

    def get_aux_velocities(self):
        return self.get_symbols(b'aux_velocity')

    def get_aux_accelerations(self):
        return self.get_symbols(b'aux_acceleration')

    def get_parameters(self):
        return self.get_symbols(b'parameter')

    def get_joint_unknowns(self):
        return self.get_symbols(b'joint_unknown')

    def get_inputs(self):
        return self.get_symbols(b'input')


    def get_bases(self):
        return BasesMapping(self)

    def get_matrices(self):
        return MatricesMapping(self)

    def get_vectors(self):
        return VectorsMapping(self)

    def get_tensors(self):
        return TensorsMapping(self)

    def get_points(self):
        return PointsMapping(self)

    def get_frames(self):
        return FramesMapping(self)

    def get_solids(self):
        return SolidsMapping(self)

    def get_wrenches(self):
        return WrenchesMapping(self)



    get_coords = get_coordinates
    get_aux_coords = get_aux_coordinates

    get_params = get_parameters
    get_unknowns = get_joint_unknowns




    def get_symbols_matrix(self, kind):
        '''get_symbols_matrix(kind: str) -> Matrix
        Get a matrix with all the symbols of the given type defined within the system.

            :Example:

            >>> new_param('a'), new_param('b'), new_param('c')
            >>> m = get_symbols_matrix('parameter')
            >>> m * 2
            [ 2*a, 2*b, 2*c ]

        :param kind: Must be one of the next values:
            ‘acceleration’, ‘aux_coordinate’, ‘aux_velocity’,
            ‘aux_acceleration’, ‘parameter’, ‘input’, ‘joint_unknown’

        :rtype: Matrix

        '''
        return super()._get_symbols_matrix(kind)

    def get_coordinates_matrix(self):
        return self.get_symbols_matrix(b'coordinate')

    def get_velocities_matrix(self):
        return self.get_symbols_matrix(b'velocity')

    def get_accelerations_matrix(self):
        return self.get_symbols_matrix(b'acceleration')

    def get_aux_coordinates_matrix(self):
        return self.get_symbols_matrix(b'aux_coordinate')

    def get_aux_velocities_matrix(self):
        return self.get_symbols_matrix(b'aux_velocity')

    def get_aux_accelerations_matrix(self):
        return self.get_symbols_matrix(b'aux_acceleration')

    def get_parameters_matrix(self):
        return self.get_symbols_matrix(b'parameter')

    def get_joint_unknowns_matrix(self):
        return self.get_symbols_matrix(b'joint_unknown')

    def get_inputs_matrix(self):
        return self.get_symbols_matrix(b'input')


    get_coords_matrix = get_coordinates_matrix
    get_aux_coords_matrix = get_aux_coordinates_matrix
    get_params_matrix = get_parameters_matrix
    get_unknowns_matrix = get_joint_unknowns_matrix



    def get_symbols_values(self, kind):
        '''get_symbols_values() -> SymbolsValuesMapping
        Returns a special structure which can be used to update the numerical values of the
        symbols of the system, and it can be treated as a regular numpy array:

        :param kind: The kind of symbols. The returned value can be used to fetch or
            set the numeric values of symbols with the given type
            :Example:

            >>> new_param('a', 1), new_param('b', 0), new_param('c', 2)
            >>> get_params()
            g  9.8
            a  1
            b  0
            c  2
            >>> p_values = get_symbols_values('parameter')
            >>> p_values
            array([[9.8],
                   [1. ],
                   [0. ],
                   [2. ]])
            >>> param_values -= 1
            >>> param_values
            array([[ 8.8],
                   [ 0. ],
                   [-1. ],
                   [ 1. ]])
            >>> param_values *= 2
            array([[17.6],
                   [ 0. ],
                   [-2. ],
                   [ 2. ]])
            >>> get_params()
            g  17.6
            a   0
            b  -2
            c   2

        '''
        return self._symbols_values[_parse_symbol_type(kind).decode()].as_array()


    get_values = get_symbols_values

    def get_coordinates_values(self):
        return self.get_symbols_values('coordinate')

    def get_velocities_values(self):
        return self.get_symbols_values('velocity')

    def get_accelerations_values(self):
        return self.get_symbols_values('acceleration')

    def get_aux_coordinates_values(self):
        return self.get_symbols_values('aux_coordinate')

    def get_aux_velocities_values(self):
        return self.get_symbols_values('aux_velocity')

    def get_aux_accelerations_values(self):
        return self.get_symbols_values('aux_acceleration')

    def get_parameters_values(self):
        return self.get_symbols_values('parameter')

    def get_joint_unknowns_values(self):
        return self.get_symbols_values('joint_unknown')

    def get_inputs_values(self):
        return self.get_symbols_values('input')


    get_coords_values = get_coordinates_values
    get_aux_coords_values = get_aux_coordinates_values
    get_params_values = get_parameters_values
    get_unknowns_values = get_joint_unknowns_values





    def get_scene(self):
        '''get_scene() -> Scene
        Get the 3D scene manager object associated to this system

        :rtype: Viewer or None
        :raises RuntimeError: If the graphical environment was not installed
        '''
        if self._scene is None:
            raise RuntimeError('The graphical environment was not installed')
        return self._scene





    ######## Constructors ########


    def new_symbol(self, kind, *args, **kwargs):
        result = super()._new_symbol(kind, args, kwargs)
        if isinstance(result, SymbolNumeric):
            result = (result,)
        for symbol in result:
            values = self._symbols_values[symbol.get_type()]
            values[symbol.get_name()] = symbol._get_value()

        # Invalidate previous stored state for now ( to be developed later )
        self._state = None
        return result[0] if len(result) == 1 else result




    def new_coordinate(self, *args, **kwargs):
        '''new_coordinate(name: str[, vel_name: str[, acc_name: str[, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]], [value: numeric[, vel_value: numeric[, acc_value: numeric]]])) -> Tuple[SymbolNumeric, SymbolNumeric, SymbolNumeric]
        Creates a new coordinate symbol and its derivative components (velocity and acceleration)

            :Example:

            >>> a, da, dda = new_coordinate('a', 1, 2, 3)

            >>> a.value, a.type
            1, 'coordinate'

            >>> da.value, da.type
            2, 'velocity'

            >>> dda.value, dda.type
            3, 'acceleration'

            >>> a.name, da.name, dda.name
            'a', 'da', 'dda'


        .. note::

            You can specify the initial values of the coordinate and its derivatives
            right after the first argument (name) or any other string parameter (if all arguments are positional):

            :Example:

            >>> new_coordinate('a', 1, 2, 3)
            >>> new_coordinate('a', 'a2', 'a3', 1, 2)


        :param str name: Name of the coordinate
        :param str vel_name: Name of the first derivative
            (By default its the name of the coordinate prefixed with 'd')
        :param str acc_name: Name of the second derivative
            (By default its the name of the coordinate prefixed with 'dd')

        :param str tex_name: Name in latex of the coordinate
            By default (if not specified) is autogenerated based on the given name if ``autogen_latex_names``
            is enabled. Otherwise, its set to an empty string.

            .. seealso:: :func:`autogen_latex_names`


        :param str vel_tex_name: Name in latex of the first derivative
            By default its ``\\dot{tex_name}`` if tex_name is not an empty string.
            Otherwise, its also set to an empty string
        :param str acc_tex_name: Name in latex of the second derivative
            By default its ``\\ddot{tex_name}`` if tex_name is not an empty string.
            Otherwise, its also set to an empty string

        :param numeric value: The initial numeric value of the coordinate. By default 0
        :param numeric vel_value: The intial numeric value of the first derivative. By default 0
        :param numeric acc_value: The initial numeric value of the first derivative. By default 0

        :returns: The new coordinate and its derivatives created on success
        :rtype: Tuple[SymbolNumeric, SymbolNumeric, SymbolNumeric]

        :raises TypeError: If any input argument has an invalid type
        :raises ValueError: If any input argument has an invalid value

        :raises IndexError: If a cordinate was already created with the same name, but the
            names of its derivatives doesnt match with the ones indicated as arguments.
            It can also be raised if an object which is not a numeric symbol
            with the given name was created already

        .. warning::

            If a coordinate was already created with the same name (also for the
            derivatives), this method dont create a new one, only updates the latex names & the values
            specified in the arguments (but it raises a user warning)

        '''
        return self.new_symbol(b'coordinate', *args, **kwargs)



    def new_aux_coordinate(self, *args, **kwargs):
        '''new_aux_coordinate(name: str[, vel_name: str[, acc_name: str[, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]], [value: numeric[, vel_value: numeric[, acc_value: numeric]]])) -> SymbolNumeric
        Creates a new "auxiliar" coordinate symbol and its derivative components (velocity and acceleration)

            :Example:

            >>> a, da, dda = new_aux_coordinate('a', 1, 2, 3)

            >>> a.value, a.type
            1, 'aux_coordinate'

            >>> da.value, da.type
            2, 'aux_velocity'

            >>> dda.value, dda.type
            3, 'aux_acceleration'

            >>> a.name, da.name, dda.name
            'a', 'da', 'dda'



        The behaviour and signature is the same as for new_coordinate method.

        .. seealso:: :func:`new_coordinate()`
        '''
        return self.new_symbol(b'aux_coordinate', *args, **kwargs)


    def new_parameter(self, *args, **kwargs):
        return self.new_symbol(b'parameter', *args, **kwargs)

    def new_joint_unknown(self, *args, **kwargs):
        return self.new_symbol(b'joint_unknown', *args, **kwargs)

    def new_input(self, *args, **kwargs):
        return self.new_symbol(b'input', *args, **kwargs)



    def new_base(self, name, *args, **kwargs):
        '''new_base(name: str[, previous: Base][rotation_tupla][, rotation_angle: Expr]) -> Base
        Creates a new base in this system with the given name, rotation tupla & angle

        Any of the next calls creates a base named 'a' with xyz as parent base and
        with a rotation tupla with values [0, 1, 2]:

            :Example:

            >>> new_base('a', 'xyz', 0, 1, 2)
            >>> new_base('a', None, 0, 1, 2)
            >>> new_base('a', 0, 1, 2)
            >>> new_base('a', [0, 1, 2])
            >>> new_base('a', rotation_tupla=[0, 1, 2])
            m = Matrix([0, 1, 2])
            >>> new_base('a', rotation_tupla=m)

        The same but rotation angle is set to pi:

            :Example:

            >>> new_base('a', 'xyz', 0, 1, 2, pi)
            >>> new_base('a', 0, 1, 2, pi)
            >>> new_base('a', [0, 1, 2], pi)
            >>> new_base('a', rotation_tupla=[0, 1, 2], rotation_angle=pi)



        :param str name: Must be the name of the new base
        :param previous: Is the previous base of the new base.
            By default is the "xyz" base
        :type previous: str, Base
        :param rotation_angle: Must be the rotation angle
        :param rotation_tupla: A list of three components that represents the base rotation tupla.
            It can also be a Matrix 1x3 or 3x1

            .. note::
                The rotation tupla can be specified also three different positional arguments
                (all of them expressions or numbers)

        :type rotation_angle: Expr
        :type rotation_tupla: Tuple[Expr, Expr, Expr], Matrix

        :returns: The new base created on success
        :rtype: Base
        :raises TypeError: If any argument supplied has an invalid type
        :raises ValueError: If any argument supplied has an incorrect value (e.g: previous base doesnt exist)
        :raises IndexError: If there is already a base with the name specified
        '''
        return self._new_base(name, args, kwargs)



    def new_matrix(self, name, *args, **kwargs):
        '''new_matrix(name[, shape][, values]) -> Matrix
        Creates a new matrix with the given name, shape and values in the system

            :Example:

            >>> new_matrix('a')
            [ 0 ]

            >>> new_matrix('a', shape=[2, 2])
            ╭      ╮
            │ 0  0 │
            │ 0  0 │
            ╰      ╯

            >>> new_matrix('a', [0, 1, 2, 3, 4])
            [ 0 1 2 3 4 ]

            >>> new_matrix('a', [[0, 1], [2, 3]])
            ╭      ╮
            │ 0  1 │
            │ 2  3 │
            ╰      ╯

            >>> new_matrix('a', values=range(0, 9), shape=[3, 3])
            ╭         ╮
            │ 0  1  2 │
            │ 3  4  5 │
            │ 6  7  8 │
            ╰         ╯

        It is also possible to create matrix from a numpy array with one or two
        dimensions (numpy must be installed):

            :Example:

            >>> import numpy as np
            >>> new_matrix('a', np.eye(3))
            ╭         ╮
            │ 1  0  0 │
            │ 0  1  0 │
            │ 0  0  1 │
            ╰         ╯

            >>> new_matrix('a', values=np.linspace(0, 1, 9), shape=[3,3])
            ╭                     ╮
            │     0  0.125   0.25 │
            │ 0.375    0.5  0.625 │
            │  0.75  0.875      1 │
            ╰                     ╯

        :param str name: Name of the new matrix

        :param shape: Must be the shape of the new array (number of rows and columns)
            If shape is not specified, the length of both dimensions of the new array
            are determined by the argument "values"
        :type shape: Tuple[int, int]

        :param values: Must be the initial values of the matrix:

            * If specified, it can be a list or a list of sublists of expressions (or anything convertible to
                expressions like numbers). It can also be a numpy array.

            * If its a list and shape argument was not specified, the resulting matrix
                will have one row with the values indicated in it (the list cant be empty).

            * If its a list of sublists of expressions, each sublist will represent a row
                in the matrix (the number of sublists must be greater than zero and the length
                of sublists must be greater than zero and all equal).

            * If both shape and values was specified, the resulting matrix will have the given
                shape and values (the number of values must match the number of rows and columns
                indicated).

        :type values: List[Expr], ndarray

        :rtype: Matrix

        :raises TypeError: If any of the input arguments has an invalid type.
        :raises ValueError: If any of the input arguments has an inorrect or inconsistent value.
        :raises IndexError: If an object with the specified name already exists within the system and its
            not a Matrix object

        .. warning:: If a matrix with the given name was already created, this method only
            updates the shape & values of the existing matrix (also throws a user warning).

        '''
        return self._new_matrix(name, args, kwargs)



    def new_vector(self, name, *args, **kwargs):
        '''new_vector(name: str[, values][, base: Base]) -> Vector3D
        Creates a new 3D vector in this system with the given name, values and geometric base.

            :Example:

            >>> new_vector('v')
            [ 0 0 0 ]

            >>> new_vector('v', 1, 2, 3)
            [ 1 2 3 ]

            >>> new_vector('v', [4, 5, 6])
            [ 4 5 6 ]

            >>> new_vector('v', values=[7, 8, 9])
            [ 7 8 9 ]


        The geometric base of the vector will be xyz on the examples above.
        You can indicate a different base:

            :Example:

            >>> foo = new_base('foo', 'xyz')
            >>> new_vector('v', [1, 2, 3], foo)
            >>> new_vector('v', foo)
            >>> new_vector('v', 'foo')
            >>> new_vector('v', base='foo', values=[1, 2, 3])


        :param str name: Name of the new vector

        :param values: A list of three expressions indicating the initial values
            of the elements in the vector. These values can be also specified as
            three different positional arguments (they must precede the base argument)

        :param base: The geometric base for the new the vector
        :type base: str or Base

        :rtype: Vector3D

        :raises TypeError: If any of the input arguments has an invalid type.
        :raises ValueError: If any of the input arguments has an inorrect or inconsistent value.
        :raises IndexError: If an object with the specified name already exists within the system and its
            not a Vector object

        .. warning:: If a vector with the given name already exists in the system, this method
            only updates its values and geometric base using the arguments specified (also raises
            a user warning)

        '''
        return self._new_vector(name, args, kwargs)



    def new_tensor(self, name, *args, **kwargs):
        '''new_tensor(name: str[, values][, base: Base]) -> Tensor3D
        Creates a new tensor with the given name, values and geometric base.

            :Example:

            >>> new_tensor('q')
            ╭         ╮
            │ 0  0  0 │
            │ 0  0  0 │
            │ 0  0  0 │
            ╰         ╯
            >>> new_tensor('q', range(0, 9), 'xyz')
            ╭         ╮
            │ 0  1  2 │
            │ 3  4  5 │
            │ 6  7  8 │
            ╰         ╯
            >>> new_tensor('q', 1, 2, 3, 1, 2, 3, 1, 2, 3, 'xyz')
            ╭         ╮
            │ 1  2  3 │
            │ 1  2  3 │
            │ 1  2  3 │
            ╰         ╯

        You can use a numpy array to indicate the initial values:

            :Example:

            >>> import numpy as np
            >>> new_tensor('q', np.eye(3), base='xyz')
            ╭         ╮
            │ 1  0  0 │
            │ 0  1  0 │
            │ 0  0  1 │
            ╰         ╯
            >>> new_tensor('q', values=np.linspace(0, 1, 9), base=get_base('xyz'))
            ╭                     ╮
            │     0  0.125   0.25 │
            │ 0.375    0.5  0.625 │
            │  0.75  0.875      1 │
            ╰                     ╯


        :param str name: The name of the new tensor
        :param values: Initial values of the tensor. It can be a list of expressions,
            matrix or numpy array. It can also be specified as nine different positional arguments
            (all of them expressions)
        :param base: The base of the argument (by default is the xyz base)
        :type base: str, Base

        :rtype: Tensor3D

        :raises TypeError: If any of the input arguments has an invalid type.
        :raises ValueError: If any of the input arguments has an inconsistent value.
        :raises IndexError: If an object in the system already exists with the given name
            and its not a tensor.

        .. warning:: If an object already exists with the given name and its a tensor,
            this method only updates its values & base (also raises a warning message).
            Then the existing tensor is returned.

        '''
        return self._new_tensor(name, args, kwargs)



    def new_point(self, name, *args, **kwargs):
        '''new_point(name: str, previous: Point, position: Vector3D) -> Point
        Creates a new point in the system with the given name, position vector and previous point

        Any of the next calls to new_point will create a point with the "O" point
        as the previous one and a vector 'v' as its position:

            :Example:

            >>> v = new_vector('v', 1, 2, 3)

            >>> new_point('p', v)
            >>> new_point('p', 'v')
            >>> p = new_point('p', position=v)
            >>> p.position
            [ 1 2 3 ]
            >>> p.previous.name
            'O'


        You can specify a different previous point:

            :Example:

            >>> v, w = new_vector('v', 1, 2, 3), new_vector('w', 4, 5, 6)
            >>> q = new_point('q', v)
            >>> new_point('p', q, w)

        The next calls are equivalent to the last one above:

            :Example:

            >>> new_point('p', 'q', 'w')
            >>> new_point('p', previous=q, position=w)
            >>> new_point('p', previous='q', position='w')



        :param previous: Previous point. By default is the 'O' point
        :type previous: str or Point

        :param position: Position vector for the new point.
        :type position: str or Vector3D

        :rtype: Point


        :raises TypeError: If any of the input arguments has an invalid type.
        :raises ValueError: If any of the input arguments has an inorrect or inconsistent value.
        :raises IndexError: If an object with the specified name already exists within the system and its
            not a Point object

        .. warning:: If a point with the given name already exists in the system, this method
            only updates its position vector and changes the previous point (also raises
            a user warning)
        '''
        return self._new_point(name, args, kwargs)



    def new_frame(self, name, point, base=None):
        '''new_frame(name: str, point: Point[, base: Base]) -> Frame
        Creates a new frame on the system with the given name, point and base.

        The next calls will create a frame called 'f' with 'O' as point and xyz as its base:

            :Example:

            >>> new_frame('f', get_point('O')
            >>> new_frame('f', 'O')
            >>> new_frame('f', 'O', 'xyz')
            >>> new_frame('f', base='xyz', point='O')

        You can indicate a different point & base:

            :Example

            >>> b = new_base('b', previous='xyz')

            >>> v = new_vector('v', 1, 2, 3)
            >>> p = new_point('p', position=v, previous='O')

            >>> new_frame('f', p, b)
            >>> new_frame('f', 'p', 'b')
            >>> new_frame('f', base='b', point='p')


        :param str name: The name of the new frame

        :param point: The point of the new frame.
        :type point: str, Point

        :param base: The base of the new frame
        :type base: str, Base

        :rtype: Frame


        :raise TypeError: If the given input arguments have an invalid type.
        :raise IndexError: If an object with the given name already exists and
            its not a frame.

        .. warning:: If an frame object already exists with the given name, this
            method only updates its values & properties using the arguments
            provided (point and base) on the existing frame. Then, its returned
            (also raises a user warning)
        '''
        return self._new_frame(name, point, base)



    def new_solid(self, name, point, base, mass, CM, IT):
        '''new_solid(name: str, point: Point, base: Base, mass: SymbolNumeric, CM: Vector3D, IT: Tensor3D)
        Creates a new solid object

            :Example:

            >>> new_base('Barm', 0, 1, 0)
            >>> new_param('m', 1)
            >>> new_vector('Oarm_Garm', 0, 0, 1, 'Barm')
            >>> new_tensor('Iarm', base='Barm')
            >>> arm = new_solid('arm', 'O', 'Barm', 'm', 'Oarm_Garm', 'Iarm')
            >>> arm.get_G().name
            'Garm'
            >>> s.get_mass()
            m = 1.0


        :param str name: Name of the new solid

        :param point:
        :type point: str, Point

        :param base: The geometric base of the solid
        :type base: str, Base

        :param mass: The mass of the solid (must be a parameter symbol)
        :type mass: str, SymbolNumeric

        :param CM: Center of mass point of the solid
        :type CM: str, Vector3D

        :param IT: Intertia tensor of the solid
        :type IT: str, Tensor3D

        :rtype: Solid

        :raise TypeError: If any of the input arguments has an invalid type.
            Also raised if the mass symbol is not a parameter
        :raise IndexError: If there exists another object with the given name already
        '''
        return self._new_solid(name, point, base, mass, CM, IT)




    def new_wrench(self, name, force, moment, point, solid, type):
        '''new_wrench(name: str, force: Vector3D, moment: Vector3D, point: Point, solid: Solid, type: str) -> Wrench3D
        Create a new wrench with the given name, force and moment vectors, point, solid object
        and with the given type.

            :Example:

            >>> new_base('Barm', 0, 1, 0)
            >>> new_param('m', 1)
            >>> new_vector('Oarm_Garm', 0, 0, 1, 'Barm')
            >>> new_tensor('Iarm', base='Barm')
            >>> new_solid('arm', 'O', 'Barm', 'm', 'Oarm_Garm', 'Iarm')

            >>> force = new_vector('f', 0, 1, 0, 'xyz')
            >>> moment = new_vector('mt', 0, 0, 0, 'xyz')
            >>> point = new_point('p', position=new_vector('v', 0, 1, 2, 'xyz'))

            >>> w = new_wrench('w', force, moment, point, 'arm', 'Constraint')
            >>> w.get_force().name
            'f'


        :param str name: Name of the wrench

        :param force: The Force vector
        :type force: str, Vector3D

        :param moment: The moment vector
        :type moment: str, Vector3D

        :param point: The point of the wrench
        :type point: str, Point

        :param solid: The solid of the wrench
        :type solid: str, Solid

        :param str type: The kind of wrench

        :rtype: Wrench3D

        :raises TypeError: If any of the given input arguments has an invalid type.
        :raise IndexError: If there exists another object with the given name already
        '''
        return self._new_wrench(name, force, moment, point, solid, type)



    new_coord = new_coordinate
    new_aux_coord = new_aux_coordinate,
    new_param = new_parameter
    new_unknown = new_joint_unknown




    ######## Kinematic operations ########


    def reduced_base(self, a, b):
        '''reduced_base(a: Base, b: Base) -> Base
        Find the common base in the tree of the given bases.

            :Example:

            >>> a = new_base('a', 'xyz')
            >>> b = new_base('b', 'xyz')
            >>> reduced_base(a, b).name
            'xyz'


        :type a: str, Base
        :type b: str, Base

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Base

        '''
        return self._reduced_base(a, b)



    def reduced_point(self, a, b):
        '''reduced_point(a: Point, b: Point) -> Point
        Get the point obtained by reducing the given ones as argument.

            :Example:

            >>> b = new_base('b', 'xyz')
            >>> b
            Base b, ancestors: xyz
            >>> v, w = new_vector('v', base='xyz'), new_vector('w', base=b)
            >>> p, q = new_point('p', v), new_point('q', w)
            >>> reduced_point(p, q).name
            'O'

        :type a: str, Point
        :type b: str, Point

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Point

        '''
        return self._reduced_point(a, b)



    def pre_point_branch(self, a, b):
        '''pre_point_branch(a: Point, b: Point) -> Point
        Get the previous point in the branch from a to b (gravity down)

        :type a: str, Point
        :type b: str, Point

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Point

        '''
        return self._pre_point_branch(a, b)


    previous_point_branch = pre_point_branch



    def rotation_matrix(self, a, b):
        '''rotation_matrix(a: Base, b: Base) -> Matrix
        Calculate the rotation matrix for the given bases

            :Example:

            >>> a = new_base('a', 'xyz')
            >>> rotation_matrix(a, 'xyz')
            ╭         ╮
            │ 1  0  0 │
            │ 0  1  0 │
            │ 0  0  1 │
            ╰         ╯

        :type a: str, Base
        :type b: str, Base

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Matrix

        '''
        return self._rotation_matrix(a, b)



    def position_vector(self, a, b):
        '''position_vector(a: Point, b: Point) -> Vector3D
        Get the position vector between the given points (a to b)

            :Example:

            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> v = new_vector('v', a, b, c, 'xyz')
            >>> w = new_vector('w', 1, 2, 3, 'xyz')
            >>> p, q = new_point('p', v), new_point('q', w)
            >>> position_vector(p, q)
            [ 1-a  2-b  3-c ]

        :type a: str, Point
        :type b: str, Point

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._position_vector(a, b)



    def angular_velocity(self, a, b):
        '''angular_velocity(a: Base, b: Base) -> Vector3D
        Get the angular velocity between two bases (from a to b)

        :type a: str, Base
        :type b: str, Base

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._angular_velocity(a, b)



    def angular_velocity_tensor(self, a, b):
        '''angular_velocity_tensor(a: Base, b: Base) -> Tensor3D
        Get the angular velocity tensor between two bases (from a to b)

        :type a: str, Base
        :type b: str, Base

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Tensor3D

        '''
        return self._angular_velocity_tensor(a, b)



    def velocity_vector(self, frame, point, solid=None):
        '''velocity_vector(frame: Frame, point: Point[, solid: Solid]) -> Vector3D
        Get the velocity vector of the point with respect the given frame.
        If solid is specified, the resulting velocity is computed with respect
        the frame in such solid.

        :type frame: str, Frame
        :type point: str, Point
        :type solid: None, str, Solid

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._velocity_vector(frame, point, solid)



    def angular_acceleration(self, a, b):
        '''angular_acceleration(a: Base, b: Base) -> Vector3D
        Get the angular acceleration between two bases (from a to b)

        :type a: str, Base
        :type b: str, Base

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._angular_acceleration(a, b)



    def acceleration_vector(self, frame, point, solid=None):
        '''acceleration_vector(frame: Frame, point: Point[, solid: Solid]) -> Vector3D
        Get the acceleration vector of the point with respect the given frame.
        If solid is specified, the resulting acceleration is computed with respect
        the frame in such solid.

        :type frame: str, Frame
        :type point: str, Point
        :type solid: None, str, Solid

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._acceleration_vector(frame, point, solid)




    def twist(self, solid):
        '''twist(solid: Solid) -> Wrench3D

        :type solid: str, Solid

        :raises TypeError: If the input arguments dont have a valid type

        :rtype: Vector3D

        '''
        return self._twist(solid)




    def derivative(self, *args, **kwargs):
        '''derivative(x: Expr | Matrix | Vector[, base: Base][, frame: Frame]) -> Expr | Matrix | Vector3D
        Compute the time derivative of the given expression:

            :Example:

            >>> a = new_param('a')
            >>> t = get_time()
            >>> derivative(a * t ** 2 + 20)
            2*t*a


        You can also compute the time derivatives of the components of a matrix
        or vector:

            >>> v = new_vector('v', 1, a / t, a / t ** 2 )
            >>> derivative(v)
            [ 0  -t**(-2)*a  -2*t**(-3)*a ]

        :param base: Additional argument which is only valid if the first argument
            is a vector:
            * If specified, it must be a base.
            * The time derivatives will be computed with respect such base.
            * The argument frame cannot be set if this one is indicated.

        :param frame: Additional argument which is only valid if the first argument
            is a vector:
            * If specified, it must be a frame.
            * The time derivatives will be computed with respect such frame.
            * The argument base cannot be set if this one is indicated.
        :type frame: str, Frame

        '''
        return self._derivative(args, kwargs)


    dt = derivative




    def jacobian(self, *args, **kwargs):
        '''jacobian(x: Matrix, y: Matrix | SymbolNumeric, symmetric: Expr) -> Matrix
        Compute the jacobian matrix between two matrices or a matrix and a symbol

        The next example shows how to calculate the jacobian of a row matrix with respect
        a symbol:

            :Example:

            >>> a, b = new_param('a'), new_param('b')
            >>> m = new_matrix('m', [a, b, a ** 2, b ** 2])
            >>> m
            [ a  b  a**2  b**2 ]
            >>> jacobian(m, a)
            [ 1  0  2*a  0 ]
            >>> jacobian(m, a).shape
            (4, 1)
            >>> jacobian(m, b)
            [ 0  1  0  2*b ]
            >>> jacobian(m, b).shape
            (4, 1)


        You can also compute the jacobian between a row matrix and a column matrix

            :Example:

            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> m = Matrix([a ** 2 + b, b ** 2 + c, c ** 2 + a, a + b + c])
            >>> q = Matrix([a, b, c]).transpose()
            >>> jacobian(m, q)
            ╭               ╮
            │ 2*a    1    0 │
            │   0  2*b    1 │
            │   1    0  2*c │
            │   1    1    1 │
            ╰               ╯
            >>> jacobian(m, q).shape
            (4, 3)

        :param Matrix x: Must be a row matrix
        :param Matrix y: Must be a column matrix
        :param Expr symmetric: It must be a symbolic expression indicating if the
            jacobian matrix computation should be symmetric or not. 0 for non symmetric.
            Otherwise it will be symmetric ( when evaluating the expression numerically )
            By default it is set to 0

        '''
        return self._jacobian(args, kwargs)




    def diff(self, x, symbol):
        '''diff(x: Expr | Matrix | Wrench3D, symbol: SymbolNumeric) -> Expr | Matrix | Wrench3D
        Computes the derivative of the given expression, matrix, vector, tensor or wrench
        with respect a symbol.

            :Example:

            >>> a = new_param('a')
            >>> diff(2 * a ** 2, a)
            4*a
            >>> b = new_param('b')
            >>> diff(b / a, a)
            -a**(-2)*b
            >>> m = new_matrix('m', [a, b / a, b / a ** 2, b / a ** 3], shape=[2, 2])
            >>> m
            ╭                      ╮
            │         a  a**(-1)*b │
            │ a**(-2)*b  a**(-3)*b │
            ╰                      ╯
            >>> diff(m, a)
            ╭                            ╮
            │            1    -a**(-2)*b │
            │ -2*a**(-3)*b  -3*a**(-4)*b │
            ╰                            ╯

        :param x: Must be the expression, matrix or wrench to derivate
        :type x: Expr, Matrix, Wrench3D

        :param symbol: Must be the symbol about which the expression, matrix or wrench
            is derivated
        :type symbol: SymbolNumeric, str


        :rtype: Expr, Matrix, Wrench3D


        '''
        return self._diff(x, symbol)




    def to_symbol(self, x):
        '''to_symbol(x: Expr | SymbolNumeric) -> SymbolNumeric
        This method turns the given symbolic expression into a symbol instance
        ( is the python version of GiNaC::ex_to C++ function ).
        The given expression must be composed of one single symbol ( defined within this system )

        :rtype: SymbolNumeric
        :raises ValueError: If the conversion couldnt be performed

        '''
        if not isinstance(x, (SymbolNumeric, Expr)):
            raise TypeError('Input argument must be a numeric symbol or expresion')
        if isinstance(x, SymbolNumeric):
            return x
        return x.to_symbol(self)





    ######## Solid operations ########


    def gravity_wrench(self, solid):
        '''gravity_wrench(solid: Solid) -> Wrench3D
        Get the gravity wrench of a solid

        :rtype: Wrench3D

        '''
        return self._gravity_wrench(solid)



    def inertia_wrench(self, solid):
        '''inertia_wrench(solid: Solid) -> Wrench3D
        Get the inertia wrench of a solid

        :rtype: Wrench3D

        '''
        return self._inertia_wrench(solid)








    ######## Numeric evaluation ########

    @lru_cache(maxsize=256)
    def _compile_numeric_function_cached(self, matrix, c_optimized=False):
        return self._compile_numeric_function(matrix.wrapped, c_optimized)


    def compile_numeric_function(self, matrix, c_optimized=False):
        '''
        Get a function that can be used to evaluate the given matrix numerically.

        :param c_optimized: If set to True, compile the underline numeric function
            as a cython extension. The numeric function evaluation will be faster but
            this method will be slower (a few seconds to generate and compile the cython extension)
            Otherwise, if its False (by default), the underline function is compiled as a
            regular python function.

        .. seealso:: :func:`evaluate`

        '''
        return self._compile_numeric_function_cached(HashObjectWrapper(matrix), c_optimized)



    def compile_numeric_function_c_optimized(self, matrix):
        '''
        This is an alias of ``compile_numeric_function(matrix, c_optimized=True)``

        .. seealso:: :func:`compile_numeric_function`

        '''
        return self.compile_numeric_function(matrix, c_optimized=True)


    compile_numeric_func = compile_numeric_function
    compile_numeric_func_c_optimized  = compile_numeric_function_c_optimized



    def evaluate(self, x):
        '''evaluate(func: NumericFunction | Matrix) -> np.ndarray
        Evaluate the given numeric function, symbolic matrix or expression

            :Example:

            >>> disable_atomization()
            >>> a, b, c = new_param('a', 1), new_input('b', 2), new_joint_unknown('c', 3)
            >>> v = new_vector('v', a, b, c)
            >>> m = v.skew * v.module
            >>> m
            ╭                                                                                    ╮
            │                          0  -c*(b**2+a**2+c**2)**(1/2)   b*(b**2+a**2+c**2)**(1/2) │
            │  c*(b**2+a**2+c**2)**(1/2)                           0  -(b**2+a**2+c**2)**(1/2)*a │
            │ -b*(b**2+a**2+c**2)**(1/2)   (b**2+a**2+c**2)**(1/2)*a                           0 │
            ╰                                                                                    ╯
            >>> evaluate(m)
            array([[  0.        , -11.22497216,   7.48331477],
                   [ 11.22497216,   0.        ,  -3.74165739],
                   [ -7.48331477,   3.74165739,   0.        ]])
            >>> evaluate(a ** 2 + b ** 2)
            5
        '''
        if not isinstance(x, (NumericFunction, Matrix, Expr, SymbolNumeric)):
            raise TypeError('Input argument must be a numeric function, matrix, symbol or expression')
        if isinstance(x, SymbolNumeric):
            return x.get_value()
        if isinstance(x, Expr):
            return next(iter(self.evaluate(Matrix([x])).flat)).item()
        if isinstance(x, Matrix):
            x = self.compile_numeric_func(x)
        return x.evaluate()



    ######## Export ########


    def export_numeric_function_MATLAB(self, matrix, func_name, func_out_name=None):
        '''export_numeric_function_MATLAB(matrix: Matrix, func_name: str[, func_out_name: str])

        Build a MATLAB script which defines a function that evaluates the given symbolic
        matrix numerically.
        '''
        self._export_function_MATLAB(matrix, func_name, func_out_name)


    def export_numeric_init_function_MATLAB(self):
        '''export_numeric_init_function_MATLAB()

        Build a MATLAB script which defines a function that initializes the numeric values of the
        symbols of the system.
        '''
        self._export_numeric_init_function_MATLAB()



    export_numeric_func_MATLAB = export_numeric_function_MATLAB
    export_numeric_init_func_MATLAB = export_numeric_init_function_MATLAB




    ######## Restoring/Saving state ########


    def save_state(self):
        self._state = dict([(key, value.as_array().copy()) for key, value in self._symbols_values.items()])


    def restore_previous_state(self):
        if self._state is None:
            return
            #raise RuntimeError('You must call first to save_state')
        for key, arr in self._state.items():
            np.copyto(self._symbols_values[key].as_array(), arr)






    ######## Properties ########


    @property
    def symbols(self):
        '''
        Only read property that returns all the symbols defined within this system.

        :rtype: Mapping[str, SymbolNumeric]

        .. note::
            It calls internally the method ``get_symbols``

            .. seealso:: :func:`get_symbols`
        '''
        return self.get_symbols()


    @property
    def time(self):
        '''
        Only read property that returns the time symbol

        :rtype: SymbolNumeric

        .. note::
            It calls internally the method ``get_time``

            .. seealso:: :func:`get_time`
        '''
        return self.get_time()

    @property
    def coordinates(self):
        return self.get_coordinates()

    @property
    def velocities(self):
        return self.get_velocities()

    @property
    def accelerations(self):
        return self.get_accelerations()

    @property
    def aux_coordinates(self):
        return self.get_aux_coordinates()

    @property
    def aux_velocities(self):
        return self.get_aux_velocities()

    @property
    def aux_accelerations(self):
        return self.get_aux_accelerations()

    @property
    def parameters(self):
        return self.get_parameters()

    @property
    def joint_unknowns(self):
        return self.get_joint_unknowns()

    @property
    def inputs(self):
        return self.get_inputs()

    @property
    def bases(self):
        return self.get_bases()

    @property
    def matrices(self):
        return self.get_matrices()

    @property
    def vectors(self):
        return self.get_vectors()

    @property
    def tensors(self):
        return self.get_tensors()

    @property
    def points(self):
        return self.get_points()

    @property
    def frames(self):
        return self.get_frames()

    @property
    def solids(self):
        return self.get_solids()

    @property
    def wrenches(self):
        return self.get_wrenches()


    coords = coordinates
    aux_coords = aux_coordinates
    params = parameters
    unknowns = joint_unknowns



    @property
    def O(self):
        '''
        Only read property that returns the origin point.

        :rtype: Point

        .. note::
            Its equivalent to ``get_point('O')``
            .. seealso:: :func:`get_point`

        '''
        return self.get_point('O')


    @property
    def xyz(self):
        '''
        Only read property that returns the xyz base.

        :rtype: Base

        .. note::
            Its equivalent to ``get_base('xyz')``
            .. seealso:: :func:`get_base`

        '''
        return self.get_base('xyz')



    @property
    def abs(self):
        '''
        Only read property that returns the abs base.

        :rtype: Frame

        .. note::
            Its equivalent to ``get_frame('abs')``
            .. seealso:: :func:`get_frame`

        '''
        return self.get_frame('abs')




    @property
    def autogen_latex_names(self):
        '''
        This property can be used to turn on/off numeric symbols latex name
        autogeneration (by default is turned on)

            :Example:

            >>> sys = System()
            >>> sys.autogen_latex_names = True

            >>> a = sys.new_param('a')
            >>> a.tex_name
            '\\alpha'

            >>> sys.autogen_latex_names = False
            >>> b = sys.new_param('b')
            >>> b.tex_name
            ''
        '''
        return self._is_autogen_latex_names_enabled()

    @autogen_latex_names.setter
    def autogen_latex_names(self, enabled):
        self._set_autogen_latex_names(enabled)



    @property
    def scene(self):
        '''
        Read only property that returns the 3d scene manager associated to this system

        :rtype: Scene

        .. seealso:: :func:`get_scene`

        '''
        return self.get_scene()






    ######## Mixin methods ########

    def set_as_default(self):
        '''
        Set this instance as the default system.
        '''
        from . import set_default_system
        set_default_system(self)




    ######## Metamethods ########
    # TODO





class HashObjectWrapper:
    '''
    This is a class that can be used to wrap an unhasable object in order to be passed to
    a function which is decorated with lru_cache. The id of the object is used as
    the hash.
    '''
    def __init__(self, obj):
        self.wrapped = obj

    def __eq__(self, other):
        if not isinstance(other, HashObjectWrapper):
            return False
        return self.wrapped == other.wrapped

    def __hash__(self):
        return hash((HashObjectWrapper, id(self.wrapped)))






######## class SymbolsValuesMapping ########

class SymbolsValuesMapping(MutableMapping):
    '''
    An instance of this class is used to represent and store pairs of symbols names and their associated numeric values

        :Example:

        >>> m = SymbolValuesVector()
        >>> m['a'] = 1.0
        >>> m['a']
        1.0
        >>> m['b'] = 2
        2.0
        >>> m['c'] = 3
        3.0
        >>> list(m.keys())
        ['a', 'b', 'c']
        >>> list(m.values())
        [1.0, 2.0, 3.0]
        >>> m.as_array()
        array([[1.],
               [2.],
               [3.]])
        >>> del m['b']
        >>> m.as_array()
        array([[1.],
               [3.]])

    '''


    ######## Constructor ########

    def __init__(self):
        self._names  = []
        self._values = np.array(np.zeros(shape=(0,1), dtype=np.float64), copy=False, order='C', subok=True)


    ######## Getters ########


    def as_array(self):
        return self._values

    def index(self, name):
        return self._names.index(name)




    ######## Metamethods ########


    def __getitem__(self, name):
        try:
            return self._values[self._names.index(name)].item()
        except ValueError:
            raise KeyError

    def __setitem__(self, name, value):
        if name in self._names:
            self._values[self._names.index(name)] = value
        else:
            index = len(self._names)
            self._names.append(name)
            self._values = np.insert(self._values, index, value, axis=0)


    def __delitem__(self, name):
        if name not in self._names:
            raise KeyError
        index = self._names.index(name)
        self._names.remove(name)
        self._values = np.delete(self._values, index, axis=0)

    def __iter__(self):
        return iter(self._names)

    def __len__(self):
        return len(self._names)

    def __repr__(self):
        data = list(zip(self._names, self._values.flat))
        return tabulate(data, tablefmt='plain')






# This variable will store the "default" system object.
_default_system = None


def get_default_system():
    '''get_default_system() -> System
    Get the default system instance.

    :rtype: System
    '''
    global _default_system
    if _default_system is None:
        _default_system = System()
    return _default_system


def set_default_system(system):
    '''set_default_system(system: System)
    Set the default system instance

    :param System system: The system instance to be set as default
    :raises TypeError: If the input argument is not an instance of the class System
    '''
    global _default_system
    if not isinstance(system, System):
        raise TypeError('Input argument must be an instance of the class System')
    _default_system = system












######## Docstrings autogeneration for System class ########



# Template docstring for get_param, get_input, get_joint_unknown, ...
_symbol_getter_docstring_template = '''get_{kind}(name: str) -> SymbolNumeric
Get a {name} by name defined within this system.

:param str name: Name of the {name} to fetch
:rtype: SymbolNumeric

:raises TypeError: If the input argument has an invalid type.
:raises IndexError: If no {name} with the given name exists.

.. note:: This is equivalent to ``get_symbol(name, '{kind}')``
.. seealso:: :func:`get_symbol`
'''

# Template docstring for has_param, has_input, has_joint_unknown, ...
_symbol_checker_docstring_template = '''has_{kind}(name: str) -> bool
Check if a {name} with the given name is defined within the system

:param str name: Name of the {name} to check
:rtype: bool

:raises TypeError: If the input argument has an invalid type.

.. note:: This is equivalent to ``has_symbol(name, '{kind}')``

.. seealso::  :func:`has_symbol`
'''


# Template docstring for get_matrix, get_tensor, get_vector, ...
_geom_object_getter_docstring_template = '''get_{kind}(name: str) -> {class}
Get a {name} by name defined within this system.

:param str name: Name of the {name} to fetch
:rtype: {class}

:raises TypeError: If the input argument has an invalid type.
:raises IndexError: If no {name} with the given name exists.
'''

# Template docstring for has_matrix, has_tensor, has_vector, ...
_geom_object_checker_docstring_template = '''has_{kind}(name: str) -> bool
Check if a {name} with the given name is defined within the system.

:param str name: Name of the {name} to check
:rtype: bool

:raises TypeError: If the input argument has an invalid type.
'''


# Template docstring for get_params, get_inputs, get_joint_unknowns, ...
_symbol_pgetter_docstring_template = '''get_{pkind}() -> Mapping[str, SymbolNumeric]
Get all the {pname} defined within this system.

:rtype: Mapping[str, SymbolNumeric]

.. note::
    This is equivalent to ``get_symbols('{kind}')``

    .. seealso:: :func:`get_symbols`

'''

# Template docstring for get_vectors, get_tensors, get_matrices, ...
_geom_object_pgetter_docstring_template = '''get_{pkind}() -> Mapping[str, {class}]
Get all the {pname} defined within this system.

:rtype: Mapping[str, {class}]

'''

# Template docstring for get_inputs_matrix, get_parameters_matrix, ...
_symbol_matrix_getter_docstring_template = '''get_{pkind}_matrix(name: str) -> Matrix
Get a matrix with all the {pname} defined within this system.

:rtype: Matrix

.. note::
    This is equivalent to ``get_symbols_matrix('{kind}')``

    .. seealso:: :func:`get_symbols_matrix`
'''

# Template docstring for new_input, new_joint_unknown and new_parameter
_symbol_constructor_docstring_template = r'''new_{kind}(name: str[, tex_name: str][, value: numeric]) -> SymbolNumeric
Creates a new {name} with the given name and value in the system.

    :Example:

    >>> new_{kind}('a')
    a = 0.0

    >>> new_{kind}('a', 1.5)
    a = 1.5

    >>> a = new_{kind}('a', '\\sigma', 2)
    >>> a.tex_name, a.value
    '\\sigma', 2

    >>> a = new_{kind}('a', value=3, tex_name='\\beta')
    >>> a.tex_name, a.value
    '\\beta', 3

:param str name: The name of the {name}
:param str tex_name: Name in latex for the {name}. By default (if not specified) is autogenerated based
    on the given name if ``autogen_latex_names`` is enabled. Otherwise, its set to
    an empty string.

    .. seealso:: :func:`autogen_latex_names`

:param numeric value: The initial numeric value (by default its 0). This can be specified
    as positional argument before the latex name.

:rtype: SymbolNumeric

:raises TypeError: if the given arguments have incorrect types
:raises IndexError: If there is already an object defined in the system with the given
    name and its not a {name}

.. warning:: If there is already a {name} with the given name defined in the system,
    this method will only update the latex name & numeric value of such symbol and
    return it (it will also raise a user warning)

'''


# Template docstring for properties "coordinates", "parameters", "inputs", ...
_symbol_pgetter_prop_docstring_template = '''
Read only property that returns all the {pname} defined within this system.

:rtype: Mapping[str, SymbolNumeric]

.. note:: Its equivalent to ``get_symbols('{kind}')``

    .. seealso:: :func:`get_symbols`

'''

# Template docstring for properties "matrices", "vectors", "tensors", ...
_geom_object_pgetter_prop_docstring_template = '''
Read only property that returns all the {pname} defined within this system.

:rtype: Mapping[str, {class}]

.. note:: Its calls internally to ``get_{pkind}``

    .. seealso:: :func:`get_{pkind}`
'''




# Its time to autogenerate docstrings...

for _symbol_type in map(bytes.decode, _symbol_types):
    _symbol_ptype = _symbol_type + 's' if not _symbol_type.endswith('velocity') else _symbol_type[:-1] + 'ies'
    _symbol_name = _symbol_type.replace('_', ' ')
    _symbol_pname = _symbol_ptype.replace('_', ' ')

    _context = {
        'kind':_symbol_type, 'pkind':_symbol_ptype,
        'name':_symbol_name, 'pname':_symbol_pname
    }
    _getter_docstring = _symbol_getter_docstring_template.format(**_context)
    _pgetter_docstring = _symbol_pgetter_docstring_template.format(**_context)
    _matrix_getter_docstring = _symbol_matrix_getter_docstring_template.format(**_context)
    _checker_docstring = _symbol_checker_docstring_template.format(**_context)
    _pgetter_prop_docstring = _symbol_pgetter_prop_docstring_template.format(**_context)

    getattr(System, f'get_{_symbol_type}').__doc__ = _getter_docstring
    getattr(System, f'get_{_symbol_ptype}').__doc__ = _pgetter_docstring
    getattr(System, f'get_{_symbol_ptype}_matrix').__doc__ = _matrix_getter_docstring
    getattr(System, f'has_{_symbol_type}').__doc__ = _checker_docstring
    getattr(System, _symbol_ptype).__doc__ = _pgetter_prop_docstring

    if _symbol_type in ('input', 'joint_unknown', 'parameter'):
        _constructor_docstring = _symbol_constructor_docstring_template.format(**_context)
        getattr(System, f'new_{_symbol_type}').__doc__ = _constructor_docstring



# matrix, tensor, vector, point, frame
for _geom_type in map(bytes.decode, _geom_types):
    _geom_class = _geom_type.title()
    if _geom_type in ('vector', 'tensor', 'wrench'):
        _geom_class = _geom_class + '3D'

    if _geom_type == 'matrix':
        _geom_ptype = 'matrices'
    elif _geom_type == 'wrench':
        _geom_ptype = 'wrenches'
    else:
        _geom_ptype = _geom_type + 's'
    _geom_name = _geom_type
    _geom_pname = _geom_ptype

    _context = {
        'kind': _geom_type, 'pkind': _geom_ptype,
        'class': _geom_class,
        'name': _geom_name, 'pname': _geom_pname
    }
    _getter_docstring = _geom_object_getter_docstring_template.format(**_context)
    _pgetter_docstring = _geom_object_pgetter_docstring_template.format(**_context)
    _checker_docstring = _geom_object_checker_docstring_template.format(**_context)
    _pgetter_prop_docstring = _geom_object_pgetter_prop_docstring_template.format(**_context)

    getattr(System, f'get_{_geom_type}').__doc__ = _getter_docstring
    getattr(System, f'get_{_geom_ptype}').__doc__ = _pgetter_docstring
    getattr(System, f'has_{_geom_type}').__doc__ = _checker_docstring
    getattr(System, _geom_ptype).__doc__ = _pgetter_prop_docstring
