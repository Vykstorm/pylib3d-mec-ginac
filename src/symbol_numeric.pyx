'''
Author: Víctor Ruiz Gómez
Description: This module defines the wrapper class SymbolNumeric.
'''




######## Class SymbolNumeric ########


cdef class SymbolNumeric(Object):
    '''
    Objects of this class can be used to perform math symbolic computation.
    '''

    ######## C Attributes  ########


    cdef c_symbol_numeric* _c_handler
    cdef object _owner



    ######## Constructor & Destructor  ########

    def __cinit__(self, Py_ssize_t ptr, owner):
        self._c_handler = <c_symbol_numeric*>ptr
        self._owner = owner


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


    def get_owner(self):
        return self._owner


    def get_type(self):
        owner = self.get_owner()
        if self == owner._get_time():
            return 'time'
        for symbol_type in _symbol_types:
            if self in owner._get_symbols(symbol_type):
                return symbol_type.decode()
        raise RuntimeError



    ######## Setters ########


    cpdef set_value(self, value):
        '''set_value(value: float)
        Assigns a new numeric value to this symbol.
        :param value: It must be the new numeric value to assign for this symbol
        :type value: int, float
        :raises TypeError: If value has an incorrect type.
        '''
        self._c_handler.set_value(c_numeric(<double>_parse_numeric_value(value)))



    cpdef set_tex_name(self, tex_name):
        self._c_handler.set_TeX_name(_parse_text(tex_name))




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
    def tex_name(self):
        '''
        Property that returns the name in latex of this symbol.
        :rtype: str
        '''
        return self.get_tex_name()


    @tex_name.setter
    def tex_name(self, tex_name):
        self.set_tex_name(tex_name)


    @property
    def owner(self):
        return self.get_owner()


    @property
    def type(self):
        return self.get_type()

    @property
    def kind(self):
        return self.get_type()



    ######## Arithmetic operations ########


    def __neg__(self):
        return -Expr(self)

    def __pos__(self):
        return +Expr(self)

    def __add__(self, other):
        return NotImplemented if isinstance(other, Expr) else Expr(self) + Expr(other)

    def __sub__(self, other):
        return NotImplemented if isinstance(other, Expr) else Expr(self) - Expr(other)

    def __mul__(self, other):
        return NotImplemented if isinstance(other, (Expr, Matrix)) else Expr(self) * Expr(other)

    def __truediv__(self, other):
        return NotImplemented if isinstance(other, Expr) else Expr(self) / Expr(other)

    def __pow__(self, other, modulo):
        return pow(Expr(self), other, modulo)




    ######## Number conversions ########


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





    ######## Printing ########


    def to_latex(self):
        return self.get_tex_name() or r'\textrm{' + self.get_name()  + '}'


    def __str__(self):
        return f'{self.get_name()} = {round(self.get_value(), 4)}'





NamedObject.register(SymbolNumeric)
LatexRenderable.register(SymbolNumeric)
