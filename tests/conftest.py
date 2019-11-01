
import pytest
from functools import partial
from itertools import chain, filterfalse
from re import match
from inspect import isclass



######## Fixtures ########


@pytest.fixture(scope='session')
def strings():
    '''
    This fixture returns a list of arbitrary strings
    '''
    return ('foo', 'bar', 'qux', '', 'abc')


@pytest.fixture(scope='session')
def non_strings():
    '''
    This fixture returns a list of objects which are not strings nor bytes.
    '''
    class Foo:
        pass
    return (False, 0, True, 1.5, 2, partial, Foo, Foo())


@pytest.fixture(scope='session')
def valid_object_names():
    '''
    This fixture returns a list of valid system object names.
    '''
    return ('a', 'b', 'c', 'foo', 'bar', 'foobar', 'foo_bar', '_foo', 'foo2', 'bar_2', '__foo')



@pytest.fixture(scope='session')
def invalid_object_names():
    '''
    This fixture returns a list of invalid system object names.
    '''
    return ('', '1', '1_', '1_foo', '1foo', 'foo$', 'fo(o)', '@foo')



@pytest.fixture(scope='session')
def valid_numeric_values():
    '''
    This fixture returns a list of valid numeric values
    '''
    return -1, 1, 0, 3.1415, -2



@pytest.fixture(scope='session')
def invalid_numeric_values():
    '''
    This fixture returns a list of objects which are not numeric values
    '''
    return 'foo', b'foo', (1, 2, 3), [1, 2, 3], {1, 2, 3}






@pytest.fixture(scope='session')
def classes():
    '''
    This fixture returns a list with all the avaliable classes of this library
    '''
    import lib3d_mec_ginac
    keys = dir(lib3d_mec_ginac)
    return tuple(filter(isclass, map(partial(getattr, lib3d_mec_ginac), keys)))


@pytest.fixture(scope='session')
def methods(classes):
    '''
    This fixture returns a list with all the methods inside any of the classes
    exposed by the library
    '''
    values = chain.from_iterable([[getattr(cls, key) for key in dir(cls)] for cls in classes])
    methods = filter(callable, values)
    #methods = filterfalse(lambda method: method.__name__.startswith('_'), methods)
    methods = filter(lambda method: match(r'\w+\.', method.__qualname__), methods)
    return tuple(methods)


@pytest.fixture(scope='session')
def properties(classes):
    '''
    This fixture returns a list with all the properties of any of the classes
    exposed by the library
    '''
    values = chain.from_iterable([[getattr(cls, key) for key in dir(cls) if not key.startswith('_')] for cls in classes])
    props = filter(lambda value: isinstance(value, property) or type(value).__name__ == 'getset_descriptor', values)
    return tuple(props)


@pytest.fixture(scope='session')
def global_functions():
    '''
    This fixture returns a list with all the global functions exposed by the library
    '''
    import lib3d_mec_ginac
    values = map(partial(getattr, lib3d_mec_ginac), filterfalse(lambda key: key.startswith('_'), dir(lib3d_mec_ginac)))
    funcs = filter(lambda value: callable(value) and not isclass(value), values)
    funcs = filter(lambda func: func.__module__.startswith('lib3d_mec_ginac'), funcs)
    return tuple(funcs)




@pytest.fixture(scope='session')
def api():
    '''
    This fixture returns a structured dictionary containing information about the public
    parts of this library (what functions, methods and classes must be in the public API)
    '''
    return {
        'classes': {
            'System': {
                'methods': [
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
                'properties': [
                    'symbols',
                    'time',
                    'coordinates', 'velocities', 'accelerations',
                    'aux_coordinates', 'aux_velocities', 'aux_accelerations',
                    'parameters', 'joint_unknowns', 'inputs',
                    'bases', 'matrices', 'vectors', 'tensors', 'points',
                    'frames', 'solids', 'wrenches', 'drawings', 'autogen_latex_names'
                ]
            },

            'SymbolNumeric': {
                'methods': [
                    '__complex__', '__float__', '__int__',
                    'get_owner', 'get_tex_name', 'get_type', 'get_value',
                    'set_tex_name', 'set_value',
                    '__neg__', '__pos__', '__add__', '__sub__',
                    '__mul__', '__truediv__', '__pow__'
                ],
                'properties': [
                    'owner', 'tex_name', 'type', 'value'
                ]
            },

            'Expr': {
                'methods': [
                    'eval',
                    '__neg__', '__pos__', '__add__', '__sub__',
                    '__mul__', '__truediv__', '__pow__',
                    '__iadd__', '__isub__', '__imul__', '__itruediv__',
                    '__eq__'
                ],
                'properties': []
            },

            'Base': {
                'methods': [
                'get_previous_base', 'has_previous_base', 'get_rotation_angle',
                'get_rotation_tupla'
                ],
                'properties': [
                    'previous_base', 'previous', 'rotation_tupla', 'rotation_angle'
                ]
            },

            'Matrix': {
                'methods': [
                    'get_shape', 'get_num_rows', 'get_num_cols', 'get_size', '__len__',
                    'get_values', 'get', '__getitem__', 'set', '__setitem__',
                    '__iter__', '__reversed__',
                    '__pos__', '__neg__', '__add__', '__sub__',
                    '__mul__', '__truediv__',
                    'subs', 'transpose', 'get_transposed'
                ],
                'properties': [
                    'shape', 'num_rows', 'num_cols', 'size', 'T', 'transposed', 'values'
                ]
            },

            'Vector3D': {
                'methods': [
                    'get_module', 'get_skew',
                    'in_base', 'dot', 'cross',
                    '__pos__', '__neg__', '__add__', '__sub__',
                    '__mul__', '__truediv__', '__xor__'
                ],
                'properties': [
                    'module', 'skew', 'x', 'y', 'z'
                ]
            },

            'Tensor3D': {
                'methods': [
                    'in_base',
                    '__pos__', '__neg__', '__add__', '__sub__',
                    '__mul__', '__truediv__'
                ],
                'properties': []
            },

            'Wrench3D': {
                'methods': [
                    'get_force', 'get_moment', 'get_solid', 'get_type', 'get_point',
                    'unatomize', 'at_point',
                    '__pos__', '__neg__',
                    '__add__', '__sub__', '__mul__', '__truediv__'
                ],
                'properties': [
                    'force', 'moment', 'solid', 'type', 'point'
                ]
            },

            'Drawing3D': {
                'methods': [
                    'get_file', 'get_type', 'get_color', 'get_point', 'get_scale', 'get_vector',
                    'set_file', 'set_color', 'set_scale', 'set_vector'
                ],
                'properties': [
                    'file', 'point', 'scale', 'type', 'vector', 'color'
                ]
            },

            'Point': {
                'methods': [
                    'get_position_vector', 'get_position', 'get_previous', 'has_previous'
                ],
                'properties': [
                    'position_vector', 'position', 'previous'
                ]
            },

            'Frame': {
                'methods': [
                    'get_point', 'get_scale', 'set_point'
                ],
                'properties': [
                    'point', 'scale'
                ]
            },

            'Solid': {
                'methods': [
                    'get_CM', 'get_IT', 'get_G', 'get_mass'
                ],
                'properties': [
                    'CM', 'IT', 'G', 'mass'
                ]
            }

        },

        'functions': {
            'get_default_system', 'set_default_system',
            'set_atomization_state', 'enable_atomization', 'disable_atomization',
            'get_atomization_state',
            'set_gravity_direction', 'set_gravity_up', 'set_gravity_down',
            'get_gravity_direction',
            'unatomize', 'subs',
            'dot', 'cross'
        }
    }
