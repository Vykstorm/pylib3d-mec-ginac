'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Matrix
'''



######## Helper functions ########

cdef Matrix _matrix_from_c(c_Matrix* x):
    # Converts C++ Matrix object to Python class Matrix instance
    # (it doesnt make a copy, only stores the given pointer to the C++ matrix)
    mat = Matrix()
    mat._c_handler, mat._owns_c_handler = x, False
    return mat



cdef Matrix _matrix_from_c_value(c_Matrix x):
    # Converts C++ Matrix object to Python class Matrix instance
    # It performs a copy of the given C++ matrix
    mat = Matrix()
    cdef c_Matrix* c_mat = new c_Matrix(x.get_matrix())
    c_mat.set_name(x.get_name())

    mat._c_handler, mat._owns_c_handler = c_mat, True
    return mat





######## Class Matrix ########

cdef class Matrix(Object):
    '''
    Represents a 2D matrix of symbolic expressions of arbitrary sizes.
    '''

    ######## C Attributes ########


    cdef c_Matrix* _c_handler
    cdef bint _owns_c_handler



    ######## Constructor ########


    def __init__(self, values=None, shape=None):
        # Validate input arguments
        if values is None and shape is None:
            # Matrix 1x1 with a zero initialized by default
            self._c_handler = NULL
            return


        if shape is None and values is not None and not isinstance(values, (range, list, tuple, set, frozenset)):
            # Check if values is a numpy array
            try:
                import numpy as np
                if isinstance(values, np.ndarray):
                    dtype = values.dtype
                    if dtype not in (np.float64, np.int64):
                        dtype = np.float64
                    m = np.array(values, dtype=dtype, copy=False, order='C')
                    # Check numpy array dimensions
                    if m.ndim not in (1, 2):
                        raise ValueError('Input numpy array must have one or two dimensions')
                    shape = m.shape if m.ndim == 2 else (1, m.shape[0])
                    values = m.tolist()

            except ImportError:
                pass



        # Validate & parse shape argument
        if shape is not None:
            if not isinstance(shape, (Iterable, int)):
                raise TypeError('Matrix shape must be an integer or iterable object')
            if isinstance(shape, int):
                shape = (shape, shape)
            else:
                shape = tuple(shape)
                if len(shape) == 1:
                    shape *= 2

            if len(shape) != 2 or not isinstance(shape[0], int) or not isinstance(shape[1], int):
                raise ValueError('Matrix shape must be a pair of numbers (num.rows x num.cols)')
            if shape[0] <= 0 or shape[1] <= 0:
                raise ValueError('Matrix dimensions must be numbers greater than zero')


        if values is not None:
            # values must be a matrix or an iterable
            if not isinstance(values, Iterable):
                raise TypeError(f'Matrix values must be an iterable object')

            values = tuple(values)
            if len(values) == 0:
                raise ValueError(f'You must specify at least one value')
            if isinstance(values[0], Iterable):
                if not all(map(lambda x: isinstance(x, Iterable), values[1:])):
                    raise TypeError

                # value is a list of sublists with expressions
                values = tuple(map(tuple, values))

                # check that all subslits have the same size
                if not all(map(lambda x: len(x) == len(values[0]), values[1:])):
                    raise ValueError('All sublists must have the same size')

                if shape is None:
                    # compute shape from values
                    shape = (len(values), len(values[0]))
                values = tuple(chain.from_iterable(values))
                if len(values) == 0:
                    raise ValueError('You must specify at least one value')
            else:
                # values is a list of expressions
                if any(map(lambda x: isinstance(x, Iterable), values[1:])):
                    raise TypeError
                if shape is None:
                    # compute shape from values
                    shape = (1, len(values))
                if len(values) == 0:
                    raise ValueError('You must specify at least one value')

            if shape[0] * shape[1] != len(values):
                raise ValueError(f'Inconsistent number of values ({len(values)}) and shape ({shape[0]} x {shape[1]})')


        # set matrix shape
        self._c_handler = new c_Matrix(shape[0], shape[1])
        self._owns_c_handler = True

        if values is not None:
            # Assign values to the matrix
            for k, value in enumerate(map(Expr, values)):
                i, j = k // shape[1], k % shape[1]
                self._c_handler.set(i, j, (<Expr>value)._c_handler)



    def __dealloc__(self):
        if self._c_handler != NULL and self._owns_c_handler:
            del self._c_handler


    cdef c_Matrix* _get_c_handler(self) except? NULL:
        if self._c_handler == NULL:
            self._c_handler = new c_Matrix(1, 1)
            self._owns_c_handler = True
        return self._c_handler



    ######## Getters ########


    def get_shape(self):
        '''
        Get the shape of this matrix.
        :returns: A tuple with two numbers (number of rows and columns)
        :rtype: Tuple[int, int]
        '''
        return self._get_c_handler().rows(), self._get_c_handler().cols()


    def get_num_rows(self):
        '''
        Get the number of rows of this matrix
        :rtype: int
        '''
        return self._get_c_handler().rows()


    def get_num_cols(self):
        '''
        Get the number of columns of this matrix
        :rtype: int
        '''
        return self._get_c_handler().cols()


    def get_size(self):
        '''
        Get the total number of items of this matrix (number of rows x number of columns)
        :rtype: int
        '''
        return self.get_num_rows() * self.get_num_cols()


    def __len__(self):
        '''
        Alias of get_size()
        '''
        return self.get_size()


    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            pass

        if key not in ('get_module', 'get_skew', 'module', 'skew') or type(self) != Matrix:
            raise AttributeError(f'"Matrix" object has no attribute "{key}"')
        if self.get_size() != 3:
            raise AttributeError(f'Only 1x3 or 3x1 matrices have access to "{key}" method or property')

        values = self.get_values()
        cdef c_ex x = (<Expr>values[0])._c_handler
        cdef c_ex y = (<Expr>values[1])._c_handler
        cdef c_ex z = (<Expr>values[2])._c_handler
        return getattr(_vector_from_c_value(c_Vector3D(b'', x, y, z, NULL)), key)


    def __dir__(self):
        if self.get_size() != 3 or type(self) != Matrix:
            return super().__dir__()
        return super().__dir__() + ['get_module', 'get_skew', 'module', 'skew']




    ######## Accessing values ########


    def _parse_row_index(self, i):
        if not isinstance(i, int):
            raise TypeError('Matrix indices must be numbers')
        n = self.get_num_rows()
        if i < 0:
            i += n
        if i not in range(0, n):
            raise IndexError('Row index out of bounds')
        return i

    def _parse_col_index(self, j):
        if not isinstance(j, int):
            raise TypeError('Matrix indices must be numbers')
        m = self.get_num_cols()
        if j < 0:
            j += m
        if j not in range(0, m):
            raise IndexError('Column index out of bounds')
        return j


    def _parse_indices(self, i, j):
        return self._parse_row_index(i), self._parse_col_index(j)



    def get_values(self):
        '''
        Get all the items of this matrix
        :returns: A list containing all the items of this matrix, where the item
        at ith row and jth column will be located at i*num_cols + j index in that list
        :rtype: List[Expr]
        '''
        return list(self)



    def get(self, i, j=None):
        '''
        Get an element of this matrix.
        If two arguments are passed, they will be interpreted as the row and column
        indices of the element to fetch:

            :Example:

            m = new_matrix('m', [[0, 1], [2, 3]])
            >> matrix.get(0, 0)
            0
            >> matrix.get(1, 1)
            3

        You can pass also one index value if the matrix has only one row or
        column.
        The returned value will be the element at ith column or ith row respectively

            :Example:

            >> m = new_matrix('m', [1, 3, 5, 7])
            >> m.shape
            (1, 4)
            >> m.get(2)
            5
            >> m.transpose().get(3)
            7

        Indices can also be negative values:

            :Example:

            >> m = new_matrix('m', [[1, 0, 0], [0, 2, 0], [0, 0, 3]])
            >> m.get(2, 2)
            3
            >> m.get(-1, -1)
            3

        :raise TypeError: If the indices passed are not valid
        :raise IndexError: If the indices are out of bounds
        '''
        if j is None:
            n, m = self.get_shape()
            if n > 1 and m > 1:
                raise TypeError('Missing column index')
            j = 0
            if n == 1:
                i, j = j, i

        i, j = self._parse_indices(i, j)
        return _expr_from_c(self._get_c_handler().get(i, j))



    def __getitem__(self, index):
        '''
        Implements the indexing operator. You can use it to fetch an element of
        the matrix by index.

            :Example:

            >> m = new_matrix('m', [[1, 0, 0], [0, 2, 0], [0, 0, 3]])
            >> m[1, 1]
            2

        .. seealso:: get
        '''
        if isinstance(index, tuple):
            if len(index) not in (1, 2):
                raise TypeError('Wrong number of indices')
            return self.get(*index)
        return self.get(index)





    ######## Changing values ########


    def set(self, i, *args):
        '''
        Change the value of an element in the matrix.
        The arguments must be the indices of the element to change followed
        by its new value

            :Example:

            >> m = new_matrix('m', [[0, 1], [2, 3]])
            >> m.get(1, 1)
            3
            >> m.set(1, 1, 4)
            >> m.get(1, 1)
            4

        You could also specify just one index if the matrix has only one row or
        column.
        The element to be changed will be at ith column or ith row respectively

            :Example:

            >> m = new_matrix('m', [1, 2, 3, 4])
            >> m.get(2)
            3
            >> m.set(2, 0)
            >> m.get(2)
            0

        And indices can also be negative:

            :Example:

            >> m = new_matrix('m', [[1, 2], [3, 4]])
            >> m.set(-1, -1, 0)
            >> m.get(1, 1)
            4


        :raise TypeError: If the given indices or the new value for the element are not valid
        :raise IndexError: If the indices are out of bounds
        .. sealso:: get

        '''
        if len(args) == 0:
            raise TypeError('Missing column index')
        if len(args) == 1:
            j, value = None, args[0]
        else:
            if len(args) > 2:
                raise TypeError('Wrong number of indices')
            j, value = args[0:2]

        if j is None:
            n, m = self.get_shape()
            if n > 1 and m > 1:
                raise TypeError('Missing column index')
            j = 0
            if n == 1:
                i, j = j, i

        i, j = self._parse_indices(i, j)
        if not isinstance(value, Expr):
            value = Expr(value)
        self._get_c_handler().set(i, j, (<Expr>value)._c_handler)



    def __setitem__(self, index, value):
        '''
        Implements the assignment indexing operator. You can use it to change
        the value of an specific element in the matrix.

            :Example:

            >> m = new_matrix('m', [[1, 2], [3, 4]])
            >> m[0, 1] = 0
            >> m.get(0, 1)
            0

        .. seealso:: set
        '''
        if isinstance(index, tuple):
            if len(index) != 2:
                raise TypeError('Wrong number of indices')
            i, j = index
            self.set(i, j, value)
        else:
            self.set(index, value)



    ######## Iteration ########


    def __iter__(self):
        '''
        This metamethod allow matrices to be iterated efficiently
        The returned iterator yields all the elements of this matrix

            :Example:

            >> m = new_matrix('m', [[0, 1], [2, 3]])
            >> [pow(el, 2)+1 for el in m]
            [1, 2, 5, 10]

            >> list(m)
            [0, 1, 2, 3]
        '''
        n, m = self.get_shape()
        for i in range(0, n):
            for j in range(0, m):
                yield _expr_from_c(self._get_c_handler().get(i, j))


    def __reversed__(self):
        '''
        Same as __iter__ but returns the elements in reversed order.

        ..seealso:: __iter__
        '''
        n, m = self.get_shape()
        for i in reversed(range(0, n)):
            for j in reversed(range(0, m)):
                yield _expr_from_c(self._get_c_handler().get(i, j))



    ######## Arithmetic operations ########


    def __pos__(self):
        '''
        Get a matrix with their elements are the result of a unary positive operation
        of the elements of this matrix.
        :rtype: Matrix
        '''
        return _matrix_from_c_value(c_deref(self._get_c_handler()))

    def __neg__(self):
        '''
        Get a matrix with the elements of this one negated.
        :rtype: Matrix
        '''
        return _matrix_from_c_value(-c_deref(self._get_c_handler()))


    def __add__(Matrix self, other):
        '''
        Performs the sum operation between two matrices. The result
        is also a matrix.
        :rtype: Matrix
        :raise TypeError: If the operands are not matrices
        '''
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operand type for +: Matrix and {type(other).__name__}')
        return _matrix_from_c_value(c_deref(self._get_c_handler()) + c_deref((<Matrix>other)._get_c_handler()))


    def __sub__(Matrix self, other):
        '''
        Performs the subtraction operation between two matrices. The result
        is also a matrix.
        :rtype: Matrix
        :raise TypeError: If the operands are not matrices
        '''
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operand type for -: Matrix and {type(other).__name__}')
        return _matrix_from_c_value(c_deref(self._get_c_handler()) - c_deref((<Matrix>other)._get_c_handler()))


    def __mul__(left_op, right_op):
        '''
        If both operands are matrices, performs the matrix product.
        If one operand is a matrix and the other is an expression, performs
        the scalar product (each element is multiplied by the given expression).

        In both cases, the result is another matrix object.

        :rtype: Matrix
        :raises TypeError: If the input operands are not either two matrices or a matrix
            and a expression.
        '''
        if isinstance(left_op, Matrix) and isinstance(right_op, Matrix):
            return _matrix_from_c_value(
                c_deref((<Matrix>left_op)._get_c_handler()) * c_deref((<Matrix>right_op)._get_c_handler())
            )

        if not isinstance(left_op, Matrix) and not isinstance(right_op, Matrix):
            raise TypeError(f'Unsupported operand type for *: {type(left_op).__name__} and {type(right_op).__name__}')

        if isinstance(left_op, Matrix):
            right_op = Expr(right_op)
        else:
            left_op, right_op = right_op, Expr(left_op)
        return _matrix_from_c_value(c_deref((<Matrix>left_op)._get_c_handler()) * (<Expr>right_op)._c_handler)



    def __truediv__(Matrix self, other):
        '''
        Perform the scalar division operation. Elements of the matrix are divided by
        the given expression (second operand).

        :rtype: Matrix
        .. sealso:: __mul__
        '''
        if not isinstance(other, Expr):
            other = Expr(other)
        inverted = 1 / other
        return _matrix_from_c_value(c_deref(self._get_c_handler()) * (<Expr>inverted)._c_handler)





    ######## Misc operations ########


    cpdef transpose(self):
        '''
        Tranpose this matrix
        :returns: Returns this matrix transposed
        '''
        cdef c_Matrix c_mat = self._get_c_handler().transpose()
        return _matrix_from_c_value(c_mat)


    def get_transposed(self):
        '''
        Alias of transpose method
        .. seealso:: transpose
        '''
        return self.transpose()





    ######## Properties ########


    @property
    def shape(self):
        '''
        Read only property that returns the shape of this matrix
        :rtype: Tuple[int, int]
        '''
        return self.get_shape()

    @property
    def num_rows(self):
        '''
        Read only property that returns the number of rows of this matrix
        :rtype: int
        '''
        return self.get_num_rows()

    @property
    def num_cols(self):
        '''
        Read only property that returns the number of columns of this matrix
        :rtype: int
        '''
        return self.get_num_cols()

    @property
    def size(self):
        '''
        Read only property that returns the total number of items on this matrix
        :rtype: int
        '''
        return self.get_size()


    @property
    def T(self):
        '''
        Read only property that returns the transposed matrix
        :rtype: Matrix
        '''
        return self.transpose()

    @property
    def transposed(self):
        '''
        Read only property that returns the transposed matrix
        :rtype: Matrix
        '''
        return self.transpose()


    @property
    def values(self):
        '''
        Read only property that returns all the items of this matrix as a regular list
        :rtype: List[Expr]
        '''
        return self.get_values()





NamedObject.register(Matrix)
LatexRenderable.register(Matrix)