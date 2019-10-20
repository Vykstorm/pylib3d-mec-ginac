'''
Author: Víctor Ruiz Gómez
Description: This file contains all the declarations of the C++ header
Frame.h that are going to be used by this library
'''


######## Imports ########

# Imports from the standard C++ library
from libcpp.string cimport string

# Imports from other .pxd files
from src.pxd.cpoint cimport Point
from src.pxd.cbase cimport Base
from src.pxd.ginac.cnumeric cimport numeric



######## Class Frame ########

cdef extern from "Frame.h":
    cdef cppclass Frame:
        # Getters
        Point* get_Point()
        Base* get_Base()
        string get_name()
        numeric get_scale()


        # Setters
        void set_Point(Point*)
        void set_Base(Base*)
