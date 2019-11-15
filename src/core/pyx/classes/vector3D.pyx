'''
Author: Víctor Ruiz Gómez
Description: This file contains the definition of the class Vector3D
'''




######## Helper functions ########

cdef Vector3D _vector_from_c(c_Vector3D* x):
    # Converts C++ Vector3D object to Python class Vector3D instance
    # It doesnt make a copy of the contents of the C++ Vector
    v = Vector3D()
    v._c_handler, v._owns_c_handler = x, False
    return v


cdef Vector3D _vector_from_c_value(c_Vector3D x):
    # Converts C++ Vector3D object to Python class Vector3D instance
    # It performs a copy of the contents of the given C++ Vector3D
    v = Vector3D()
    v._c_handler = new c_Vector3D(x.get_Name(), x.get(0, 0), x.get(1, 0), x.get(2, 0), x.get_Base())
    (<c_Vector3D*>v._c_handler).set_System(x.get_System())
    v._owns_c_handler = True
    return v






######## Class Vector ########

cdef class Vector3D(Matrix):
    '''
    Represents a 3D vector defined within a base. Its a matrix with three rows
    and only one column.

    .. note::
        This class is not intented to instantiated manually. Use the
        method ``System.new_vector`` instead

        .. seealso:: :func:`System.new_vector`

    '''


    ######## Attributes ########


    ######## Constructor & Destructor ########

    def __init__(self, *args, **kwargs):
        if not args and not kwargs:
            # Construction without arguments is reserved for internal purposes
            self._c_handler = NULL
            return

        # Validate & parse arguments
        if args:
            args = list(args)

            try:
                if isinstance(args[-1], (str, Base)):
                    base, values = args[-1], args[:-1]
                    if len(values) not in (0, 1, 3):
                        raise TypeError
                    if len(values) != 1:
                        if len(values) == 0:
                            values = kwargs.pop('values', (0, 0, 0))
                        args = [values, base]
                else:
                    values = args
                    if len(values) not in (1, 3):
                        raise TypeError
                    if len(values) == 3:
                        args = [values]


            except TypeError:
                raise TypeError('You must specify exactly three values for the vector components')

        values, base, system = _apply_signature(
            ['values', 'base', 'system'],
            {'values': (0, 0, 0), 'base': 'xyz', 'system': None},
            args, kwargs
        )

        if not isinstance(base, (str, Base)):
            raise TypeError('base must be an instance of the class Base or a str')

        if not isinstance(system, _System):
            raise TypeError('system must be an instance of the class System')

        if isinstance(base, str):
            base = system.get_base(base)

        values = tuple(map(Expr, values))


        # Create the underline vector object
        cdef c_ex x = (<Expr>values[0])._c_handler
        cdef c_ex y = (<Expr>values[1])._c_handler
        cdef c_ex z = (<Expr>values[2])._c_handler
        cdef c_Base* c_base = (<Base>base)._c_handler

        cdef c_Vector3D* c_vector = new c_Vector3D(b'', x, y, z, c_base)

        self._c_handler = <c_Matrix*>c_vector
        self._owns_c_handler = True
        c_vector.set_System((<_System>system)._c_handler)




    cdef c_Matrix* _get_c_handler(self) except? NULL:
        if self._c_handler == NULL:
            raise RuntimeError
        return self._c_handler




    ######## Getters ########

    cpdef get_module(self):
        '''get_module() -> Expr
        Get the module of the vector

            :Example:

            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> v = new_vector('v', a, b, c)
            >>> v.get_module()
            (a**2+b**2+c**2)**(1/2)

        :rtype: Expr

        '''
        cdef c_ex c_expr = (<c_Vector3D*>self._get_c_handler()).get_module()
        return _expr_from_c(c_expr)


    cpdef get_skew(self):
        '''get_skew() -> Matrix
        Get the skew matrix of this vector.

            :Example:

            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> v = new_vector('v', a, b, c)
            >>> v.skew
            ╭            ╮
            │  0  -c   b │
            │  c   0  -a │
            │ -b   a   0 │
            ╰            ╯

        :rtype: Matrix

        '''
        cdef c_Matrix c_skew = (<c_Vector3D*>self._get_c_handler()).skew()
        return _matrix_from_c_value(c_skew)





    ######## Setters ########




    ######## Operations ########


    cpdef in_base(self, new_base):
        '''in_base(new_base: Base) -> Vector3D
        Performs a base change operation on this vector.

        :param base: The new base
        :type base: Base

        :return: A new vector which is the same as this but with its base changed

        :rtype: Vector3D

        '''
        if not isinstance(new_base, Base):
            raise TypeError('Input argument must be a Base object')
        return _vector_from_c_value((<c_Vector3D*>self._get_c_handler()).in_Base((<Base>new_base)._c_handler))



    def dot(self, other):
        '''dot(other: Vector3D) -> Expr
        Computes the dot product of two vectors.

            :Example:

            >>> a, b = new_param('a'), new_param('b')
            >>> v = new_vector('v', a, b, 1)
            >>> w = new_vector('w', 1, b, a)
            >>> v.dot(w)
            2*a+b**2

        :rtype: Expr
        :raise TypeError: If the input argument is not a vector
        '''
        if not isinstance(other, Vector3D):
            raise TypeError('Input argument must be a Vector3D')
        return _expr_from_c(
            c_deref(<c_Vector3D*>(<Vector3D>self)._get_c_handler()) *\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def cross(self, other):
        '''cross(other: Vector3D) -> Vector3D
        Computes the cross product of two vectors.

            :Example:

            >>> a, b = new_param('a'), new_param('b')
            >>> v = new_vector('v', a, b, 1)
            >>> w = new_vector('w', 1, b, a)
            >>> v.cross(w)
            [ a*b-b  1.0-a**2  a*b-b ]
            >>> w.cross(v)
            [ -a*b+b  -1.0+a**2  -a*b+b ]

            :rtype: Vector3D
            :raise TypeError: If the input argument is not a vector
        '''
        if not isinstance(other, Vector3D):
            raise TypeError('Input argument must be a Vector3D')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>(<Vector3D>self)._get_c_handler()) ^\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )



    def normalize(self):
        '''normalize() -> Vector3D
        Get this vector normalized

            :Example:
            
            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> v = new_vector('v', a, b, c)
            >>> v.normalize()
            [
            (b**2+c**2+a**2)**(-1/2)*a,
            (b**2+c**2+a**2)**(-1/2)*b,
            c*(b**2+c**2+a**2)**(-1/2)
            ]

        :rtype: Vector3D

        :raises ZeroDivisionError: If the module of this vector is zero length

        '''
        module = self.get_module()
        if module == 0:
            raise ZeroDivisionError('You cant normalize a vector with module zero')
        return self / module






    ######## Arithmetic operations ########


    def __pos__(self):
        '''
        Performs the unary positive operation on this vector. The result is another
        vector.
        :rtype: Vector3D
        '''
        return _vector_from_c_value(c_deref(<c_Vector3D*>self._get_c_handler()))

    def __neg__(self):
        '''
        Get this vector negated.
        :rtype: Vector3D
        '''
        return _vector_from_c_value(-c_deref(<c_Vector3D*>self._get_c_handler()))


    def __add__(Vector3D self, other):
        '''
        Perform the sum operation between two vectors. The result is another vector.
        :rtype: Vector3D
        '''
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for +: Vector3D and {type(other).__name__}')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>self._get_c_handler()) +\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def __sub__(Vector3D self, other):
        '''
        Perform the subtraction operation between two vectors. The result is another vector.
        :rtype: Vector3D
        '''
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for -: Vector3D and {type(other).__name__}')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>self._get_c_handler()) -\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def __mul__(left_op, right_op):
        '''
        Perform the product operation between two vectors or a vector and a expression.
        If the product is between two vectors, computes the dot product between them and the
        result is a expression.
        Otherwise, computes the scalar product of the vector with the given expression and
        the result is a vector.

        .. seealso:: dot
        '''
        if isinstance(left_op, Vector3D) and isinstance(right_op, Vector3D):
            # Dot product between vectors
            return left_op.dot(right_op)

        if not isinstance(left_op, Vector3D) and not isinstance(right_op, Vector3D):
            raise TypeError(f'Unsupported operand type for *: {type(left_op).__name__} and {type(right_op).__name__}')

        if type(left_op) == Matrix or type(right_op) == Matrix:
            return Matrix.__mul__(left_op, right_op)

        if isinstance(left_op, Vector3D):
            right_op = Expr(right_op)
        else:
            left_op, right_op = right_op, Expr(left_op)

        return _vector_from_c_value(
            (<Expr>right_op)._c_handler *\
            c_deref(<c_Vector3D*>((<Vector3D>left_op)._get_c_handler()))
        )



    def __truediv__(Vector3D self, other):
        '''
        Performs the scalar product between this vector and the given expression inverted.
        The result is also a vector.
        :rtype: Vector3D
        '''
        if not isinstance(other, Expr):
            other = Expr(other)
        inverted_expr = 1 / other

        return _vector_from_c_value(
            (<Expr>inverted_expr)._c_handler *\
            c_deref(<c_Vector3D*>(self._get_c_handler()))
        )



    def __xor__(Vector3D self, other):
        '''
        Performs the cross product of this vector with another.
        :rtype: Vector3D
        .. sealso:: cross
        '''
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for ^: Vector3D and {type(other).__name__}')
        return self.cross(other)




    ######## Properties ########

    @property
    def module(self):
        '''
        Only read property that returns the module of this vector.

        :rtype: Expr

        .. note:: This calls ``get_module`` internally.

            .. seealso::
                :func:`get_module`

        '''
        return self.get_module()


    @property
    def normalized(self):
        '''
        Only read property that returns this vector normalized.

        :rtype: Vector3D

        .. note:: This calls to ``normalize`` insternally.

            .. seealso:: :func:`normalize`

        '''
        return self.normalize()




    @property
    def skew(self):
        '''
        Only read property that returns the skew matrix of this vector.

        :rtype: Matrix

        .. note:: This calls ``get_skew`` internally.

            .. seealso:: get_skew

        '''
        return self.get_skew()

    @property
    def x(self):
        '''
        Returns the first component of the vector. You can also use this property
        to assign a new value to it.

        :rtype: Expr

        '''
        return self.get(0)

    @x.setter
    def x(self, value):
        self.set(0, value)

    @property
    def y(self):
        '''
        Returns the second component of the vector. You can also use this property
        to assign a new value to it.

        :rtype: Expr

        '''
        return self.get(1)

    @y.setter
    def y(self, value):
        self.set(1, value)

    @property
    def z(self):
        '''
        Returns the third component of the vector. You can also use this property
        to assign a new value to it.

        :rtype: Expr

        '''
        return self.get(2)

    @z.setter
    def z(self, value):
        self.set(2, value)





