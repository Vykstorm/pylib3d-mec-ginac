'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Expr, a basic wrapper of
the C++ class GiNac::ex
'''




######## Class Expr ########

cdef class Expr:
    '''
    This class represents a symbolic expression.
    It implements a subset of the features provided by the C++ class GiNac::ex
    '''

    ######## C Attributes ########


    cdef c_ex _c_handler



    ######## Constructor ########


    def __cinit__(self, value=None):
        if value is not None:
            if not isinstance(value, (int, float, SymbolNumeric, Expr)):
                raise TypeError(f'"{type(value)} object cant be converted to an expression"')

            if isinstance(value, (int, float)):
                self._c_handler = c_ex(<double>float(value))
            elif isinstance(value, SymbolNumeric):
                self._c_handler = c_ex(c_deref(<c_basic*>((<SymbolNumeric>value)._c_handler)))
            else:
                self._c_handler = (<Expr>value)._c_handler


    ######## Getters ########



    ######## Evaluation ########


    cpdef eval(self):
        return _expr_from_c(self._c_handler.eval())



    ######## Properties ########





    ######## Arithmetic operations ########


    def __neg__(self):
        return _expr_from_c(-self._c_handler)

    def __pos__(self):
        return _expr_from_c(+self._c_handler)

    def __add__(self, other):
        return _expr_from_c(Expr(self)._c_handler + Expr(other)._c_handler)

    def __sub__(self, other):
        return _expr_from_c(Expr(self)._c_handler - Expr(other)._c_handler)

    def __mul__(self, other):
        if isinstance(other, Matrix):
            return NotImplemented
        return _expr_from_c(Expr(self)._c_handler * Expr(other)._c_handler)

    def __pow__(self, other, modulo):
        if modulo is not None:
            return NotImplemented
        return _expr_from_c(c_pow(Expr(self)._c_handler, Expr(other)._c_handler))



    def __truediv__(self, other):
        return _expr_from_c(Expr(self)._c_handler / Expr(other)._c_handler)


    def __iadd__(self, other):
        self._c_handler = self._c_handler + Expr(other)._c_handler
        return self

    def __isub__(self, other):
        self._c_handler = self._c_handler - Expr(other)._c_handler
        return self

    def __imul__(self, other):
        self._c_handler = self._c_handler * Expr(other)._c_handler
        return self

    def __itruediv__(self, other):
        self._c_handler = self._c_handler / Expr(other)._c_handler
        return self




    ######## Printing ########


    def __str__(self):
        # Use GiNac print method
        x = _ginac_print_ex(self._c_handler)

        # Try to format the expression as a number (remove decimals if its integer)
        try:
            x = float(x)
            if floor(x) == x:
                x = floor(x)
            else:
                x = round(x, 4)
            return str(x)
        except:
            return x



    def __repr__(self):
        return self.__str__()
