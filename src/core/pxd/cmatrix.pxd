'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Matrix.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string
from libcpp.vector cimport vector

# Imports from .pxd file definitions
from src.core.pxd.ginac.cmatrix cimport matrix
from src.core.pxd.ginac.cexpr cimport ex


######## Class Matrix ########
cdef extern from "Matrix.h":
    cdef cppclass Matrix:
        # Constructors
        Matrix() except +
        Matrix(long, long) except +
        Matrix(long, long, vector[Matrix*]) except +
        Matrix(matrix) except +


        # Getters
        string get_name()
        void set_name(string)
        long rows()
        long cols()

        matrix get_matrix()
        void set_matrix(matrix)
        ex& get(int i, int j)

        # Setters
        void set(int, int, ex&)

        # Arithmetic operations
        Matrix operator+()
        Matrix operator-()
        Matrix operator+(Matrix&)
        Matrix operator-(Matrix&)
        Matrix operator*(Matrix&)
        Matrix operator*(ex&)


        # Misc operations
        Matrix transpose()
        Matrix expand()
