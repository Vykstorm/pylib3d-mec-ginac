
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac System.h header which are going to be used by this library.
'''

from libcpp.vector cimport vector
from libcpp.string cimport string
from src.csymbol_numeric cimport symbol_numeric
from src.cnumeric cimport numeric

cdef extern from "System.h":

    # Public API for System class
    cdef cppclass System:
        ## Constructors
        System() except +

        ## Symbol container getters
        vector[symbol_numeric*] get_Coordinates()
        vector[symbol_numeric*] get_Velocities()
        vector[symbol_numeric*] get_Accelerations()
        vector[symbol_numeric*] get_AuxCoordinates()
        vector[symbol_numeric*] get_AuxVelocities()
        vector[symbol_numeric*] get_AuxAccelerations()
        vector[symbol_numeric*] get_Parameters()
        vector[symbol_numeric*] get_Inputs()
        vector[symbol_numeric*] get_Joint_Unknowns()

        ## Symbol getters
        symbol_numeric* get_Velocity(string name)
        symbol_numeric* get_Acceleration(string name)
        symbol_numeric* get_AuxVelocity(string name)
        symbol_numeric* get_AuxAcceleration(string name)

        ## Symbol spawners
        symbol_numeric* new_Coordinate(string name, string vel_name, string acc_name, string tex_name, string vel_tex_name, string acc_tex_name, numeric value, numeric vel_value, numeric acc_value)
        symbol_numeric* new_AuxCoordinate(string name, string vel_name, string acc_name, string tex_name, string vel_tex_name, string acc_tex_name, numeric value, numeric vel_value, numeric acc_value)
        symbol_numeric* new_Parameter(string name, string tex_name, numeric value)
        symbol_numeric* new_Joint_Unknown(string name, string tex_name, numeric value)
        symbol_numeric* new_Input(string name, string tex_name, numeric value)
