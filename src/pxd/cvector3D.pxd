'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Vector3D.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string


# Imports from .pxd file definitions
from src.pxd.cginac cimport ex
from src.pxd.cmatrix cimport Matrix
from src.pxd.cbase cimport Base



######## Class Vector3D ########

cdef extern from "Vector3D.h":
    cdef cppclass Vector3D(Matrix):
        Vector3D(string name, ex x, ex y, ex z, Base* base) except +
