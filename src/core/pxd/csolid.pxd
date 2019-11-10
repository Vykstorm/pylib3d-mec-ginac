'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Solid.h that are going to be used by this library
'''



######## Imports ########

from src.core.pxd.cframe cimport Frame
from src.core.pxd.cvector3D cimport Vector3D
from src.core.pxd.ctensor3D cimport Tensor3D
from src.core.pxd.cpoint cimport Point
from src.core.pxd.csymbol_numeric cimport symbol_numeric



######## Class Solid ########

cdef extern from "Solid.h":
    cdef cppclass Solid(Frame):

        # Getters
        Vector3D* get_CM()
        Tensor3D* get_IT()
        symbol_numeric* get_mass()
        Point* get_G()
