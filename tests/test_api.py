'''
Author: Víctor Ruiz Gómez
Description:
This file provides test cases to check that all public functions & classes of
the library are avaliable for the user (can be imported from the API)
'''

import pytest
from inspect import isclass
from functools import partial
from itertools import chain, filterfalse
from operator import attrgetter, concat
from re import match


######## Fixtures ########

@pytest.fixture(scope='module')
def classes():
    '''
    This fixture returns a list with all the avaliable classes of this library
    '''
    import lib3d_mec_ginac
    keys = dir(lib3d_mec_ginac)
    return tuple(filter(isclass, map(partial(getattr, lib3d_mec_ginac), keys)))


@pytest.fixture(scope='module')
def methods(classes):
    '''
    This fixture returns a list with all the methods inside any of the classes
    exposed by the library
    '''
    #methods = filter(callable, map(partial(getattr, System), chain.from_iterable(map(dir, classes))))
    values = chain.from_iterable([[getattr(cls, key) for key in dir(cls)] for cls in classes])
    methods = filter(callable, values)
    methods = filterfalse(lambda method: method.__name__.startswith('_'), methods)
    methods = filter(lambda method: match(r'\w+\.', method.__qualname__), methods)
    return tuple(methods)


@pytest.fixture(scope='module')
def properties(classes):
    '''
    This fixture returns a list with all the properties of any of the classes
    exposed by the library
    '''
    values = chain.from_iterable([[getattr(cls, key) for key in dir(cls)] for cls in classes])
    props = filter(lambda value: isinstance(value, property), values)
    return tuple(props)




######## Tests ########


def test_classes(classes):
    '''
    This test checks that the next classes are avaliable:
    SymbolNumeric, Expr, Base, Matrix, Vector3D, Tensor3D, Wrench3D, Drawing3D,
    Point, Frame, Solid, Object, System
    '''
    assert {
        'SymbolNumeric', 'Expr', 'Base', 'Matrix', 'Vector3D', 'Tensor3D', 'Wrench3D',
        'Drawing3D', 'Point', 'Frame', 'Solid', 'Object', 'System'
    }.issubset(set(map(attrgetter('__name__'), classes)))



def test_system_methods(methods):
    '''
    This test checks that all the methods of the class System in the public API
    are avaliable
    '''
    assert set(map(partial(concat, 'System.'), [
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
    ])).issubset(set(map(attrgetter('__qualname__'), methods)))



def test_system_properties(properties):
    '''
    This method checks that all properties defined by the class System in the public
    API are avaliable.
    '''

    assert set(map(partial(concat, 'System.'), [
        'symbols',
        'time',
        'coordinates', 'velocities', 'accelerations',
        'aux_coordinates', 'aux_velocities', 'aux_accelerations',
        'parameters', 'joint_unknowns', 'inputs',
        'bases', 'matrices', 'vectors', 'tensors', 'points',
        'frames', 'solids', 'wrenches', 'drawings', 'autogen_latex_names',

    ])).issubset( set(map(attrgetter('__qualname__'), map(attrgetter('fget'), properties))) )
