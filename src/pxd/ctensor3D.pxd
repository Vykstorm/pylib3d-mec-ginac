
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac Tensor3D.h header which are going to be used by this library.
'''

######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from .pxd file definitions
from src.pxd.cmatrix cimport Matrix
from src.pxd.cbase cimport Base




######## Class Tensor3D ########


cdef extern from "Tensor3D.h":
    cdef cppclass Tensor3D(Matrix):
        Base* get_Base()
