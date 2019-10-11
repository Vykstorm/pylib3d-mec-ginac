'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Tensor3D
'''



######## Helper functions ########


cdef Tensor3D _tensor_from_c(c_Tensor3D* x):
    # Converts C++ Tensor3D object to Python class Tensor3D instance
    # It doesnt make a copy of the contents of the C++ tensor
    tensor = Tensor3D()
    tensor._c_handler, tensor._owns_c_handler = x, False
    return tensor



cdef Tensor3D _tensor_from_c_value(c_Tensor3D x):
    # Convert C++ Tensor3D object to Python class Tensor3D instance
    # It perform a copy of the contents of the given C++ Vector3D
    tensor = Tensor3D()
    tensor._c_handler = new c_Tensor3D(<c_Matrix>x, x.get_Base(), x.get_System())
    tensor._c_handler.set_name(x.get_name())
    tensor._owns_c_handler = True
    return tensor






######## Class Tensor3D ########

cdef class Tensor3D(Matrix):

    ######## Constructor ########

    def __init__(self, values=None, base=None, system=None):
        if values is None and base is None and system is None:
            # Construct without arguments is reserved for internal implementation purposes
            self._c_handler = NULL
            return

        if not isinstance(system, _System):
            raise TypeError(f'system must be a valid System object')

        if not isinstance(base, Base):
            base = system.get_base(base)

        values = Matrix(shape=(3, 3), values=list(values))


        # Call matrix initializer
        self._c_handler = new c_Tensor3D(
            c_deref((<Matrix>values)._get_c_handler()),
            (<Base>base)._c_handler,
            (<_System>system)._c_handler
        )
        self._owns_c_handler = True



    cdef c_Matrix* _get_c_handler(self) except? NULL:
        if self._c_handler == NULL:
            raise RuntimeError
        return self._c_handler



    ######## Getters ########


    ######## Operations ########


    cpdef in_base(self, new_base):
        '''in_base(new_base: Base) -> Tensor3D
        Performs a base change operation on this tensor.
        :param Base base: The new base
        :return: A new tensor which is the same as this but with its base changed
        :rtype: Tensor3D
        '''
        if not isinstance(new_base, Base):
            raise TypeError('Input argument must be a Base object')

        return _tensor_from_c_value((<c_Tensor3D*>self._get_c_handler()).in_Base((<Base>new_base)._c_handler))




    ######## Unary arithmetic operations ########


    def __neg__(self):
        '''
        Returns this tensor negated.
        '''
        return _tensor_from_c_value(
            Expr(-1)._c_handler *\
            c_deref(<c_Tensor3D*>self._get_c_handler())
        )


    def __pos__(self):
        '''
        Perform the unary positive operation on this tensor. The result is another
        tensor.
        '''
        return _tensor_from_c_value(c_deref(<c_Tensor3D*>self._get_c_handler()))




    ######## Binary arithmetic operations ########


    def __add__(Tensor3D self, other):
        '''
        Performs the sum operation between two tensors. The result is also a
        tensor.
        '''
        if not isinstance(other, Tensor3D):
            raise TypeError(f'Unsupported operand type for +: Tensor3D and {type(other).__name__}')

        return _tensor_from_c_value(
            c_deref(<c_Tensor3D*>self._get_c_handler()) +\
            c_deref(<c_Tensor3D*>(<Tensor3D>other)._get_c_handler())
        )


    def __sub__(Tensor3D self, other):
        '''
        Performs the subtraction operation between two tensors. The result is also
        a tensor.
        '''
        if not isinstance(other, Tensor3D):
            raise TypeError(f'Unsupported operand type for -: Tensor3D and {type(other).__name__}')

        return _tensor_from_c_value(
            c_deref(<c_Tensor3D*>self._get_c_handler()) -\
            c_deref(<c_Tensor3D*>(<Tensor3D>other)._get_c_handler())
        )


    def __mul__(left_op, right_op):
        '''
        Performs the product operation between two tensors, a tensor and vector or
        a tensor and a expression.
        * If both operands are tensors, the result is a tensor
        * If the first operand is a tensor and the second a vector, the result is a new
            vector
        * If one of the operands is a tensor and the other is an expression, perform
            the scalar product between them. The result is also a tensor.
        '''
        if isinstance(left_op, Tensor3D) and isinstance(right_op, Tensor3D):
            return _tensor_from_c_value(
                c_deref(<c_Tensor3D*>(<Tensor3D>left_op)._get_c_handler()) *\
                c_deref(<c_Tensor3D*>(<Tensor3D>right_op)._get_c_handler())
            )

        if not isinstance(left_op, Tensor3D) and not isinstance(right_op, Tensor3D):
            raise TypeError(f'Unsupported operand type for *: {type(left_op).__name__} and {type(right_op).__name__}')

        if isinstance(right_op, Vector3D):
            return _vector_from_c_value(
                c_deref(<c_Tensor3D*>(<Tensor3D>left_op)._get_c_handler()) *\
                c_deref(<c_Vector3D*>(<Vector3D>right_op)._get_c_handler())
            )

        if not isinstance(left_op, Tensor3D):
            left_op, right_op = right_op, left_op


        right_op = Expr(right_op)
        return _tensor_from_c_value(
            (<Expr>right_op)._c_handler *\
            c_deref(<c_Tensor3D*>(<Tensor3D>left_op)._get_c_handler())
        )


    def __truediv__(Tensor3D self, other):
        '''
        Performs the division operation between this tensor and a expression.
        The result is another expression.
        '''
        if not isinstance(other, Expr):
            expr = Expr(other)
        inverted_expr = 1 / expr

        return _tensor_from_c_value(
            (<Expr>inverted_expr)._c_handler *\
            c_deref(<c_Tensor3D*>(self._get_c_handler()))
        )



    ######## Properties ########










GeometricObject.register(Tensor3D)
