'''
Author: Víctor Ruiz Gómez
Description: This module defines the wrapper class SymbolNumeric.
'''




######## Class SymbolNumeric ########


cdef class SymbolNumeric:
    '''
    Objects of this class can be used to perform math symbolic computation.
    '''

    ######## C Attributes  ########


    cdef c_symbol_numeric* _c_handler



    ######## Constructor & Destructor  ########

    def __cinit__(self, Py_ssize_t ptr):
        self._c_handler = <c_symbol_numeric*>ptr


    ######## Getters ########


    cpdef double get_value(self):
        '''get_value() -> float
        :return: The numeric value of this symbol as a float value.
        :rtype: float
        '''
        return self._c_handler.get_value().to_double()


    cpdef get_name(self):
        '''get_name() -> str
        Get the name of this symbol
        :rtype: str
        '''
        return (<bytes>self._c_handler.get_name()).decode()


    cpdef get_tex_name(self):
        '''get_tex_name() -> str
        Get the name in latex of this symbol
        :rtype: str
        '''
        return (<bytes>self._c_handler.print_TeX_name()).decode()




    ######## Setters ########


    cpdef set_value(self, value):
        '''set_value(value: float)
        Assigns a new numeric value to this symbol.
        :param value: It must be the new numeric value to assign for this symbol
        :type value: int, float
        :raises TypeError: If value has an incorrect type.
        '''
        self._c_handler.set_value(c_numeric(_parse_symbol_value(value)))




    ######## Properties  ########


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
    def name(self):
        '''
        Only read property that returns the name of this symbol.
        :rtype: str
        '''
        return self.get_name()


    @property
    def tex_name(self):
        '''
        Only read property that returns the name in latex of this symbol.
        :rtype: str
        '''
        return self.get_tex_name()




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
        return complex(self._c_handler.get_value().real().to_double(), self._c_handler.get_value().imag().to_double())


    def __hash__(self):
        '''
        Returns the hash value for this symbol. One instance of this class is equal to
        another one if they refer to the same numeric symbol (same name)
        '''
        return hash((SymbolNumeric, self.name))


    def __eq__(self, other):
        '''
        Check if two objects refer to the same numeric symbol (have the same name)
        :param other: Other object to compare this instance with
        :return: True if the specified object is also an instance of the class SymbolNumeric and have the same name as this object. False otherwise.
        :rtype: bool
        '''
        if not isinstance(other, SymbolNumeric):
            return False
        return self.name == other.name


    def __str__(self):
        return f'Symbol {self.name}, value = {round(self.value, 4)}'

    def __repr__(self):
        return self.__str__()
