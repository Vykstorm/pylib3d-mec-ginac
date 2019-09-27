'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Matrix
'''

######## Imports ########

# Cython imports
from cython.operator cimport dereference as c_deref

# C++ standard library imports
from libcpp.string cimport string as c_string

# Import .pxd declarations
from src.cmatrix cimport Matrix as c_Matrix
from src.cginac cimport matrix as c_ginac_matrix
from src.cginac cimport print_python as c_print_context
from src.cginac cimport ex as c_ex
from src.cpp cimport stringstream as c_sstream

# Python imports
from collections.abc import Iterable
from itertools import chain


######## Helper methods ########


cdef Matrix _matrix_from_c(c_Matrix* x):
    # Converts C++ Matrix to Python class Matrix instance
    m = Matrix()
    m._c_handler, m._owns_c_handler = x, False
    return m






######## Class Matrix ########

cdef class Matrix:

    ######## C Attributes ########


    cdef c_Matrix* _c_handler
    cdef bint _owns_c_handler



    ######## Constructor ########


    def __cinit__(self, values=None, shape=None):
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


    ######## Getters ########


    cdef c_Matrix* _get_c_handler(self):
        if self._c_handler == NULL:
            self._c_handler = new c_Matrix(1, 1)
            self._owns_c_handler = True
        return self._c_handler


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
        return list(iter(self))



    def get(self, i, j):
        '''
        Get the value at ith row and jth column
        :param int i: The row index
        :param int j: The column index
        :returns: The item at the given position
        :rtype: Expr
        :raises TypeError: If indices are not int objects
        :raises IndexError: If indices are out of bounds
        '''
        i, j = self._parse_indices(i, j)
        return _expr_from_c(self._get_c_handler().get(i, j))




    ######## Changing values ########


    def set(self, i, j, value):
        '''
        Set the value at ith row and jth column
        :param int i: The row index
        :param int j: The column index
        :raises TypeError: If indices are not int objects
        :raises IndexError: If indices are out of bounds
        '''
        i, j = self._parse_indices(i, j)
        if not isinstance(value, Expr):
            value = Expr(value)
        self._get_c_handler().set(i, j, (<Expr>value)._c_handler)



    ######## Methods ########


    def transpose(self):
        '''
        Tranpose this matrix
        :returns: Returns this matrix transposed
        '''
        cdef c_Matrix a = self._get_c_handler().transpose()
        cdef c_Matrix* b = new c_Matrix(a.get_matrix())
        b.set_name(a.get_name())

        m = Matrix()
        (<Matrix>m)._c_handler, (<Matrix>m)._owns_c_handler = b, True
        return m


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
    def values(self):
        '''
        Read only property that returns all the items of this matrix
        :rtype: List[Expr]
        '''
        return self.values()



    ######## Metamethods ########

    def __len__(self):
        return self.get_size()


    def __iter__(self):
        n, m = self.get_shape()
        for i in range(0, n):
            for j in range(0, m):
                yield _expr_from_c(self._get_c_handler().get(i, j))


    def __getitem__(self, index):
        if not isinstance(index, tuple) or len(index) != 2:
            raise TypeError('Matrix index must be a pair of numbers (row and column indices)')
        return self.get(*index)

    def __setitem__(self, index, value):
        if not isinstance(index, tuple) or len(index) != 2:
            raise TypeError('Matrix index must be a pair of numbers (row and column indices)')
        i, j = index
        self.set(i, j, value)


    def __str__(self):
        # Use GiNac print method to print the underline matrix
        cdef c_print_context* c_printer = new c_print_context(c_sstream())
        self._get_c_handler().get_matrix().print(c_deref(c_printer))
        cdef c_string s = (<c_sstream*>&c_printer.s).str()
        del c_printer
        return (<bytes>s).decode()

    def __repr__(self):
        return self.__str__()
