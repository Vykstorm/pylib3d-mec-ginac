
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac Tensor3D.h header which are going to be used by this library.
'''

######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from .pxd file definitions
from src.core.pxd.cmatrix cimport Matrix
from src.core.pxd.cvector3D cimport Vector3D
from src.core.pxd.cbase cimport Base
from src.core.pxd.ginac.cexpr cimport ex
from src.core.pxd.csystem cimport System






######## Class Tensor3D ########


cdef extern from "Tensor3D.h":
    cdef cppclass Tensor3D(Matrix):
        # Constructor
        Tensor3D(Matrix, Base*, System*)

        # Getters
        Base* get_Base()
        System* get_System()


        # Setters
        void set_Base(Base*)
        Tensor3D in_Base(Base*)


        # Operations
        Tensor3D operator+(Tensor3D&)
        Tensor3D operator-(Tensor3D&)
        Tensor3D operator*(Tensor3D&)
        Vector3D operator*(Vector3D&)
