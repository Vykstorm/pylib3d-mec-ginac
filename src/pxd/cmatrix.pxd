'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Matrix.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from .pxd file definitions
from src.pxd.cginac cimport matrix, ex


######## Class Matrix ########
cdef extern from "Matrix.h":
    cdef cppclass Matrix:
        # Constructors
        Matrix() except +
        Matrix(long rows, long cols) except +
        Matrix(matrix m) except +

        # Getters
        string get_name()
        void set_name(string name)
        long rows()
        long cols()

        matrix get_matrix()
        ex& get(int i, int j)

        # Setters
        void set(int i, int j, ex& value)

        # Arithmetic operations
        Matrix operator+(Matrix& other)
        Matrix operator-(Matrix& other)
        Matrix operator*(Matrix& other)
        Matrix operator*(ex& other)


        # Misc operations
        Matrix transpose()
        Matrix expand()
