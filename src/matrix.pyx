'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Matrix
'''

######## Imports ########

# C++ standard library imports
from libcpp.string cimport string as c_string

# Import .pxd declarations
from src.cmatrix cimport Matrix as c_Matrix
#from src.cginac cimport matrix as c_ginac_matrix




######## Class Matrix ########

cdef class Matrix:

    ######## C Attributes ########


    cdef c_Matrix* _c_handler




    ######## Constructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Matrix*>handler




    ######## Getters ########


    def get_shape(self):
        return self._c_handler.rows(), self._c_handler.cols()

    def get_num_rows(self):
        return self._c_handler.rows()

    def get_num_cols(self):
        return self._c_handler.cols()

    def get_size(self):
        return self.get_num_rows() * self.get_num_cols()

    def get_name(self):
        return (<bytes>self._c_handler.get_name()).decode()




    ######## Accessing matrix values ########


    ######## Changing matrix values ########


    ######## Properties ########


    @property
    def shape(self):
        return self.get_shape()

    @property
    def num_rows(self):
        return self.get_num_rows()

    @property
    def num_cols(self):
        return self.get_num_cols()

    @property
    def size(self):
        return self.get_size()

    @property
    def name(self):
        return self.get_name()




    ######## Metamethods ########

    def __len__(self):
        return self.get_size()
