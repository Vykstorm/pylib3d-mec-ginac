'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Wrench3D.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string



# Imports from .pxd file definitions
from src.pxd.cvector3D cimport Vector3D
from src.pxd.cpoint cimport Point
from src.pxd.csolid cimport Solid
from src.pxd.ginac.cexpr cimport ex


######## Class Wrench3D ########

cdef extern from "Wrench3D.h":
    cdef cppclass Wrench3D:
        # Constructors
        Wrench3D(string name, Vector3D force, Vector3D moment, Point* point, Solid* sol, string type) except +

        # Getters
        string get_name()
        Vector3D get_Force()
        Vector3D get_Moment()
        Point* get_Point()
        Solid* get_Solid()
        string get_Type()

        # Operations
        Wrench3D unatomize()
        Wrench3D at_Point(Point* point)

        # Arithmetic operations
        Wrench3D operator+(Wrench3D& other)
        Wrench3D operator-(Wrench3D& other)
        Wrench3D operator-()
        ex operator*(Wrench3D& other)
