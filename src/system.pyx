
{#
'''
Author: Víctor Ruiz Gómez
Description: This module defines the class System
'''
#}


## Import statements

# Import cython internal library
cimport cython

# C++ standard library imports
from libcpp.string cimport string
from libcpp.vector cimport vector

# Import .pxd declarations
from src.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.csystem cimport System as c_System
from src.cnumeric cimport numeric as c_numeric

# Python imports
from collections.abc import Mapping
from operator import attrgetter



## Wrapper of System class for Python
cdef class System:
    '''
    Its the main class of the library. It represents a mechanical system defined with different variables:
    coordinates, parameters, inputs, tensors, ...
    '''
    ######## C Attributes ########

    cdef c_System* system


    ######## Constructor & Destructor ########

    def __cinit__(self):
        self.system = new c_System()

    def __dealloc__(self):
        del self.system


    ######## Symbol spawners  ########

    cpdef Parameter new_parameter(self, unicode name, unicode tex_name=None):
        '''new_parameter(name: str[, tex_name: str]) -> Parameter
        Creates a new parameter with the given name.

        :param str name: The name of the new parameter
        :param str tex_name: The name of the new parameter in latex.
        :return: Returns the parameter created on success
        :rtype: Parameter
        :raises TypeError: If input arguments have incorrect types
        :raises ValueError: If a parameter with the given name already exists in the system
        '''
        if name is None:
            raise TypeError('Parameter name must be a string')
        if self.has_parameter(name):
            raise ValueError(f'Parameter "{name}" already created')

        cdef c_symbol_numeric* handler
        if tex_name is None:
            handler = self.system.new_Parameter(name.encode())
        else:
            handler = self.system.new_Parameter(name.encode(), tex_name.encode())
        return Parameter(<Py_ssize_t>handler, self)


    ######## Symbol getters ########

    cpdef get_symbol(self, unicode name):
        '''get_symbol(name: str) -> SymbolNumeric
        Get a symbol defined on this system by name

        :param str name: Name of the symbol
        :return: Return the symbol defined on the system with the specified name.
        :rtype: str
        :raises TypeError: If input argument have invalid type
        :raises ValueError: If no symbol with that name exists in the system.
        '''
        return self.get_parameter(name)


    cpdef Parameter get_parameter(self, unicode name):
        '''get_parameter(name: str) -> Parameter
        Get a parameter by name.

        :param str name: The name of the parameter to query
        :return: The parameter on the system with the specified name
        :rtype: Parameter
        :raises TypeError: If input argument have invalid type
        :raises ValueError: If no parameter with the given name exists in the system
        '''
        if name is None:
            raise TypeError('Parameter name must be a string')
        if not self.has_parameter(name):
            raise ValueError(f'Parameter "{name}" not created yet')
        return Parameter(<Py_ssize_t>self.system.get_Parameter(name.encode()), self)


    cdef bint has_parameter(self, unicode name):
        '''
        Check if a parameter with the given name exists.
        '''
        cdef vector[c_symbol_numeric*] ptrs = self.system.get_Parameters()
        cdef c_symbol_numeric* ptr
        for ptr in ptrs:
            if ptr.get_name() == <string>name.encode():
                return 1
        return 0


    ######## Symbol containers getters ########

    cpdef get_symbols(self):
        '''get_symbols() -> Dict[str, SymbolNumeric]
        Get all the symbols defined in the system.

        :return: Return all the symbols defined in the system in a dictionary, where
        keys are symbol names and values, instances of the class SymbolNumeric.
        :rtype: Dict[str, SymbolNumeric]
        '''
        # TODO
        symbols = {}
        {% for symbol_type in symbol_types %}
        symbols.update(self.{{symbol_type | plural | getter}}()){% endfor %}
        return symbols



    {% for symbol_type in symbol_types %}
    cpdef {{symbol_type | plural | getter}}(self):
        '''{{symbol_type | plural | getter}}() -> Dict[str, {{symbol_type | pytitle}}]
        Get all the {{symbol_type | plural}} created within the system.

        :return: Return all the {{symbol_type | replace('_', ' ')}} symbols defined in the system in a dictionary where
        keys are their names and the entry values, instances of the class {{symbol_type | pytitle}}.
        :rtype: Dict[str, {{symbol_type | pytitle}}]
        '''
        items = []
        {% if symbol_type == 'joint_unknown' %}
        cdef vector[c_symbol_numeric*] ptrs = self.system.get_Joint_Unknowns()
        {% else %}
        cdef vector[c_symbol_numeric*] ptrs = self.system.{{symbol_type | plural | pytitle | getter}}()
        {% endif %}
        cdef c_symbol_numeric* ptr
        for ptr in ptrs:
            items.append({{symbol_type | pytitle}}(<Py_ssize_t>ptr, self))
        return dict(zip(map(attrgetter('name'), items), items))

    {% endfor %}



    ######## Symbol containers properties ########

    @property
    def symbols(self):
        '''
        This property (read only) retrieves all the symbols defined in the system.
        :return: The same as get_symbols()
        :rtype: Dict[str, SymbolNumeric]
        '''
        return self.get_symbols()


    {% for symbol_type in symbol_types %}
    @property
    def {{symbol_type | plural}}(self):
        '''
        This property (read only) retrieves all the {{symbol_type | plural}} defined within the system.

        :return: The same as {{symbol_type | plural | getter}}()
        :rtype: Dict[str, {{symbol_type | pytitle}}]
        '''
        return self.{{symbol_type | plural | getter}}()

    {% endfor %}



    ######## Symbol value getter & setter ########

    cpdef get_value(self, symbol):
        '''get_value(symbol: Union[str, SymbolNumeric]) -> float
        Get the numeric value of a symbol.

        :param symbol: The symbol to fetch its numeric value
        :type symbol: str or SymbolNumeric
        :return: The value of the symbol specified
        :rtype: float
        :raises TypeError: if input arguments have invalid types
        :raises ValueError: if the argument is a string and there not exists a symbol in the system with that name
        '''
        if isinstance(symbol, str):
            symbol = self.get_symbol(symbol)
        elif not isinstance(symbol, SymbolNumeric):
            raise TypeError(f'Input argument must be a string or an instance of the class {SymbolNumeric.__name__}')
        return symbol.get_value()


    cpdef set_value(self, symbol, value):
        '''set_value(symbol: Union[str, SymbolNumeric], value: Union[float, int])
        Set the numeric value of a symbol.

        :param symbol: The symbol where to assign a new numeric value
        :type symbol: str or SymbolNumeric
        :param value: The new value
        :type value: int, float

        :raises TypeError: If input arguments have invalid types
        :raises ValueError: If the first argument is a string and there not exists a symbol in the system with that name.
        '''
        if isinstance(symbol, str):
            symbol = self.get_symbol(symbol)
        elif not isinstance(symbol, SymbolNumeric):
            raise TypeError(f'First argument must be a string or an instance of the class {SymbolNumeric.__name__}')
        symbol.set_value(value)
