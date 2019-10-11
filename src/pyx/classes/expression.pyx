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

            if isinstance(value, float):
                self._c_handler = c_ex(<double>value)
            elif isinstance(value, int):
                self._c_handler = c_ex(<long>value)
            elif isinstance(value, SymbolNumeric):
                self._c_handler = c_ex(c_deref(<c_basic*>((<SymbolNumeric>value)._c_handler)))
            else:
                self._c_handler = (<Expr>value)._c_handler


    ######## Getters ########



    ######## Evaluation ########


    cpdef eval(self):
        return _expr_from_c(self._c_handler.eval())



    ######## Properties ########





    ######## Arithmetic unary operations ########


    def __neg__(self):
        '''
        Get this expression negated.
        :rtype: Expr
        '''
        return _expr_from_c(-self._c_handler)


    def __pos__(self):
        '''
        This method implements the unary positive operator for this expression.
        :rtype: Expr
        '''
        return _expr_from_c(+self._c_handler)




    ######## Arithmetic binary operations ########


    def __add__(left_op, right_op):
        '''
        Sum two expressions.
        :rtype: Expr
        :raise TypeError: If the operands have incorrect types
        .. note:: One of the operands can also be any object which can be converted to
            an expression (a numeric symbol or number)
        '''
        return _expr_from_c(Expr(left_op)._c_handler + Expr(right_op)._c_handler)


    def __sub__(left_op, right_op):
        '''
        Subtract two expressions.
        :rtype: Expr
        :raise TypeError: If the operands have incorrect types
        .. note:: One of the operands can also be any object which can be converted to
            an expression (a numeric symbol or number)
        '''
        return _expr_from_c(Expr(left_op)._c_handler - Expr(right_op)._c_handler)


    def __mul__(left_op, right_op):
        '''
        Computes the product of two expressions.
        :rtype: Expr
        :raise TypeError: If the operands have incorrect types
        .. note:: One of the operands can also be any object which can be converted to
            an expression (a numeric symbol or number)
        '''
        if isinstance(right_op, Matrix):
            return NotImplemented
        return _expr_from_c(Expr(left_op)._c_handler * Expr(right_op)._c_handler)


    def __pow__(base, exp, modulo):
        '''
        Returns this expression raised to the power of another expression.
        :rtype: Expr
        :raise TypeError: If the operands have incorrect types
        .. note:: One of the operands (either the base or the exponent)
            can also be any object which can be converted to
            an expression (a numeric symbol or number)
        '''
        if modulo is not None:
            return NotImplemented
        return _expr_from_c(c_pow(Expr(base)._c_handler, Expr(exp)._c_handler))



    def __truediv__(self, other):
        '''
        Returns this expression divided by another
        :rtype: Expr
        :raise TypeError: If the operands have incorrect types
        .. note:: One of the operands can also be any object which can be converted to
            an expression (a numeric symbol or number)
        '''
        if other == 0:
            raise ZeroDivisionError('Expression divided by zero')
        return _expr_from_c(Expr(self)._c_handler / Expr(other)._c_handler)




    ######## Arithmetic binary operations (inplace) ########


    def __iadd__(self, other):
        '''
        Perform an inplace sum operation with another expression
        :rtype: Expr
        :return: This instance
        :raise TypeError: If the operands have incorrect types
        .. note:: The input argument must be an expression or any object which can
            be converted to an expression (a numeric symbol or number)
        '''
        self._c_handler = self._c_handler + Expr(other)._c_handler
        return self


    def __isub__(self, other):
        '''
        Perform an inplace subtract operation with another expression
        :rtype: Expr
        :return: This instance
        :raise TypeError: If the operands have incorrect types
        .. note:: The input argument must be an expression or any object which can
            be converted to an expression (a numeric symbol or number)
        '''
        self._c_handler = self._c_handler - Expr(other)._c_handler
        return self


    def __imul__(self, other):
        '''
        Perform an inplace product operation with another expression
        :rtype: Expr
        :return: This instance
        :raise TypeError: If the operands have incorrect types
        .. note:: The input argument must be an expression or any object which can
            be converted to an expression (a numeric symbol or number)
        '''
        self._c_handler = self._c_handler * Expr(other)._c_handler
        return self

    def __itruediv__(self, other):
        '''
        Perform an inplace division operation with another expression
        :rtype: Expr
        :return: This instance
        :raise TypeError: If the operands have incorrect types
        .. note:: The input argument must be an expression or any object which can
            be converted to an expression (a numeric symbol or number)
        '''
        self._c_handler = self._c_handler / Expr(other)._c_handler
        return self




    ######## Comparision binary operations ########


    def __eq__(Expr self, other):
        if other == 0:
            return self._c_handler.is_zero()
        return self._c_handler.is_equal(Expr(other)._c_handler)



LatexRenderable.register(Expr)



######## Aliases for class Expr ########

Expression = Expr
Ex = Expr
