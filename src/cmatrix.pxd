'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Matrix.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from .pxd file definitions
from src.cginac cimport matrix, ex


######## Class Matrix ########
cdef extern from "Matrix.h":
    cdef cppclass Matrix:
        Matrix() except +
        Matrix(long rows, long cols) except +

        string get_name()
        void set_name(string name)

        matrix get_matrix()

        long rows()
        long cols()

        ex& get(int i, int j)
        void set(int i, int j, ex& value)


        Matrix get_row(int i)
        Matrix get_col(int j)
        void set_row(const int i, Matrix values)
        void set_col(const int j, Matrix values)
        Matrix remove_row(const int i)
        Matrix remove_col(const int j)

        Matrix transpose()
        Matrix expand()
