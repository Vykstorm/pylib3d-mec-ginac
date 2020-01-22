'''
Author: Víctor Ruiz Gómez
Description: This module defines the wrapper class SymbolNumeric.
'''




######## Class SymbolNumeric ########


cdef class SymbolNumeric(Object):
    '''
    Objects of this class can be used to perform math symbolic computation.

    .. note::
        Do not instantiate this class manually.
        Use the methods ``new_symbol``, ``new_parameter``, ``new_coordinate``, ...
        defined in the System class

        .. seealso:: :class:`System`

    '''

    ######## C Attributes  ########


    cdef c_symbol_numeric* _c_handler
    cdef object _owner
    cdef object _type



    ######## Constructor & Destructor  ########

    def __cinit__(self, Py_ssize_t ptr, _System owner=None):
        self._c_handler = <c_symbol_numeric*>ptr
        self._owner, self._type = owner, None


    ######## Getters ########


    def get_value(self):
        '''get_value() -> float
        :return: The numeric value of this symbol as a float value.

        :rtype: float

        '''
        return self.get_owner().get_value(self)



    cpdef double _get_value(self):
        return self._c_handler.get_value().to_double()




    cpdef get_tex_name(self):
        '''get_tex_name() -> str
        Get the name in latex of this symbol

        :rtype: str

        '''
        return (<bytes>self._c_handler.print_TeX_name()).decode()


    def get_owner(self):
        '''get_owner() -> System
        Get the system where this numeric symbol was created

        :rtype: System

        '''
        if self._owner is None:
            raise RuntimeError
        return self._owner


    def get_type(self):
        '''get_type() -> str
        Get the type of this symbol.

        :returns:
            One of the next values:
                'parameter', 'joint_unknown', 'input',
                'coordinate', 'velocity', 'acceleration',
                'aux_coordinate', 'aux_velocity', 'aux_acceleration'
                'time' (the last one only if this instance is the time symbol)

        :rtype: str

        '''
        if self._type is None:
            owner = self.get_owner()
            if self == owner._get_time():
                return 'time'
            for symbol_type in _symbol_types:
                if self in owner._get_symbols(symbol_type):
                    self._type = symbol_type.decode()
                    return self._type
            raise RuntimeError
        return self._type



    ######## Setters ########


    def set_value(self, value):
        '''set_value(value: numeric)
        Assigns a new numeric value to this symbol.

        :param value: It must be the new numeric value to assign for this symbol
        :type value: numeric
        :raises TypeError: If value has an incorrect type
        '''
        self.get_owner().set_value(self, value)


    cpdef _set_value(self, value):
        self._c_handler.set_value(c_numeric(<double>_parse_numeric_value(value)))




    cpdef set_tex_name(self, tex_name):
        '''set_tex_name(tex_name: str)
        Changes the latex name of this symbol

        :param str tex_name: The new latex name
        :raise TypeError: If the input argument has an incorrect type
        '''
        self._c_handler.set_TeX_name(_parse_text(tex_name))




    ######## Properties  ########


    @property
    def value(self):
        '''
        Property that returns the numeric value of this symbol (as a float number). It also supports
        assignment.

        :rtype: float

        .. note:: It calls internally the methods ``get_value`` or ``set_value``

            .. seealso::
                :func:`get_value`
                :func:`set_value`
        '''
        return self.get_value()

    @value.setter
    def value(self, value):
        self.set_value(value)


    @property
    def tex_name(self):
        '''
        Property that returns the name in latex of this symbol. It also supports assignment.

        :rtype: str

        .. note:: It calls internally the methods ``get_tex_name`` or ``set_tex_name``

            .. seealso::
                :func:`get_tex_name`
                :func:`set_tex_name`
        '''
        return self.get_tex_name()


    @tex_name.setter
    def tex_name(self, tex_name):
        self.set_tex_name(tex_name)


    @property
    def owner(self):
        '''
        Property that returns the system where this symbol was created

        :rtype: System

        '''
        return self.get_owner()


    @property
    def type(self):
        '''
        Only read property that returns the kind of symbol

        :rtype: str

        '''
        return self.get_type()


    @property
    def kind(self):
        '''
        This is an alias of property "type"

        :rtype: str

        '''
        return self.get_type()



    ######## Arithmetic operations ########


    def __neg__(self):
        '''
        Negates this symbol. The result is a symbolic expression.
        :rtype: Expr
        '''
        return -Expr(self)


    def __pos__(self):
        '''
        Performs unary positive operation on this symbol.
        The result is a expression.
        :rtype: Expr
        '''
        return +Expr(self)


    def __add__(self, other):
        '''
        Performs the sum operation with another symbol. The result is a symbolic
        expression.
        :rtype: Expr
        .. note:: Sum operation can be performed between symbols and expressions, but
            this logic is implemented in Expr.__add__ metamethod
        '''
        return NotImplemented if isinstance(other, Expr) else Expr(self) + Expr(other)


    def __sub__(self, other):
        '''
        Performs the subtraction operation with another symbol. The result is a symbolic
        expression.
        :rtype: Expr
        .. note:: Subtraction operation can be performed between symbols and expressions, but
            this logic is implemented in Expr.__sub__ metamethod
        '''
        return NotImplemented if isinstance(other, Expr) else Expr(self) - Expr(other)


    def __mul__(self, other):
        '''
        Multiplies this symbol with another. The result is a symbolic expression.
        :rtype: Expr
        .. note:: Symbols can be multiplied with matrices (or its subclasses) and expressions, but this is implemented
            in the metamethods Expr.__mul__, Matrix.__mul__, Vector3D.__mul__ and Tensor3D.__mul__
        '''
        return NotImplemented if isinstance(other, (Expr, Matrix, Wrench3D)) else Expr(self) * Expr(other)


    def __truediv__(self, other):
        '''
        :rtype: Expr
        Divides this symbol with another. The result is a symbolic expression.
        .. note:: Symbols can also divide or be divided by expressions. This
            functionality is implemented in Expr.__truediv__
        '''
        return NotImplemented if isinstance(other, Expr) else Expr(self) / other


    def __pow__(self, other, modulo):
        '''
        :rtype: Expr
        Raises this symbol by another one (the exponent could also be an expression).
        The result is an expression.
        '''
        return pow(Expr(self), other, modulo)




    ######## Number conversions ########


    def __float__(self):
        '''
        You can use the built-in float function to
        get the numeric value of this symbol:

            :Example:

            >>> a = new_param('a', 1.5)
            >>> float(a)
            1.5

        .. note::
            Its equivalent to ``get_value()``

            .. seealso:: :func:`get_value`
        '''
        return self.get_value()


    def __int__(self):
        '''
        You can use the built-in int function to
        get the numeric value of this symbol (as an integer):

            :Example:

            >>> a = new_param('a', 1.5)
            >>> int(a)
            1

        .. note::
            Its equivalent to ``int(get_value())``

            .. seealso:: :func:`get_value`
        '''
        return int(self.get_value())



    def __complex__(self):
        '''
        You can use the built-in complex function to
        get the numeric value of this symbol as a complex number (the imaginary
        part is set to zero):

            :Example:

            >>> a = new_param('a', 1.5)
            >>> complex(a)
            1.5+0j

        .. note::
            Its equivalent to ``complex(get_value())``

            .. seealso:: :func:`get_value`
        '''
        return complex(self._c_handler.get_value().real().to_double(), self._c_handler.get_value().imag().to_double())





    ######## Comparision operations ########


    def __eq__(self, other):
        if isinstance(other, Expr):
            return NotImplemented
        return super().__eq__(other)




NamedObject.register(SymbolNumeric)
LatexRenderable.register(SymbolNumeric)
