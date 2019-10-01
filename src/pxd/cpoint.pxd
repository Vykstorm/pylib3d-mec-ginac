'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Point.h that are going to be used by this library
'''

######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from .pxd file definitions
from src.pxd.cvector3D cimport Vector3D



######## Class Point ########

cdef extern from "Point.h":
    cdef cppclass Point:

        Point*    get_Previous_Point()
        Vector3D* get_Position_Vector()
        string    get_name()
        void      set_name(string name)
