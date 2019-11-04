'''
Author: Víctor Ruiz Gómez
Description:
This file defines test cases for the getter methods of the class System.
'''


import pytest
from functools import partial
from itertools import product
from operator import itemgetter



######## Fixtures ########

@pytest.fixture(scope='module')
def system():
    '''
    This fixture returns an instance of the class System used for the above test cases.
    Its a system with predefined parameters, matrices, vectors, tensors, ...
    It also returns a dictionary with information about the predefined objects in the system.
    '''
    from lib3d_mec_ginac import System

    s = System()
    s.new_parameter('a')
    s.new_joint_unknown('b')
    s.new_input('c')
    s.new_coordinate('h', 'dh', 'ddh')
    s.new_aux_coordinate('k', 'dk', 'ddk')
    s.new_base('r', 'xyz')
    s.new_matrix('y', shape=[3,3])
    s.new_vector('v', 1, 2, 3)
    s.new_tensor('q')
    s.new_point('p', 'v')
    s.new_frame('z', 'O')

    s.new_base('Barm', 0, 1, 0)
    s.new_param('m', 1)
    s.new_vector('Oarm_Garm', 0, 0, 1, 'Barm')
    s.new_tensor('Iarm', base='Barm')
    s.new_solid('arm', 'O', 'Barm', 'm', 'Oarm_Garm', 'Iarm')

    s.new_vector('f', 0, 1, 0, 'xyz')
    s.new_vector('mt', 0, 0, 0, 'xyz')
    s.new_wrench('w', 'f', 'mt', 'p', 'arm', 'Constraint')

    return s



@pytest.fixture(scope='module')
def system_objects_info(system):
    '''
    This fixture returns information about the objects defined in the system created
    in the fixture above
    '''
    from lib3d_mec_ginac import SymbolNumeric, Base, Matrix, Vector3D, Tensor3D, Point, Frame, Solid, Wrench3D
    return {
        'a':   {'class':SymbolNumeric, 'getter': system.get_parameter, 'kind': 'parameter'},
        'b':   {'class':SymbolNumeric, 'getter': system.get_joint_unknown, 'kind': 'joint_unknown'},
        'c':   {'class':SymbolNumeric, 'getter': system.get_input, 'kind': 'input'},
        'h':   {'class':SymbolNumeric, 'getter': system.get_coordinate, 'kind': 'coordinate'},
        'dh':  {'class':SymbolNumeric, 'getter': system.get_velocity, 'kind': 'velocity'},
        'ddh': {'class':SymbolNumeric, 'getter': system.get_acceleration, 'kind': 'acceleration'},
        'k':   {'class':SymbolNumeric, 'getter': system.get_aux_coordinate, 'kind': 'aux_coordinate'},
        'dk':  {'class':SymbolNumeric, 'getter': system.get_aux_velocity, 'kind': 'aux_velocity'},
        'ddk': {'class':SymbolNumeric, 'getter': system.get_aux_acceleration, 'kind': 'aux_acceleration'},

        'r':   {'class':Base, 'getter': system.get_base},
        'y':   {'class':Matrix, 'getter': system.get_matrix},
        'v':   {'class':Vector3D, 'getter': system.get_vector},
        'q':   {'class':Tensor3D, 'getter': system.get_tensor},
        'p':   {'class':Point, 'getter': system.get_point},
        'z':   {'class':Frame, 'getter': system.get_frame},
        'arm': {'class':Solid, 'getter': system.get_solid},
        'w':   {'class':Wrench3D, 'getter': system.get_wrench}
    }


@pytest.fixture(scope='module')
def getters(system):
    '''
    This fixture returns the getters of the system defined by the fixture 'system'
    '''
    return tuple(map(partial(getattr, system), ('get_coordinate', 'get_velocity', 'get_acceleration',
    'get_aux_coordinate', 'get_aux_velocity', 'get_aux_acceleration',
    'get_parameter', 'get_joint_unknown', 'get_input',
    'get_base', 'get_matrix', 'get_vector', 'get_tensor', 'get_point',
    'get_frame', 'get_solid', 'get_wrench')))





######## Tests ########


def test_getters_input_type(getters, strings, non_strings):
    '''
    This test case checks that:
    - All getters in the class System have one input argument, which must be a
    string. If its not string, it should raise TypeError
    - If the input argument is string, it should not raise TypeError
    '''
    for getter, non_string in product(getters, non_strings):
        with pytest.raises(TypeError):
            getter(non_string)

    for getter, string in product(getters, strings):
        try:
            getter(string)
        except TypeError:
            raise AssertionError
        except IndexError:
            pass




def test_getters_invalid_name(system_objects_info, getters, strings):
    '''
    This test case checks that if the name passed as argument to the getter is not the name of
    any of the objects created previously in the System, the method raises IndexError
    '''
    for getter, name in product(getters, set(strings) - set(system_objects_info)):
        with pytest.raises(IndexError):
            getter(name)


    for a, getter in zip(system_objects_info.keys(), tuple(map(itemgetter('getter'), system_objects_info.values()))):
        for b in set(system_objects_info.keys()) - set([a]):
            try:
                with pytest.raises(IndexError):
                    getter(b)
            except:
                raise AssertionError(f'{getter.__qualname__} didnt raise IndexError properly')



def test_getters_return_value(system_objects_info):
    '''
    This test case checks that if the name passed as argument to the getter is the name
    of any of the object created previously in the System, no exception is raised and the return
    value is:
    * SymbolNumeric for the methods:
        get_coordinate, get_velocity, get_acceleration,
        get_aux_coordinate, get_aux_velocity, get_aux_acceleration,
        get_parameter, get_joint_unknown, get_input
    * Base for get_base
    * Matrix for get_matrix
    * Vector3D for get_vector
    * Tensor3D for get_tensor
    * Wrench3D for get_wrench
    * Point for get_point
    * Frame for get_frame
    * Solid for get_solid
    '''
    from lib3d_mec_ginac import SymbolNumeric

    for name, info in system_objects_info.items():
        cls, getter = info['class'], info['getter']
        obj = getter(name)
        assert isinstance(obj, cls)

        if cls == SymbolNumeric:
            kind = info['kind']
            assert kind == obj.get_type()
