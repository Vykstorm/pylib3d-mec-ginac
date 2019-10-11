'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Solid.h that are going to be used by this library
'''



######## Imports ########

from src.pxd.cframe cimport Frame
from src.pxd.cvector3D cimport Vector3D
from src.pxd.ctensor3D cimport Tensor3D
from src.pxd.cpoint cimport Point
from src.pxd.csymbol_numeric cimport symbol_numeric



######## Class Solid ########

cdef extern from "Solid.h":
    cdef cppclass Solid(Frame):

        # Getters
        Vector3D* get_CM()
        Tensor3D* get_IT()
        symbol_numeric* get_mass()
        Point* get_G()
