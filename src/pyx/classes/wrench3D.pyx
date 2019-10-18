'''
Author: Víctor Ruiz Gómez
Description:
This file defines the Wrench3D class
'''




cdef Wrench3D _wrench_from_c(c_Wrench3D* x):
    wrench = Wrench3D()
    wrench._c_handler, wrench._owns_c_handler = x, False
    return wrench


cdef Wrench3D _wrench_from_c_value(c_Wrench3D x):
    wrench = Wrench3D()
    wrench._c_handler = new c_Wrench3D(
        x.get_name(), x.get_Force(), x.get_Moment(), x.get_Point(),
        x.get_Solid(), x.get_Type()
    )
    wrench._owns_c_handler = True
    return wrench




cdef class Wrench3D(Object):
    '''
    An instance of this class represents a wrench which is attached to solid and
    has a force and momentum vectors.
    '''

    ######## Constructor ########

    cdef c_Wrench3D* _c_handler
    cdef bint _owns_c_handler



    ######## Constructor & Destructor ########

    def __cinit__(self):
        self._c_handler = NULL


    def __dealloc__(self):
        if self._c_handler != NULL and self._owns_c_handler:
            del self._c_handler



    ######## Getters ########


    cpdef get_force(self):
        '''get_force() -> Vector3D
        Get the force vector of this wrench

        :rtype: Vector3D

        '''
        return _vector_from_c_value(self._c_handler.get_Force())


    cpdef get_moment(self):
        '''get_moment() -> Vector3D
        Get the moment vector of this wrench

        :rtype: Vector3D

        '''
        return _vector_from_c_value(self._c_handler.get_Moment())


    cpdef get_solid(self):
        '''get_solid() -> Solid
        Get the solid of this wrench

        :rtype: Solid

        '''
        return Solid(<Py_ssize_t>self._c_handler.get_Solid())


    cpdef get_type(self):
        '''get_type() -> str
        Get the type of this wrench

        :rtype: str

        '''
        return (<bytes>self._c_handler.get_Type()).decode()



    ######## Operations ########


    cpdef unatomize(self):
        return _wrench_from_c_value(self._c_handler.unatomize())


    cpdef at_point(self, point):
        if not isinstance(point, Point):
            raise TypeError('Input argument must be a Point object')
        return _wrench_from_c_value(self._c_handler.at_Point((<Point>point)._c_handler))



    ######## Unary arithmetic operations ########


    def __pos__(self):
        return _wrench_from_c_value(c_deref(self._c_handler))


    def __neg__(self):
        return _wrench_from_c_value(-c_deref(self._c_handler))


    ######## Binary arithmetic operations ########


    def __add__(Wrench3D self, other):
        if not isinstance(other, Wrench3D):
            raise TypeError(f'Unsupported operand type for +: Wrench3D and {type(other).__name__}')
        return _wrench_from_c_value(c_deref(self._c_handler) + c_deref((<Wrench3D>other)._c_handler))



    def __sub__(Wrench3D self, other):
        if not isinstance(other, Wrench3D):
            raise TypeError(f'Unsupported operand type for -: Wrench3D and {type(other).__name__}')
        return _wrench_from_c_value(c_deref(self._c_handler) - c_deref((<Wrench3D>other)._c_handler))



    def __mul__(left_op, right_op):
        if isinstance(left_op, Wrench3D) and isinstance(right_op, Wrench3D):
            # Product between wrenches
            return _expr_from_c(c_deref((<Wrench3D>left_op)._c_handler) * c_deref((<Wrench3D>right_op)._c_handler))

        if not isinstance(left_op, Wrench3D) and not isinstance(right_op, Wrench3D):
            raise TypeError(f'Unsupported operand type for *: {type(left_op).__name__} and {type(right_op).__name__}')

        if isinstance(left_op, Wrench3D):
            right_op = Expr(right_op)
        else:
            left_op, right_op = right_op, Expr(left_op)

        return _wrench_from_c_value(
            (<Expr>right_op)._c_handler *\
            c_deref((<Wrench3D>left_op)._c_handler))



    def __truediv__(left_op, right_op):
        pass



    ######## Properties ########


    @property
    def force(self):
        '''
        Read only property that returns the force vector of this wrench.

        :rtype: Vector3D

        .. note::
            This calls internally to ``get_force``

            .. seealso:: :func:`get_force`

        '''
        return self.get_force()


    @property
    def moment(self):
        '''
        Read only property that returns the moment vector of this wrench.

        :rtype: Vector3D

        .. note::
            This calls internally to ``get_moment``

            .. seealso:: :func:`get_moment`

        '''
        return self.get_moment()


    @property
    def solid(self):
        '''
        Read only property that returns the solid of this wrench.

        :rtype: Solid

        .. note::
            This calls internally to ``get_solid``

            .. seealso:: :func:`get_solid`

        '''
        return self.get_solid()


    @property
    def type(self):
        '''
        Read only property that returns the type of this wrench.

        :rtype: str

        .. note::
            This calls internally to ``get_type``

            .. seealso:: :func:`get_type`

        '''
        return self.get_type()



NamedObject.register(Wrench3D)
