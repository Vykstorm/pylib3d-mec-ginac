

######## Import statements ########

from lib3d_mec_ginac_ext import _System
from lib3d_mec_ginac_ext import _symbol_types, _derivable_symbol_types, _geom_obj_types
from collections.abc import Mapping




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




    ######## Symbol getters ########


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
        return super().get_symbol(name, kind)



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
        return super().has_symbol(self, name, kind)



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
        '''get_matrices() -> Mapping[str, Base]
        Get all the matrices defined within this system
        :returns: All the matrices in a dictionary, where keys are base names and values,
            instances of the class Matrix
        :rtype: Mapping[str, Base]
        '''
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
            m = Matrix([0, 1, 2])
            >>> new_base('a', rotation_tupla=m)

        '''
        return self._new_base(name, args, kwargs)



    def new_matrix(self, name, *args, **kwargs):
        '''new_matrix(name[, shape][, values]) -> Matrix
        '''
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


    # property
    @property
    def pgetterprop(self):
        '''
        Read only property that returns all the {pname} within this system

        :rtype: {name}
        '''
        return self._get_geom_objs(kind)


    methods = [getter, checker, pgetterprop]

    # Format method docstrings
    for method in methods:
        for key, value in locals().items():
            if not isinstance(value, str):
                continue
            method.__doc__ = method.__doc__.replace('{' + key + '}', value)

    # Change method names
    getter.__name__ = 'get_' + name
    checker.__name__ = 'has_' + name
    pgetterprop.fget.__name__ = pname

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
