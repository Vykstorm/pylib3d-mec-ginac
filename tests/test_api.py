'''
Author: Víctor Ruiz Gómez
Description:
This file provides test cases to check that all public functions & classes of
the library are avaliable for the user (can be imported from the API)
'''

import pytest



def test_import():
    '''
    This only tests that the library can be imported
    '''
    import lib3d_mec_ginac


def test_api_classes():
    '''
    This test checks that the next classes are a avaliable in the public API:
    * SymbolNumeric, Expr, Base, Matrix, Vector3D, Tensor3D, Wrench3D, Drawing3D,
        Point, Frame, Solid, Object, System
    '''
    from lib3d_mec_ginac import SymbolNumeric, Expr, Base, Matrix
    from lib3d_mec_ginac import Vector3D, Tensor3D, Wrench3D, Drawing3D
    from lib3d_mec_ginac import Point, Frame, Solid, Object, System


def test_api_classes_mro():
    '''
    * Test that the classes SymbolNumeric, Expr, Base, Matrix, Vector3D, Tensor3D, Wrench3D, Drawing3D,
    Point, Frame and Solid are subclasses of Object.
    * Also Vector3D and Tensor3D are subclasses of Matrix
    * Solid is a subclass of Frame
    '''
    from lib3d_mec_ginac import SymbolNumeric, Expr, Base, Matrix
    from lib3d_mec_ginac import Vector3D, Tensor3D, Wrench3D, Drawing3D
    from lib3d_mec_ginac import Point, Frame, Solid, Object

    assert issubclass(SymbolNumeric, Object)
    assert issubclass(Expr, Object)
    assert issubclass(Base, Object)
    assert issubclass(Matrix, Object)
    assert issubclass(Wrench3D, Object)
    assert issubclass(Drawing3D, Object)
    assert issubclass(Point, Object)
    assert issubclass(Frame, Object)
    assert issubclass(Solid, Object)

    assert issubclass(Vector3D, Matrix)
    assert issubclass(Tensor3D, Matrix)
    assert issubclass(Solid, Frame)





def test_api_methods():
    '''
    Test that all methods of any of the classes defined the library are avaliable
    in the API
    '''
    from lib3d_mec_ginac import System, SymbolNumeric, Base, Matrix
    from lib3d_mec_ginac import Vector3D, Tensor3D, Wrench3D, Drawing3D
    from lib3d_mec_ginac import Point, Frame, Solid

    methods = {
        # System methods
        System: [
            'get_value', 'set_value',
            'get_symbol', 'get_time',
            'get_coordinate', 'get_velocity', 'get_acceleration',
            'get_aux_coordinate', 'get_aux_velocity', 'get_aux_acceleration',
            'get_parameter', 'get_joint_unknown', 'get_input',
            'get_base', 'get_matrix', 'get_vector', 'get_tensor', 'get_point',
            'get_frame', 'get_solid', 'get_wrench', 'get_drawing',

            'has_symbol',
            'has_coordinate', 'has_velocity', 'has_acceleration',
            'has_aux_coordinate', 'has_aux_velocity', 'has_aux_acceleration',
            'has_parameter', 'has_joint_unknown', 'has_input',
            'has_base', 'has_matrix', 'has_vector', 'has_tensor', 'has_point',
            'has_frame', 'has_solid', 'has_wrench', 'has_drawing',

            'get_symbols',
            'get_coordinates', 'get_velocities', 'get_accelerations',
            'get_aux_coordinates', 'get_aux_velocities', 'get_aux_accelerations',
            'get_parameters', 'get_joint_unknowns', 'get_inputs',
            'get_bases', 'get_matrices', 'get_vectors', 'get_tensors',
            'get_points', 'get_frames', 'get_solids', 'get_wrenches', 'get_drawings',

            'get_symbols_matrix',
            'get_coordinates_matrix', 'get_velocities_matrix', 'get_accelerations_matrix',
            'get_aux_coordinates_matrix', 'get_aux_velocities_matrix', 'get_aux_accelerations_matrix',

            'new_coordinate', 'new_aux_coordinate',
            'new_parameter', 'new_joint_unknown', 'new_input',
            'new_base', 'new_matrix', 'new_vector', 'new_tensor',
            'new_point', 'new_frame', 'new_solid', 'new_wrench', 'new_drawing',

            'reduced_base', 'reduced_point', 'pre_point_branch', 'rotation_matrix',
            'position_vector', 'angular_velocity', 'angular_velocity_tensor',
            'velocity_vector', 'angular_acceleration', 'acceleration_vector', 'twist',
            'derivative', 'jacobian', 'diff', 'gravity_wrench', 'inertia_wrench',

            'set_as_default'
        ],

        # Symbol numeric methods
        SymbolNumeric: [
            '__complex__', '__float__', '__int__',
            'get_owner', 'get_tex_name', 'get_type', 'get_value',
            'set_tex_name', 'set_value'
        ],

        # Base methods
        Base: [
            'get_previous_base', 'get_rotation_angle', 'get_rotation_tupla',
            'has_previous_base'
        ],

        # Matrix methods
        Matrix: [
            '__getitem__', '__iter__', '__len__', '__reversed__',
            'block', 'get', 'get_num_cols', 'get_num_rows', 'get_shape',
            'get_size', 'get_values',
            'set', 'subs', 'transpose'
        ],

        # Vector3D methods
        Vector3D: [
            'cross', 'dot', 'get_module', 'get_skew', 'in_base'
        ],

        # Tensor3D methods
        Tensor3D: [
            'in_base'
        ],

        # Wrench3D methods
        Wrench3D : [
            'get_force', 'get_moment', 'get_point', 'get_solid', 'get_type'
        ],

        # Drawing3D methods
        Drawing3D: [
            'get_color', 'get_file', 'get_point', 'get_scale', 'get_type', 'get_vector',
            'set_color', 'set_file', 'set_scale', 'set_vector'
        ],

        # Point methods
        Point: [
            'get_position_vector', 'get_previous', 'has_previous'
        ],

        # Frame methods
        Frame: [
            'get_point', 'get_scale', 'set_point'
        ],

        # Solid methods
        Solid: [
            'get_CM', 'get_IT', 'get_mass'
        ]
    }

    for cls, keys in methods.items():
        for key in keys:
            assert hasattr(cls, key) and callable(getattr(cls, key))
