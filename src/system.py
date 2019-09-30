'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class System
'''


######## Import statements ########

from lib3d_mec_ginac_ext import _System
from .views import SymbolsView, BasesView, MatricesView, VectorsView



######## System class ########


class System(_System):
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''


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




    ######## Getters ########


    def get_symbol(self, name, kind=None):
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
        return super()._get_symbol(name, kind)



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
        return self.get_symbol(name, b'acceleration')

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
        return super()._has_symbol(name, kind)



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
        return self.has_symbol(name, b'acceleration')

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
        Get all symbols defined within this system

        :param str kind: Its an optional argument that can be used to retrieve
            only symbols with the given type e.g: 'parameter', 'input', ...
        :returns: Returns all the symbols defined in a dictionary, where keys are
            symbol names and values, instances of the class SymbolNumeric
        :rtype: Mapping[str, SymbolNumeric]
        '''
        return SymbolsView(self, kind)


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
        return BasesView(self)

    def get_matrices(self):
        return MatricesView(self)

    def get_vectors(self):
        return VectorsView(self)


    get_coords = get_coordinates
    get_aux_coords = get_aux_coordinates

    get_params = get_parameters
    get_unknowns = get_joint_unknowns




    def get_symbols_matrix(self, kind):
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




    ######## Constructors ########


    def new_symbol(self, kind, *args, **kwargs):
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
        return self.new_symbol(b'coordinate', *args, **kwargs)



    def new_aux_coordinate(self, *args, **kwargs):
        '''new_aux_coordinate(name: str[, vel_name: str[, acc_name: str[, tex_name: str[, vel_tex_name: str][, acc_tex_name: str]]]]], [value: float[, vel_value: float[, acc_value: float]]])) -> SymbolNumeric
        Creates a new "auxiliar" coordinate symbol and its derivative components (velocity and acceleration)
        The signature is the same as for new_coordinate method
        '''
        return self.new_symbol(b'aux_coordinate', *args, **kwargs)


    def new_parameter(self, *args, **kwargs):
        return self.new_symbol(b'parameter', *args, **kwargs)

    def new_joint_unknown(self, *args, **kwargs):
        return self.new_symbol(b'joint_unknown', *args, **kwargs)

    def new_input(self, *args, **kwargs):
        return self.new_symbol(b'input', *args, **kwargs)



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
            m = Matrix([0, 1, 2])
            >>> new_base('a', rotation_tupla=m)

        '''
        return super()._new_base(name, args, kwargs)



    def new_matrix(self, name, *args, **kwargs):
        '''new_matrix(name[, shape][, values]) -> Matrix
        '''
        return super()._new_matrix(name, args, kwargs)

    def new_vector(self, name, *args, **kwargs):
        return super()._new_vector(name, args, kwargs)


    new_coord = new_coordinate
    new_aux_coord = new_aux_coordinate,
    new_param = new_parameter
    new_unknown = new_joint_unknown




    ######## Properties ########

    @property
    def symbols(self):
        '''
        Only read property that returns all the symbols defined within this system.

        :rtype: Mapping[str, SymbolNumeric]
        '''
        return self.get_symbols()


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


    coords = coordinates
    aux_coords = aux_coordinates
    params = parameters
    unknowns = joint_unknowns





    ######## Mixin methods ########

    def set_as_default(self):
        '''
        Set this instance as the default system
        '''
        from . import set_default_system
        set_default_system(self)




    ######## Metamethods ########

    def __str__(self):
        return 'System instance'

    def __repr__(self):
        return self.__str__()
