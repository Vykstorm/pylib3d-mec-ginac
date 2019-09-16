
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
from src.cnumeric cimport numeric as c_numeric


# Python imports
from collections.abc import Mapping
from operator import attrgetter





## Wrapper of the symbol_numeric class for Python
cdef class SymbolNumeric:
    '''
    Objects of this class can be used to perform math symbolic computation.
    '''
    cdef symbol_numeric* handler

    def __cinit__(self, Py_ssize_t handler):
        self.handler = <symbol_numeric*>handler

    @property
    def name(self):
        '''
        Only read property that returns the name of this symbol.

        :rtype: str
        '''
        return (<bytes>self.handler.get_name()).decode()

    @property
    def tex_name(self):
        '''
        Only read property that returns the name in latex of this symbol.

        :rtype: str
        '''
        return (<bytes>self.handler.print_TeX_name()).decode()

    @property
    def value(self):
        '''
        Property that returns the numeric value of this symbol (as a float number). It also supports
        assignment.

        :rtype: float
        '''
        return self.get_value()


    @value.setter
    def value(self, value):
        self.set_value(value)


    cpdef float get_value(self):
        '''get_value() -> float

        :return: The numeric value of this symbol as a float value.
        :rtype: float
        '''
        return self.handler.get_value().to_double()


    cpdef set_value(self, float value):
        '''set_value(value: Union[int, float, complex, str])
        Assigns a new numeric value to this symbol.

        :param value: It must be the new numeric value to assign for this symbol
        :type value: int, float, complex, str
        :raises TypeError: If value has an incorrect type.
        '''
        if not isinstance(value, (int, float, complex, str)):
            raise TypeError(f'Value must be a int, float, complex or str')
        self.handler.set_value(c_numeric(value))


    def __float__(self):
        '''
        Alias of get_value().
        '''
        return self.get_value()


    def __int__(self):
        '''
        Returns the numeric value of this symbol truncated (as an integer)

        :rtype: int
        '''
        return int(self.get_value())


    def __complex__(self):
        '''
        Returns the numeric value of this symbol as a complex number.

        :rtype: complex
        '''
        return complex(self.handler.get_value().real().to_double(), self.handler.get_value().imag().to_double())


    def __str__(self):
        return f'Symbol {self.name}, value = {self.value}'

    def __repr__(self):
        return self.__str__()




## Wrapper of the symbol_numeric class for Python for parameters
cdef class Parameter(SymbolNumeric):
    '''
    Represents a parameter in a mechanical system.
    '''
    def __str__(self):
        return f'Parameter {self.name}, value = {self.value}'




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

        cdef symbol_numeric* handler
        if tex_name is None:
            handler = self.system.new_Parameter(name.encode())
        else:
            handler = self.system.new_Parameter(name.encode(), tex_name.encode())
        return Parameter(<Py_ssize_t>handler)


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


    cpdef _get_parameters(self):
        '''
        Retrieve a list with all the parameters created in the system.
        '''
        params = []
        cdef vector[symbol_numeric*] ptrs = self.system.get_Parameters()
        cdef symbol_numeric* ptr
        for ptr in ptrs:
            params.append(Parameter(<Py_ssize_t>ptr))
        return params


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
        '''set_value(symbol: Union[str, SymbolNumeric], value: Union[str, float, int, complex])
        Set the numeric value of a symbol.

        :param symbol: The symbol where to assign a new numeric value
        :type symbol: str or SymbolNumeric
        :param value: The new value
        :type value: int, float, complex, str

        :raises TypeError: If input arguments have invalid types
        :raises ValueError: If the first argument is a string and there not exists a symbol in the system with that name.
        '''
        if isinstance(symbol, str):
            symbol = self.get_symbol(symbol)
        elif not isinstance(symbol, SymbolNumeric):
            raise TypeError(f'First argument must be a string or an instance of the class {SymbolNumeric.__name__}')
        symbol.set_value(value)


    @property
    def parameters(self):
        '''
        This property (read only) retrieves all the parameters in the system.

        :return: A dictionary where keys are parameter names and values, instances of the class Parameter
        :rtype: Dict[str, Parameter]
        '''
        params = self._get_parameters()
        return dict(zip(map(attrgetter('name'), params), params))
