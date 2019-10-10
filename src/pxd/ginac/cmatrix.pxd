'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::matrix and all its
methods which are going to be used by this library
'''

######## Imports ########

from src.pxd.ginac.cbasic cimport basic



######## Class GiNaC::matrix ########

cdef extern from "ginac/matrix.h" namespace "GiNaC":
    cdef cppclass matrix(basic):
        pass
