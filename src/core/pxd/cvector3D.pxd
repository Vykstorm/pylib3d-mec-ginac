'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Vector3D.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string


# Imports from .pxd file definitions
from src.core.pxd.ginac.cexpr cimport ex
from src.core.pxd.cmatrix cimport Matrix
from src.core.pxd.cbase cimport Base
from src.core.pxd.csystem cimport System



######## Class Vector3D ########

cdef extern from "Vector3D.h":
    cdef cppclass Vector3D(Matrix):
        Vector3D(string, ex, ex, ex, Base*) except +

        Base* get_Base()
        void set_Base(Base*)
        Vector3D in_Base(Base*)

        string get_Name()

        ex get_module()
        Matrix skew()

        void set_System(System *)
        System* get_System()

        # Arithmetic operations
        Vector3D operator-()
        Vector3D operator+(Vector3D&)
        Vector3D operator-(Vector3D&)
        ex operator*(Vector3D&)
        Vector3D operator^(Vector3D&)
