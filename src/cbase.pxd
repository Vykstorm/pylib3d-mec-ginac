

# Imports from the standard library
from libcpp.string cimport string

# Imports from other .pxd files
from src.cexpression cimport ex

cdef extern from "Base.h":
    cdef cppclass Base:
        ## Getters
        string get_name()
        # Matrix get_Rotation_Tupla()
        Base* get_Previous_Base()
        ex get_Rotation_Angle()
