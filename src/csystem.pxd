
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac System.h header which are going to be used by this library.
'''

from libcpp.vector cimport vector
from libcpp.string cimport string
from src.csymbol_numeric cimport symbol_numeric

cdef extern from "System.h":

    # Public API for System class
    cdef cppclass System:
        System() except +
        symbol_numeric* new_Parameter(string name)
        symbol_numeric* new_Parameter(string name, string tex_name)

        symbol_numeric* get_Parameter(string name)

        vector[symbol_numeric*] get_Coordinates()
        vector[symbol_numeric*] get_Velocities()
        vector[symbol_numeric*] get_Accelerations()
        vector[symbol_numeric*] get_Parameters()
        vector[symbol_numeric*] get_Inputs()
        vector[symbol_numeric*] get_Joint_Unknowns()

        symbol_numeric* get_Coordinate(string name);
        symbol_numeric* get_Velocity(string name);
        symbol_numeric* get_Acceleration(string name);
        symbol_numeric* get_Parameter(string name);
        symbol_numeric* get_Unknown(string name);
        symbol_numeric* get_Input(string name);
