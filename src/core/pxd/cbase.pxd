'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac Base.h header which are going to be used by this library.
'''

######## Imports ########

# Imports from the standard library
from libcpp.string cimport string

# Imports from other .pxd files
from src.core.pxd.ginac.cexpr cimport ex
from src.core.pxd.cmatrix cimport Matrix
from src.core.pxd.cvector3D cimport Vector3D



######## class Base ########

cdef extern from "Base.h":
    cdef cppclass Base:
        # Getters
        string get_name()
        Matrix get_Rotation_Tupla()
        Base* get_Previous_Base()
        ex get_Rotation_Angle()

        # Other
        Vector3D angular_velocity()