GeometricObject.register(Vector3D)




######## Operations (global functions) ########


def dot(v, w):
    '''dot(v: Vector3D, w: Vector3D) -> Expr
    Computes the dot product of two vectors.

    :rtype: Expr
    :raise TypeError: If the input arguments are not vectors

        :Example:

        >>> a, b = new_param('a'), new_param('b')
        >>> v = new_vector('v', a, b, 1)
        >>> w = new_vector('w', 1, b, a)
        >>> dot(v, w)
        2*a+b**2

    .. note:: Its equivalent to v.dot(w) or w.dot(v)
    .. seealso:: Vector3D.dot
    '''
    if not isinstance(v, Vector3D) or not isinstance(w, Vector3D):
        raise TypeError('Input arguments must be Vector3D objects')
    return v.dot(w)


def cross(v, w):
    '''cross(v: Vector3D, w: Vector3D) -> Vector3D
    Computes the cross product between two vectors.

    :rtype: Vector3D
    :raise TypeError: If the input arguments are not vectors

        :Example:

        >>> a, b = new_param('a'), new_param('b')
        >>> v = new_vector('v', a, b, 1)
        >>> w = new_vector('w', 1, b, a)
        >>> cross(v, w)
        [ a*b-b  1.0-a**2  a*b-b ]
        >>> cross(w, v)
        [ -a*b+b  -1.0+a**2  -a*b+b ]


    .. note:: Its equivalent to v.cross(w)
    .. seealso:: Vector3D.cross
    '''
    if not isinstance(v, Vector3D) or not isinstance(w, Vector3D):
        raise TypeError('Input arguments must be Vector3D objects')
    return v.cross(w)




######## Aliases for class Vector3D ########

Vec3D = Vector3D
