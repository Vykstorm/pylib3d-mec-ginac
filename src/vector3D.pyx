'''
Author: Víctor Ruiz Gómez
Description: This file contains the definition of the class Vector3D
'''


######## Class Vector ########

cdef class Vector3D(Matrix):


    ######## Attributes ########

    cdef object _owner




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

        if system is not None and not isinstance(system, _System):
            raise TypeError('system must be an instance of the class System or None')

        if isinstance(base, str):
            if system is None:
                raise TypeError('base cannot be a string if system is not given')
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
        self._owner = system


    cdef c_Matrix* _get_c_handler(self) except? NULL:
        if self._c_handler == NULL:
            raise RuntimeError
        return self._c_handler




    ######## Getters ########


    cpdef get_base(self):
        cdef c_Base* c_base = (<c_Vector3D*>self._get_c_handler()).get_Base()
        return Base(<Py_ssize_t>c_base)


    cpdef get_module(self):
        cdef c_ex c_expr = (<c_Vector3D*>self._get_c_handler()).get_module()
        return _expr_from_c(c_expr)


    cpdef get_skew(self):
        cdef c_Matrix c_skew = (<c_Vector3D*>self._get_c_handler()).skew()
        return _matrix_from_c_value(c_skew)




    ######## Setters ########


    cpdef set_base(self, base):
        if not isinstance(base, Base):
            raise TypeError('Input argument must be a Base object')

        (<c_Vector3D*>self._get_c_handler()).set_Base((<Base>base)._c_handler)




    ######## Operations ########


    def dot(self, other):
        if not isinstance(other, Vector3D):
            raise TypeError('Input argument must be a Vector3D')
        return _expr_from_c(
            c_deref(<c_Vector3D*>(<Vector3D>self)._get_c_handler()) *\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def cross(self, other):
        if not isinstance(other, Vector3D):
            raise TypeError('Input argument must be a Vector3D')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>(<Vector3D>self)._get_c_handler()) ^\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )



    ######## Arithmetic operations ########


    def __pos__(self):
        return _vector_from_c_value(c_deref(<c_Vector3D*>self._get_c_handler()))

    def __neg__(self):
        return _vector_from_c_value(-c_deref(<c_Vector3D*>self._get_c_handler()))


    def __add__(Vector3D self, other):
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for +: Vector3D and {type(other).__name__}')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>self._get_c_handler()) +\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def __sub__(Vector3D self, other):
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for -: Vector3D and {type(other).__name__}')
        return _vector_from_c_value(
            c_deref(<c_Vector3D*>self._get_c_handler()) -\
            c_deref(<c_Vector3D*>(<Vector3D>other)._get_c_handler())
        )


    def __mul__(left_op, right_op):
        if isinstance(left_op, Vector3D) and isinstance(right_op, Vector3D):
            # Dot product between vectors
            return left_op.dot(right_op)

        if not isinstance(left_op, Vector3D) and not isinstance(right_op, Vector3D):
            raise TypeError(f'Unsupported operand type for *: {type(left_op).__name__} and {type(right_op).__name__}')

        if isinstance(left_op, Vector3D):
            right_op = Expr(right_op)
        else:
            left_op, right_op = right_op, Expr(left_op)

        # TODO
        raise NotImplementedError()


    def __xor__(Vector3D self, other):
        if not isinstance(other, Vector3D):
            raise TypeError(f'Unsupported operand type for ^: Vector3D and {type(other).__name__}')
        return self.cross(other)




    ######## Properties ########


    @property
    def base(self):
        return self.get_base()

    @base.setter
    def base(self, base):
        self.set_base(base)


    @property
    def module(self):
        return self.get_module()

    @property
    def skew(self):
        return self.get_skew()

    @property
    def x(self):
        return self.get(0)

    @x.setter
    def x(self, value):
        self.set(0, value)

    @property
    def y(self):
        return self.get(1)

    @y.setter
    def y(self, value):
        self.set(1, value)

    @property
    def z(self):
        return self.get(2)

    @z.setter
    def z(self, value):
        self.set(2, value)




######## Operations (global functions) ########


def dot(v, w):
    if not isinstance(v, Vector3D) or not isinstance(w, Vector3D):
        raise TypeError('Input arguments must be Vector3D objects')
    return v.dot(w)


def cross(v, w):
    if not isinstance(v, Vector3D) or not isinstance(w, Vector3D):
        raise TypeError('Input arguments must be Vector3D objects')
    return v.cross(w)




######## Aliases for class Vector3D ########

Vec3D = Vector3D
