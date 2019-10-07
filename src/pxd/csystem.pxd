
'''
Author: Víctor Ruiz Gómez
Description: This file will declare all the methods and classes defined in the lib3d
mec ginac System.h header which are going to be used by this library.
'''


######## Imports ########

# Imports from the standard library
from libcpp.vector cimport vector
from libcpp.string cimport string

# Imports from other .pxd files

# GiNaC classes
from src.pxd.csymbol_numeric cimport symbol_numeric
from src.pxd.cginac cimport numeric, ex

# lib3d-mec-ginac classes
from src.pxd.cbase cimport Base
from src.pxd.cmatrix cimport Matrix
from src.pxd.cvector3D cimport Vector3D
from src.pxd.cpoint cimport Point
from src.pxd.cframe cimport Frame




######## Class System ########

cdef extern from "System.h":

    # Public API for System class
    cdef cppclass System:
        # Constructors
        System() except +
        System(void(*func)(const char*)) except +

        # Attributes
        symbol_numeric t

        # Symbol getters
        vector[symbol_numeric*] get_Coordinates()
        vector[symbol_numeric*] get_Velocities()
        vector[symbol_numeric*] get_Accelerations()
        vector[symbol_numeric*] get_AuxCoordinates()
        vector[symbol_numeric*] get_AuxVelocities()
        vector[symbol_numeric*] get_AuxAccelerations()
        vector[symbol_numeric*] get_Parameters()
        vector[symbol_numeric*] get_Inputs()
        vector[symbol_numeric*] get_Joint_Unknowns()

        symbol_numeric* get_Coordinate(string name)
        symbol_numeric* get_Velocity(string name)
        symbol_numeric* get_Acceleration(string name)
        symbol_numeric* get_AuxCoordinate(string name)
        symbol_numeric* get_AuxVelocity(string name)
        symbol_numeric* get_AuxAcceleration(string name)
        symbol_numeric* get_Parameter(string name)
        symbol_numeric* get_Unknown(string name)
        symbol_numeric* get_Input(string name)

        # Symbol matrix getters
        Matrix Coordinates()
        Matrix Velocities()
        Matrix Accelerations()
        Matrix Aux_Coordinates()
        Matrix Aux_Velocities()
        Matrix Aux_Accelerations()
        Matrix Parameters()
        Matrix Joint_Unknowns()
        Matrix Inputs()

        # Geometric object getters
        vector[Base*] get_Bases()
        vector[Matrix*] get_Matrixs()
        vector[Vector3D*] get_Vectors()
        vector[Point*] get_Points()
        vector[Frame*] get_Frames()

        Base* get_Base(string name)
        Matrix* get_Matrix(string name)
        Vector3D* get_Vector3D(string name)
        Point* get_Point(string name)
        Frame* get_Frame(string name)

        # Symbol constructors
        symbol_numeric* new_Coordinate(string name, string vel_name, string acc_name, string tex_name, string vel_tex_name, string acc_tex_name, numeric value, numeric vel_value, numeric acc_value)
        symbol_numeric* new_AuxCoordinate(string name, string vel_name, string acc_name, string tex_name, string vel_tex_name, string acc_tex_name, numeric value, numeric vel_value, numeric acc_value)
        symbol_numeric* new_Parameter(string name, string tex_name, numeric value)
        symbol_numeric* new_Joint_Unknown(string name, string tex_name, numeric value)
        symbol_numeric* new_Input(string name, string tex_name, numeric value)

        # Geometric object constructors
        Base* new_Base(string name, string previous, ex a, ex b, ex c, ex rotation_angle)
        Matrix* new_Matrix(Matrix* m)
        void new_Vector3D(Vector3D* v)
        Point* new_Point(string name, Point* previous, Vector3D* position_vector)
        Frame* new_Frame(string name, Point* point, Base* base)
