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
    cdef c_Matrix* c_mat = new c_Matrix()
    c_mat.set_matrix(x.get_matrix())
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

        if shape is None and isinstance(values, Matrix):
            # Matrix as a copy of another one
            self._c_handler = new c_Matrix((<Matrix>values)._get_c_handler().get_matrix())
            self._owns_c_handler = True
            return


        if shape is None and values is not None and not isinstance(values, (range, list, tuple, set, frozenset)):
            # Check if values is a numpy array
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




    @staticmethod
    def block(n, m, *args):
        '''block(n: int, m: int, ...) -> Matrix
        Creates a new matrix by merging a list of matrices together.

            :Example:

            >>> a = new_matrix('a', [[1, 2], [3, 4]])
            >>> b = new_matrix('b', [[5, 6], [7, 8]])
            >>> a
            ╭      ╮
            │ 1  2 │
            │ 3  4 │
            ╰      ╯
            >>> b
            ╭      ╮
            │ 5  6 │
            │ 7  8 │
            ╰      ╯
            >>> Matrix.block(1, 2, a, b)
            ╭            ╮
            │ 1  2  5  6 │
            │ 3  4  7  8 │
            ╰            ╯
            >>> Matrix.block(2, 1, a, b)
            ╭      ╮
            │ 1  2 │
            │ 3  4 │
            │ 5  6 │
            │ 7  8 │
            ╰      ╯
            >>> Matrix.block(2, 2, a, b, a, b)
            ╭            ╮
            │ 1  2  5  6 │
            │ 3  4  7  8 │
            │ 1  2  5  6 │
            │ 3  4  7  8 │
            ╰            ╯


        :param n: The number of blocks at the row dimension. Must be a value greater
            than zero
        :type n: int

        :param m: The number of blocks at the column dimension. Must be a value greater
            than zero.
        :type m: int

        :param args: The matrices to be merged:

            * The number of matrices specified must be equal to ``n*m``
            * All matrices in the same row block must have the same number of rows
            * All matrices in the same column block must have the same number of columns

        :rtype: Matrix


        '''
        if not isinstance(n, int) or n <= 0:
            raise TypeError('n must be a number greater than zero')

        if not isinstance(m, int) or m <= 0:
            raise TypeError('m must be a number greater than zero')

        if not all(map(lambda arg: isinstance(arg, Matrix), args)):
            raise TypeError('All input values passed as varadic arguments must be matrices')

        if n*m != len(args):
            raise ValueError('Inconsistent number of varadic arguments passed')

        # All matrices layed out on the same "row" must have the same number of rows
        if m > 1:
            for i in range(0, n):
                if len(frozenset(map(attrgetter('num_rows'), args[i*m:(i+1)*m]))) != 1:
                    raise TypeError('All matrices in a row must have the same number of rows')

        if n > 1:
            for j in range(0, m):
                if len(frozenset(map(attrgetter('num_cols'), [args[i*m+j] for i in range(0, n)]))) != 1:
                    raise TypeError('All matrices in a column must have the same number of rows')


        cdef c_vector[c_Matrix*] c_blocks
        c_blocks.reserve(len(args))
        for arg in args:
            c_blocks.push_back((<Matrix>arg)._get_c_handler())

        cdef c_Matrix* c_matrix = new c_Matrix(n, m, c_blocks)

        m = Matrix()
        (<Matrix>m)._c_handler = c_matrix
        (<Matrix>m)._owns_c_handler = True
        return m





    ######## Getters ########


    def get_shape(self):
        '''get_shape() -> Tuple[int, int]
        Get the shape of this matrix.

        :return: A tuple with two numbers (number of rows and columns)
        :rtype: Tuple[int, int]

        .. seealso:: :func:`get_num_rows` :func:`get_num_cols`
        '''
        return self._get_c_handler().rows(), self._get_c_handler().cols()


    def get_num_rows(self):
        '''get_num_rows() -> int
        Get the number of rows of this matrix

        :rtype: int

        '''
        return self._get_c_handler().rows()


    def get_num_cols(self):
        '''get_num_cols() -> int
        Get the number of columns of this matrix

        :rtype: int

        '''
        return self._get_c_handler().cols()


    def get_size(self):
        '''get_size() -> int
        Get the total number of items of this matrix (number of rows x number of columns)

        :rtype: int

        .. seealso:: :func:`get_num_rows` :func:`get_num_cols`

        '''
        return self.get_num_rows() * self.get_num_cols()


    def __len__(self):
        '''
        You can use the built-in method len to get the size of the matrix:

            :Example:

            >>> m = new_matrix('m', shape=[3,3])
            >>> m.get_size()
            9
            >>> len(m)
            9

        .. seealso:: :func:`get_size`
        '''
        return self.get_size()


    def __getattr__(self, key):
        try:
            return super().__getattr__(key)
        except AttributeError:
            pass

        if key not in ('get_module', 'get_skew', 'normalize', 'module', 'skew', 'normalized') or type(self) != Matrix:
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
        return super().__dir__() + ['get_module', 'get_skew', 'normalize', 'module', 'skew', 'normalized']




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
        '''get_values() -> List[Expr]
        Get all the items of this matrix

        :returns: A list containing all the items of this matrix, where the item
            at ith row and jth column will be located at i*num_cols + j index in that list

        :rtype: List[Expr]

        '''
        return list(self)



    cpdef are_all_values_symbols(self, _System sys):
        '''are_all_values_symbols(system: System) -> bool
        This function checks that all items of this matrix are symbolic expressions composed
        by a single numeric variable defined within the given system.
        '''
        for item in self:
            if not item.is_symbol(sys):
                return False
        return True



    cpdef get_values_as_symbols(self, _System sys):
        '''get_values_as_symbols() -> List[NumericSymbol]
        This function returns a list of all the items of this matrix converted to numeric symbols
        defined within the given system.

        :raises ValueError: If one of the symbolic expressions of this matrix is not composed only
            by one numeric symbol defined within the given system.
        '''
        return list(map(methodcaller('to_symbol'), self))






    def get(self, i, j=None):
        '''get(i: int[, j: int]) -> Expr
        Get an element of this matrix.
        If two arguments are passed, they will be interpreted as the row and column
        indices of the element to fetch:

            :Example:

            >>> m = new_matrix('m', [[0, 1], [2, 3]])
            >>> m
            ╭      ╮
            │ 0  1 │
            │ 2  3 │
            ╰      ╯
            >>> matrix.get(0, 0)
            0
            >>> matrix.get(1, 1)
            3

        You can pass also one index value if the matrix has only one row or
        column.
        The returned value will be the element at ith column or ith row respectively

            :Example:

            >>> m = new_matrix('m', [1, 3, 5, 7])
            >>> m
            [ 1  3  5  7 ]
            >>> m.get(2)
            5
            >>> m.transpose().get(3)
            7

        Indices can also be negative values:

            :Example:

            >>> m = new_matrix('m', [[1, 0, 0], [0, 2, 0], [0, 0, 3]])
            ╭         ╮
            │ 1  0  0 │
            │ 0  2  0 │
            │ 0  0  3 │
            ╰         ╯
            >>> m.get(2, 2)
            3
            >>> m.get(-1, -1)
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

            >>> m = new_matrix('m', [[1, 0, 0], [0, 2, 0], [0, 0, 3]])
            >>> m
            ╭         ╮
            │ 1  0  0 │
            │ 0  2  0 │
            │ 0  0  3 │
            ╰         ╯
            >>> m[1, 1]
            2

        .. note:: It calls internally to the method ``get``

            .. seealso:: :func:`get`
        '''
        if isinstance(index, tuple):
            if len(index) not in (1, 2):
                raise TypeError('Wrong number of indices')
            return self.get(*index)
        return self.get(index)





    ######## Changing values ########


    def set(self, i, *args):
        '''set(i: int[, j: int], value: Expr)
        Change the value of an element in the matrix.
        The arguments must be the indices of the element to change followed
        by its new value

            :Example:

            >>> m = new_matrix('m', [[0, 1], [2, 3]])
            >>> m
            ╭      ╮
            │ 0  1 │
            │ 2  3 │
            ╰      ╯
            >>> m.set(1, 1, 4)
            >>> m
            ╭      ╮
            │ 0  1 │
            │ 2  4 │
            ╰      ╯

        You could also specify just one index if the matrix has only one row or
        column.
        The element to be changed will be at ith column or row respectively

            :Example:

            >>> m = new_matrix('m', [1, 2, 3, 4])
            >>> m
            [ 1  2  3  4 ]
            >>> m.set(2, 0)
            >>> m
            [ 1  2  0  4 ]

        And indices can also be negative:

            :Example:

            >>> m = new_matrix('m', [[1, 2], [3, 4]])
            >>> m
            ╭      ╮
            │ 1  2 │
            │ 3  4 │
            ╰      ╯
            >>> m.set(-1, -1, 0)
            ╭      ╮
            │ 1  2 │
            │ 3  0 │
            ╰      ╯


        :raise TypeError: If the given indices or the new value for the element are not valid
        :raise IndexError: If the indices are out of bounds

        .. seealso:: :func:`get`

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

            >>> m = new_matrix('m', [[1, 2], [3, 4]])
            >>> m
            ╭      ╮
            │ 1  2 │
            │ 3  4 │
            ╰      ╯
            >>> m[0, 1] = 0
            >>> m
            ╭      ╮
            │ 1  0 │
            │ 3  4 │
            ╰      ╯

        .. note:: It used the method ``set`` internally.

            .. seealso:: :func:`set`

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

            >>> m = new_matrix('m', [[0, 1], [2, 3]])
            >>> [pow(el, 2)+1 for el in m]
            [1, 2, 5, 10]
            >>> list(m)
            [0, 1, 2, 3]
        '''
        n, m = self.get_shape()
        for i in range(0, n):
            for j in range(0, m):
                yield _expr_from_c(self._get_c_handler().get(i, j))


    def __reversed__(self):
        '''
        Same as __iter__ but returns the elements in reversed order.

        :Example:

        >>> m = new_matrix('m', [[0, 1], [2, 3]])
        >>> [pow(el, 2)+1 for el in reversed(m)]
        [10, 5, 2, 1]
        >>> list(reversed(m))
        [3, 2, 1, 0]

        .. seealso:: :func:`__iter__`

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
            # number of columns of the first operand must match the number of rows of the second one
            if left_op.num_cols != right_op.num_rows:
                raise TypeError(f'Matrices with shapes {left_op.shape} and {right_op.shape} cant be multiplied')
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




    ######## Recursive substitution ########


    def subs(self, symbols, repl):
        '''subs(symbols: Matrix | List[SymbolNumeric] | SymbolNumeric, repl: numeric) -> Matrix
        Performs a substitution of a vector of symbols or a symbol with a numeric value in all
        of the elements of the this matrix.


        * Replace a symbol with a numeric value:

            :Example:

            >>> a, b = new_param('a'), new_param('b')
            >>> m = Matrix([[a ** 2, a ** b], [b ** a, b ** 2]])
            >>> m
            ╭            ╮
            │ a**2  a**b │
            │ b**a  b**2 │
            ╰            ╯
            >>> m.subs(a, 0)
            ╭             ╮
            │ 0  (0.0)**b │
            │ 1      b**2 │
            ╰             ╯
            >>> m.subs(a, 1)
            ╭         ╮
            │ 1     1 │
            │ b  b**2 │
            ╰         ╯
            >>> m.subs(b, 1)
            ╭         ╮
            │ a**2  a │
            │    1  1 │
            ╰         ╯

        * Replace multiple symbols with a numeric value:

            :Example:

            >>> m = Matrix([[a ** 2, a - b], [b - a, b ** 2]])
            >>> m
            ╭            ╮
            │ a**2   a-b │
            │ -a+b  b**2 │
            ╰            ╯
            >>> m.subs([a, b], 2)
            ╭      ╮
            │ 4  0 │
            │ 0  4 │
            ╰      ╯
            >>> q = Matrix([a, b])
            >>> m.subs(q, 1)
            ╭      ╮
            │ 1  0 │
            │ 0  1 │
            ╰      ╯


        :param symbols: Must be a matrix or a list of symbols to be replaced. It can also
            be a single symbol.
            If its a matrix, it must have a single row or column.
        :type symbols: Matrix, List[SymbolNumeric], SymbolNumeric

        :param repl: The numeric value which will be used to replace the symbols with

        :type repl: numeric

        :rtype: Matrix

        '''

        try:
            if not isinstance(symbols, (Matrix, SymbolNumeric, Iterable)):
                raise TypeError

            if isinstance(symbols, SymbolNumeric):
                symbols = Matrix(values=[symbols])

            elif isinstance(symbols, Matrix):
                if symbols.get_num_rows() != 1 and symbols.get_num_cols() != 1:
                    raise ValueError('symbols matrix must have one single row or column')
                if symbols.get_num_rows() == 1:
                    symbols = symbols.transpose()

            else:
                symbols = tuple(symbols)
                if not symbols:
                    raise ValueError('You must specify at least one symbol')
                if not all(map(lambda symbol: isinstance(symbol, SymbolNumeric), symbols)):
                    raise TypeError
                symbols = Matrix(values=symbols).transpose()
        except TypeError:
            raise TypeError('symbols must be a Matrix, list of symbols or a symbol')

        repl = _parse_numeric_value(repl)

        return _matrix_from_c_value(c_subs(
            c_deref(self._get_c_handler()),
            c_deref((<Matrix>symbols)._get_c_handler()),
            repl
        ))





    ######## Misc operations ########


    cpdef transpose(self):
        '''
        Get the transposed matrix

            :Example:

            >>> m = new_matrix('a', range(0, 9), shape=[3, 3])
            >>> m
            ╭         ╮
            │ 0  1  2 │
            │ 3  4  5 │
            │ 6  7  8 │
            ╰         ╯
            >>> m.transpose()
            ╭         ╮
            │ 0  3  6 │
            │ 1  4  7 │
            │ 2  5  8 │
            ╰         ╯

        :rtype: Matrix

        '''
        cdef c_Matrix c_mat = self._get_c_handler().transpose()
        return _matrix_from_c_value(c_mat)


    def get_transposed(self):
        '''
        Alias of transpose method

        .. seealso:: :func:`transpose`

        '''
        return self.transpose()





    ######## Properties ########


    @property
    def shape(self):
        '''
        Read only property that returns the shape of this matrix

        :rtype: Tuple[int, int]

        .. note:: It calls internally to ``get_shape``

            .. seealso:: :func:`get_shape`

        '''
        return self.get_shape()

    @property
    def num_rows(self):
        '''
        Read only property that returns the number of rows of this matrix

        :rtype: int


        .. note:: It calls internally to ``get_num_rows``

            .. seealso:: :func:`get_num_rows`
        '''
        return self.get_num_rows()

    @property
    def num_cols(self):
        '''
        Read only property that returns the number of columns of this matrix

        :rtype: int

        .. note:: It calls internally to ``get_num_cols``

            .. seealso:: :func:`get_num_cols`
        '''
        return self.get_num_cols()

    @property
    def size(self):
        '''
        Read only property that returns the total number of items on this matrix

        :rtype: int

        .. note:: It calls internally to ``get_size``

            .. seealso:: :func:`get_size`

        '''
        return self.get_size()


    @property
    def T(self):
        '''
        Read only property that returns the transposed matrix

        :rtype: Matrix

        .. note:: It calls internally to ``transpose``

            .. seealso:: :func:`transpose`

        '''
        return self.transpose()

    @property
    def transposed(self):
        '''
        Read only property that returns the transposed matrix

        :rtype: Matrix

        .. note:: It calls internally to ``transpose``

            .. seealso:: :func:`transpose`

        '''
        return self.transpose()


    @property
    def values(self):
        '''
        Read only property that returns all the items of this matrix as a regular list

        :rtype: List[Expr]

        .. note:: It calls internally to ``get_values``

            .. seealso:: :func:`get_values`

        '''
        return self.get_values()






    ######## Creation routines ########


    @classmethod
    def eye(cls, n):
        '''eye(n: int) -> Matrix
        Create a symbolic identity matrix of size nxn

            :Example:

            >>> Matrix.eye(3)
            ╭         ╮
            │ 1  0  0 │
            │ 0  1  0 │
            │ 0  0  1 │
            ╰         ╯
            >>> Matrix.eye(2)
            ╭      ╮
            │ 1  0 │
            │ 0  1 │
            ╰      ╯

        :rtype: Matrix

        '''
        if not isinstance(n, int) or n <= 0:
            raise TypeError('n must be a number greater than zero')
        return cls(np.eye(n))



    ######## Rotation matrices ########


    @classmethod
    def xrot(cls, phi):
        '''xrot(phi: Expr) -> Matrix
        Get a 3x3 matrix transformation which represents a rotation of ``phi`` radians
        with respect the x axis

            :Example:

            >>> a = new_param('a')
            >>> Matrix.xrot(a)
            ╭                    ╮
            │ 1       0        0 │
            │ 0  cos(a)  -sin(a) │
            │ 0  sin(a)   cos(a) │
            ╰                    ╯

        :type phi: Expr
        :rtype: Matrix

        '''
        return cls.rot([1, 0, 0], phi)


    @classmethod
    def yrot(cls, phi):
        '''yrot(phi: Expr) -> Matrix
        Get a 3x3 matrix transformation which represents a rotation of ``phi`` radians
        with respect the y axis

            :Example:

            >>> a = new_param('a')
            >>> Matrix.yrot(a)
            ╭                    ╮
            │  cos(a)  0  sin(a) │
            │       0  1       0 │
            │ -sin(a)  0  cos(a) │
            ╰                    ╯

        :type phi: Expr
        :rtype: Matrix

        '''
        return cls.rot([0, 1, 0], phi)



    @classmethod
    def zrot(cls, phi):
        '''zrot(phi: Expr) -> Matrix
        Get a 3x3 matrix transformation which represents a rotation of ``phi`` radians
        with respect the z axis

            :Example:

            >>> a = new_param('a')
            >>> Matrix.zrot(a)
            ╭                    ╮
            │ cos(a)  -sin(a)  0 │
            │ sin(a)   cos(a)  0 │
            │      0        0  1 │
            ╰                    ╯

        :type phi: Expr
        :rtype: Matrix

        '''
        return cls.rot([0, 0, 1], phi)



    @classmethod
    def rot(cls, axis, phi):
        '''rot(axis: Matrix, phi: Expr) -> Matrix
        Get a 3x3 matrix transformation which represents a rotation of ``phi`` radians
        with respect the given axis

            :Example:

            >>> x, y, z = new_param('x'), new_param('y'), new_param('z')
            >>> a = new_param('a')
            >>> Matrix.rot(axis=[x, y, z], phi=a)
            ╭                                                                                 ╮
            │ 1+(z**2+y**2)*(-1+cos(a))  -z*sin(a)-x*y*(-1+cos(a))   y*sin(a)-x*(-1+cos(a))*z │
            │  z*sin(a)-x*y*(-1+cos(a))  1+(z**2+x**2)*(-1+cos(a))  -y*(-1+cos(a))*z-x*sin(a) │
            │ -y*sin(a)-x*(-1+cos(a))*z  -y*(-1+cos(a))*z+x*sin(a)  1+(x**2+y**2)*(-1+cos(a)) │
            ╰                                                                                 ╯

        :type axis: Matrix
        :type phi: Expr
        :rtype: Matrix

        '''
        if not isinstance(axis, Matrix):
            axis = Matrix(shape=(1, 3), values=axis)
        elif axis.size != 3:
            raise TypeError('Axis must be a column or row matrix with three values')

        if not isinstance(phi, Expr):
            phi = Expr(phi)

        axis_skew = axis.get_skew()
        return cls.eye(3) + sin(phi) * axis_skew + (1 - cos(phi)) * (axis_skew * axis_skew)



    ######## Misc ########

    def __eq__(self, other):
        if not isinstance(other, Matrix):
            return False
        if (self.num_rows == 1 or self.num_cols == 1) and (other.num_rows == 1 or other.num_cols == 1):
            if len(self) != len(other):
                return False
        elif self.shape != other.shape:
            return False
        for a, b in zip(self, other):
            if a != b:
                return False
        return True




NamedObject.register(Matrix)
LatexRenderable.register(Matrix)
