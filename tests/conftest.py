
import pytest
from functools import partial
from itertools import chain, filterfalse
from re import match
from inspect import isclass
from lib3d_mec_ginac import *


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
    from lib3d_mec_ginac import System
    return tuple(filterfalse(System().get_symbols().__contains__,
        ('a', 'b', 'c', 'foo', 'bar', 'foobar', 'foo_bar', '_foo', 'foo2', 'bar_2', '__foo')))


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
def system():
    '''
    This fixture creates a system with a few objects ( vectors, tensors, wrenches, ... )
    for testing purposes ( it is used in the tests below )
    The return system instance will have the next objects ( sorted by type ):
    - symbols:
        * parameters:      a, b
        * inputs:          c
        * joint_unknowns:  d
        * coordinates:     (x, dx, ddx)
        * aux_coordinates: (y, dy, ddy)

    - bases:    bs
    - vectors:  v
    - points:   p
    - tensors:  q
    - solids:   s
    - wrenches: w
    - frames:   f
    '''
    sys = System()

    # Fill system with symbols
    sys.new_parameter('a')
    sys.new_parameter('b')
    sys.new_input('c')
    sys.new_joint_unknown('d')
    sys.new_coordinate('x')
    sys.new_aux_coordinate('y')

    # Fill system with geometric objects
    sys.new_base('bs')
    sys.new_vector('v', base='bs')
    sys.new_vector('r')
    sys.new_point('p', 'O', 'v')
    sys.new_tensor('q', base='bs')
    sys.new_solid('s', 'p', 'bs', 'a', 'v', 'q')
    sys.new_frame('f', 'p', 'bs')
    sys.new_wrench('w', 'v', 'r', 'p', 's', 'Constraint')

    return sys
