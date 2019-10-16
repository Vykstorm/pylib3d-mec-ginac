
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
from src.pxd.ginac.cnumeric cimport numeric
from src.pxd.ginac.cexpr cimport ex
from src.pxd.ginac.csymbol cimport symbol

# lib3d-mec-ginac classes
from src.pxd.csymbol_numeric cimport symbol_numeric
from src.pxd.cbase cimport Base
from src.pxd.cmatrix cimport Matrix
from src.pxd.cvector3D cimport Vector3D
from src.pxd.ctensor3D cimport Tensor3D
from src.pxd.cpoint cimport Point
from src.pxd.cframe cimport Frame
from src.pxd.csolid cimport Solid
from src.pxd.cwrench3D cimport Wrench3D



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
        vector[Tensor3D*] get_Tensors()
        vector[Point*] get_Points()
        vector[Frame*] get_Frames()
        vector[Solid*] get_Solids()
        vector[Wrench3D*] get_Wrenches()

        Base* get_Base(string name)
        Matrix* get_Matrix(string name)
        Vector3D* get_Vector3D(string name)
        Tensor3D* get_Tensor3D(string name)
        Point* get_Point(string name)
        Frame* get_Frame(string name)
        Solid* get_Solid(string name)
        Wrench3D* get_Wrench3D(string name)

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
        void new_Tensor3D(Tensor3D* t)
        Point* new_Point(string name, Point* previous, Vector3D* position_vector)
        Frame* new_Frame(string name, Point* point, Base* base)
        Solid* new_Solid(string name, Point* point, Base* base, symbol_numeric* mass, Vector3D* CM, Tensor3D* IT)
        Wrench3D* new_Wrench3D(string name, Vector3D force, Vector3D moment, Point* point, Solid* solid, string type)


        # Kinematic operations

        Base* Reduced_Base(Base*, Base*)
        Point* Reduced_Point(Point*, Point*)
        Point* Pre_Point_Branch(Point*, Point*)
        Matrix Rotation_Matrix(Base*, Base*)
        Vector3D Position_Vector(Point*, Point*)
        Vector3D Angular_Velocity(Base*, Base*)
        Tensor3D Angular_Velocity_Tensor(Base*, Base*)
        Vector3D Velocity_Vector(Frame*, Point*)
        Vector3D Velocity_Vector(Frame*, Point*, Solid*)
        Vector3D Angular_Acceleration(Base*, Base*)
        Vector3D Acceleration_Vector(Frame*, Point*)
        Vector3D Acceleration_Vector(Frame*, Point*, Solid*)

        Wrench3D Twist(Solid*)

        ex dt(ex)
        Vector3D dt(Vector3D)
        Matrix Dt(Matrix)
        Vector3D Dt(Vector3D, Base*)
        Vector3D Dt(Vector3D, Frame*)

        Matrix jacobian(Matrix, Matrix, ex)
        Matrix jacobian(Matrix, Matrix)
        Matrix jacobian(ex, Matrix)
        Matrix jacobian(Matrix, symbol)
        Matrix jacobian(ex, symbol)

        ex diff(ex, symbol)
        Matrix diff(Matrix, symbol)
        Vector3D diff(Vector3D, symbol)
        Tensor3D diff(Tensor3D, symbol)
        Wrench3D diff(Wrench3D, symbol)
        Wrench3D diff(Wrench3D, ex)

        ex numeric_evaluate(ex)
        Matrix evaluate_Matrix(Matrix)
