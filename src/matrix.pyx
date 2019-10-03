'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Matrix
'''





######## Class Matrix ########

cdef class Matrix:

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

    def get_name(self):
        '''
        Get the name of this matrix
        :rtype: int
        '''
        return (<bytes>self._get_c_handler().get_name()).decode()



    def __len__(self):
        return self.get_size()


    def __getattr__(self, key):
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
        if i not in range(0, self.get_num_rows()):
            raise IndexError('Row index out of bounds')
        return i

    def _parse_col_index(self, j):
        if not isinstance(j, int):
            raise TypeError('Matrix indices must be numbers')
        if j not in range(0, self.get_num_cols()):
            raise IndexError('Column index out of bounds')
        return j


    def _parse_indices(self, i, j):
        return self._parse_row_index(i), self._parse_col_index(j)



    def get_values(self):
        '''
        Get all the items of this matrix
        :returns: A list containing all the items of this matrix, where the item
        at ith row and jth column is located at i*num_cols + j index
        :rtype: List[Expr]
        '''
        return list(self)



    def get(self, i, j=None):
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
        if isinstance(index, tuple):
            if len(index) not in (1, 2):
                raise TypeError('Wrong number of indices')
            return self.get(*index)
        return self.get(index)





    ######## Changing values ########


    def set(self, i, *args):
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
        if isinstance(index, tuple):
            if len(index) != 2:
                raise TypeError('Wrong number of indices')
            i, j = index
            self.set(i, j, value)
        else:
            self.set(index, value)



    ######## Iteration ########


    def __iter__(self):
        n, m = self.get_shape()
        for i in range(0, n):
            for j in range(0, m):
                yield _expr_from_c(self._get_c_handler().get(i, j))




    ######## Arithmetic operations ########


    def __pos__(self):
        return _matrix_from_c_value(c_deref(self._get_c_handler()))

    def __neg__(self):
        return _matrix_from_c_value(-c_deref(self._get_c_handler()))


    def __add__(Matrix self, other):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operand type for +: Matrix and {type(other).__name__}')
        return _matrix_from_c_value(c_deref(self._get_c_handler()) + c_deref((<Matrix>other)._get_c_handler()))


    def __sub__(Matrix self, other):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operand type for -: Matrix and {type(other).__name__}')
        return _matrix_from_c_value(c_deref(self._get_c_handler()) - c_deref((<Matrix>other)._get_c_handler()))


    def __matmul__(Matrix self, other):
        if not isinstance(other, Matrix):
            raise TypeError(f'Unsupported operand type for @: Matrix and {type(other).__name__}')
        return _matrix_from_c_value(c_deref(self._get_c_handler()) * c_deref((<Matrix>other)._get_c_handler()))


    def __mul__(left_op, right_op):
        if isinstance(left_op, Matrix) and isinstance(right_op, Matrix):
            return _matrix_from_c_value(
                c_deref((<Matrix>left_op)._get_c_handler()) * c_deref((<Matrix>right_op)._get_c_handler())
            )

        if not isinstance(left_op, Matrix) and not isinstance(right_op, Matrix):
            raise TypeError(f'Unsupported operand type for @: {type(left_op).__name__} and {type(right_op).__name__}')

        if isinstance(left_op, Matrix):
            right_op = Expr(right_op)
        else:
            left_op, right_op = right_op, Expr(left_op)
        return _matrix_from_c_value(c_deref((<Matrix>left_op)._get_c_handler()) * (<Expr>right_op)._c_handler)




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
        Alias of transpose
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
    def name(self):
        '''
        Read only property that returns the name of this matrix
        :rtype: int
        '''
        return self.get_name()

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
        Read only property that returns all the items of this matrix
        :rtype: List[Expr]
        '''
        return self.get_values()



    ######## Printing ########


    def __str__(self):
        values = tuple(map(str, self.get_values()))
        n, m = self.get_shape()
        if m == 1:
            m, n = n, 1

        col_sizes = [max([len(values[i*m + j]) for i in range(0, n)])+1 for j in range(0, m)]
        delimiters = '[]' if n == 1 or m == 1 else '\u2502'*2

        lines = []
        for i in range(0, n):
            line = ' '.join([values[i*m + j].rjust(col_size) for j, col_size in zip(range(0, m), col_sizes)])
            line = delimiters[0] + line + ' ' + delimiters[1]
            lines.append(line)

        if n > 1 and m > 1:
            # Insert decoratives
            row_width = len(lines[0]) - 2
            head = '\u256d' + ' '*row_width + '\u256e'
            tail = '\u2570' + ' '*row_width + '\u256f'
            lines.insert(0, head)
            lines.append(tail)

        return '\n'.join(lines)


    def __repr__(self):
        return self.__str__()
