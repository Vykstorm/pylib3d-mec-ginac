
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
