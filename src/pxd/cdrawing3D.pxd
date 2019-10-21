'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the
lib3d-mec-ginac Drawing3D.h header that will be used by this library
'''

######## Imports ########

# C++ standard imports
from libcpp.string  cimport string

# ginac imports
from src.pxd.ginac.clst     cimport lst
from src.pxd.ginac.cnumeric cimport numeric

# lib3d-mec-ginac imports
from src.pxd.cpoint    cimport Point
from src.pxd.cbase     cimport Base
from src.pxd.cvector3D cimport Vector3D



######## Class Drawing3D ########

cdef extern from "Drawing3D.h":
    cdef cppclass Drawing3D:
        # Constructors
        Drawing3D(string, string, Point*, Base*)

        # Getters
        string   get_name()
        string   get_file()
        lst      get_color()
        string   get_type()
        Point*   get_point()
        Base*    get_base()
        numeric  get_scale()
        Vector3D get_vector()

        # Setters
        void set_file(string)
        void set_color(lst)
        void set_scale(numeric)
        void set_vector(Vector3D)
