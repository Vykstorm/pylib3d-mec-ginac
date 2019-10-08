'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Expr, a basic wrapper of
the C++ class GiNac::ex
'''




######## Helper functions ########


cdef Expr _expr_from_c(c_ex x):
    # Converts GiNac::ex to Python class Expr instance
    expr = Expr()
    expr._c_handler = x
    return expr





######## Class Expr ########

cdef class Expr(Object):
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

    def __add__(left_op, right_op):
        return _expr_from_c(Expr(left_op)._c_handler + Expr(right_op)._c_handler)

    def __sub__(left_op, right_op):
        return _expr_from_c(Expr(left_op)._c_handler - Expr(right_op)._c_handler)

    def __mul__(left_op, right_op):
        if isinstance(right_op, Matrix):
            return NotImplemented
        return _expr_from_c(Expr(left_op)._c_handler * Expr(right_op)._c_handler)

    def __pow__(base, exp, modulo):
        if modulo is not None:
            return NotImplemented
        return _expr_from_c(c_pow(Expr(base)._c_handler, Expr(exp)._c_handler))



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



LatexRenderable.register(Expr)



######## Aliases for class Expr ########

Expression = Expr
Ex = Expr
