
import pytest
from functools import partial
from itertools import chain, filterfalse
from re import match
from inspect import isclass



######## Fixtures ########

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
    import lib3d_mec_ginac
    values = map(partial(getattr, lib3d_mec_ginac), filterfalse(lambda key: key.startswith('_'), dir(lib3d_mec_ginac)))
    funcs = filter(lambda value: callable(value) and not isclass(value), values)
    funcs = filter(lambda func: func.__module__.startswith('lib3d_mec_ginac'), funcs)
    return tuple(funcs)
