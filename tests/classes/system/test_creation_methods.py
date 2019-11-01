'''
Author: Víctor Ruiz Gómez
Description: This file adds test cases for the methods of the class System which
creates new objects (symbols, matrices, tensors, ...)
'''

import pytest
from pytest import approx
from itertools import product, chain, filterfalse
from operator import eq
from types import SimpleNamespace



######## Tests ########



def test_new_parameter_unknown_input(non_strings, valid_object_names, invalid_object_names, valid_numeric_values, invalid_numeric_values):
    '''
    Test case for methods new_joint_unknown, new_parameter and new_input of the class
    System
    '''
    from lib3d_mec_ginac import System, SymbolNumeric

    def create_symbol(*args, **kwargs):
        # Try to create a parameter, unknown or input with the same input arguments
        kinds = set(['parameter', 'joint_unknown', 'input'])
        excs, symbols = {}, {}
        for kind in kinds:
            s = System()
            method = getattr(s, f'new_{kind}')
            try:
                result = method(*args, **kwargs)
                if not isinstance(result, SymbolNumeric):
                    raise AssertionError(f'{method.__qualname__} must return a SymbolNumeric instance')
                if result.get_type() != kind:
                    raise AssertionError(f'{method.__qualname__} must return a {kind} symbol')
                symbols[kind] = result
            except AssertionError as e:
                raise e
            except Exception as e:
                excs[kind] = e

        # Either no one or the three methods raised the same exception
        if len(excs) not in (0, 3):
            raise AssertionError
        if excs:
            assert len(set(map(type, excs.values()))) == 1
            raise next(iter(excs.values()))


        # The created symbols with any of the three routines with the same arguments must
        # have the same name, latex name and numeric value
        names = set(map(lambda symbol: symbol.get_name(), symbols.values()))
        values = set(map(lambda symbol: symbol.get_value(), symbols.values()))
        tex_names = set(map(lambda symbol: symbol.get_tex_name(), symbols.values()))

        assert len(names) == 1 and len(values) == 1 and len(tex_names) == 1

        symbol = next(iter(symbols.values()))
        return SimpleNamespace(
            name=symbol.get_name(),
            tex_name=symbol.get_tex_name(),
            value=symbol.get_value()
        )


    valid_object_names = tuple(filterfalse(System().get_symbols().__contains__, valid_object_names))


    # Check that we can create a symbol only by indicating its name
    for name in valid_object_names:
        props = create_symbol(name)
        assert name == props.name and props.value == 0

    # TypeError is raised if name is not a string
    for non_string in non_strings:
        with pytest.raises(TypeError):
            create_symbol(non_string)

    # ValueError is raised if name is not a valid name
    for name in invalid_object_names:
        with pytest.raises(ValueError):
            create_symbol(name)


    # Check that we can create a symbol by indicating name & latex name (as positional argument)
    for name in valid_object_names:
        props = create_symbol(name, r'\theta')
        assert props.name == name and props.tex_name == r'\theta' and approx(props.value) == 0

    for name, value in product(valid_object_names, valid_numeric_values):
        # Check that we can create a symbol by indicating the name and its value (as positional argument)
        props = create_symbol(name, value)
        assert props.name == name and approx(props.value) == value

        # Check that we can create a symbol by indicating the name, tex name and values only with positional arguments
        props = create_symbol(name, r'\gamma', value)
        assert props.name == name and props.tex_name == r'\gamma' and props.value == value

        # Check that we can create a symbol with name as positional argument and tex name & value as keywords arguments
        props = create_symbol(name, tex_name=r'\alpha', value=value)
        assert props.name == name and props.tex_name == r'\alpha' and props.value == value

        # Check that we can create a symbol with only keyword arguments
        props = create_symbol(name=name, tex_name=r'\sigma', value=value)
        assert props.name == name and props.tex_name == r'\sigma' and props.value == value


    # TypeError is raised if tex_name is not a string
    for non_string in non_strings:
        with pytest.raises(TypeError):
            create_symbol('a', tex_name=non_string)

    # TypeError is raised if value is not a valid numeric value
    for value in invalid_numeric_values:
        with pytest.raises(TypeError):
            create_symbol('a', value=value)







def test_new_coordinates():
    '''
    Test case for methods new_coordinate and new_aux_coordinate of the class System
    '''
    pass


def test_new_base():
    '''
    Test case for the method new_base of the class System
    '''
    pass


def test_new_matrix():
    '''
    Test case for the method new_matrix of the class System
    '''
    pass


def test_new_vector():
    '''
    Test case for the method new_vector of the class System
    '''
    pass


def test_new_tensor():
    '''
    Test case for the method new_tensor of the class System
    '''
    pass


def test_new_point():
    '''
    Test case for the method new_point of the class System
    '''
    pass


def test_new_frame():
    '''
    Test case for the method new_frame of the class System
    '''
    pass


def test_new_solid():
    '''
    Test case for the method new_solid of the class System
    '''
    pass


def test_new_wrench():
    '''
    Test case for the method new_wrench of the class System
    '''
    pass



def test_new_object_warnings():
    '''
    Test that checks if the name passed to the creation methods new_parameter, new_base, ...
    is the name of an already existing object in the system. In that case, the method must
    throw a user warning message if the existing object is of the same type as for the one

    '''
    pass
