{#
'''
Author: Víctor Ruiz Gómez
Description: This module defines the wrapper class SymbolNumeric and all its subclasses.
'''
#}

## Import statements
from src.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from collections import OrderedDict


## Wrapper of the symbol_numeric class for Python
cdef class SymbolNumeric:
    '''
    Objects of this class can be used to perform math symbolic computation.
    '''

    ######## C Attributes  ########

    cdef c_symbol_numeric* handler
    cdef System _owner


    ######## Constructor & Destructor  ########

    def __cinit__(self, Py_ssize_t handler, owner):
        self.handler = <c_symbol_numeric*>handler
        self._owner = owner


    ######## Properties  ########

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

    @property
    def owner(self):
        '''
        Only read property that returns the System object that created this symbol.

        :rtype: System
        '''
        return self.get_owner()


    ######## Getters ########

    cpdef float get_value(self):
        '''get_value() -> float

        :return: The numeric value of this symbol as a float value.
        :rtype: float
        '''
        return self.handler.get_value().to_double()

    cdef get_owner(self):
        '''get_owner() -> System
        Get the System object that created this symbol.

        :rtype: System
        '''
        return self._owner


    ######## Setters ########

    cpdef set_value(self, value):
        '''set_value(value: Union[int, float, complex])
        Assigns a new numeric value to this symbol.

        :param value: It must be the new numeric value to assign for this symbol
        :type value: int, float
        :raises TypeError: If value has an incorrect type.
        '''
        if not isinstance(value, (int, float)):
            raise TypeError(f'Value must be a int or float')
        self.handler.set_value(c_numeric(float(value)))


    ######## Metamethods ########

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
        return f'{self.__class__.__name__.lower()} {self.name}, value = {round(self.value, 4)}'

    def __repr__(self):
        return self.__str__()




## Wrappers for subclasses of symbol_numeric
# They only redefine the method __str__ to improve symbol printing on the python console

{% for symbol_type in symbol_types %}
{% set symbol_name = symbol_type | replace('_', ' ') %}
cdef class {{symbol_type | pytitle}}(SymbolNumeric):
    '''
    Represents {{symbol_name | aprefix}} symbol defined within a system.
    '''
    _display_name = "{{symbol_name}}"

    def __str__(self):
        return f'{{symbol_name}} {self.name}, value = {round(self.value, 4)}'

{% endfor %}



## Wrapper for values returned by symbol container getters in the class System
class SymbolsDict(OrderedDict):
    def __str__(self):
        if len(self.keys()) == 0:
            # No symbols at all
            return 'No symbols yet'

        lines = []
        for name, symbol in self.items():
            line = ''
            # Print the symbol type
            if len(frozenset(map(type, self.values()))) > 1:
                line += symbol._display_name.ljust(18) + ' '

            # Print the symbol name
            line += name.ljust(12) + ' '

            # Print the symbol value
            line += str(round(symbol.value, 4)).ljust(12)

            lines.append(line)

        return '\n'.join(lines)


    def __repr__(self):
        return self.__str__()
