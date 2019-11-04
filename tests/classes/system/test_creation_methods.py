'''
Author: Víctor Ruiz Gómez
Description: This file adds test cases for the methods of the class System which
creates new objects (symbols, matrices, tensors, ...)
'''

import pytest
from pytest import approx
from functools import partial
from itertools import product, chain, filterfalse, combinations, islice, starmap, permutations
from operator import eq, attrgetter
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
        if len(excs) not in (0, len(kinds)):
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
        assert props.name == name and props.tex_name == r'\theta' and props.value == 0

    for name, value in product(valid_object_names, valid_numeric_values):
        # Check that we can create a symbol by indicating the name and its value (as positional argument)
        props = create_symbol(name, value)
        assert props.name == name and props.value == value

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








def test_new_coordinates(strings, non_strings, valid_object_names, invalid_object_names, valid_numeric_values, invalid_numeric_values):
    '''
    Test case for methods new_coordinate and new_aux_coordinate of the class System
    '''

    from lib3d_mec_ginac import System, SymbolNumeric

    def create_coordinate(*args, **kwargs):
        # Try to create coordinates / auxiliar coordinates with the same input arguments
        kinds = set(['coordinate', 'aux_coordinate'])
        excs, symbols = {}, {}
        for kind in kinds:
            s = System()
            method = getattr(s, f'new_{kind}')
            try:
                result = method(*args, **kwargs)
                if not isinstance(result, tuple) or len(result) != 3:
                    raise AssertionError(f'{method.__qualname__} must return a tuple with three items')

                if not all(map(partial(eq, SymbolNumeric), map(type, result))):
                    raise AssertionError(f'{method.__qualname__} must return a tuple of three numeric symbols')

                coord, vel, acc = result

                if not coord.get_type().endswith('coordinate'):
                    raise AssertionError(f'First return value of {method.__qualname__} must be a coordinate symbol')

                if not vel.get_type().endswith('velocity'):
                    raise AssertionError(f'Second return value of {method.__qualname__} must be a velocity symbol')

                if not acc.get_type().endswith('acceleration'):
                    raise AssertionError(f'Second return value of {method.__qualname__} must be an acceleration symbol')

                symbols[kind] = result
            except AssertionError as e:
                raise e
            except Exception as e:
                excs[kind] = e

        # Either new_coordinate and new_aux_coordinate raised the same exceptions or any of the two
        # didnt raise anything.
        if len(excs) not in (0, len(kinds)):
            raise AssertionError
        if excs:
            assert len(set(map(type, excs.values()))) == 1
            raise next(iter(excs.values()))

        # The created symbols with the same arguments must have the same name, latex name and numeric value
        coord, vel, acc = symbols['coordinate']
        aux_coord, aux_vel, aux_acc = symbols['aux_coordinate']

        assert coord.get_name() == aux_coord.get_name()
        assert vel.get_name() == aux_vel.get_name()
        assert acc.get_name() == aux_acc.get_name()

        assert coord.get_value() == aux_coord.get_value()
        assert vel.get_value() == aux_vel.get_value()
        assert acc.get_value() == aux_acc.get_value()

        assert coord.get_tex_name() == aux_coord.get_tex_name()
        assert vel.get_tex_name() == aux_vel.get_tex_name()
        assert acc.get_tex_name() == aux_acc.get_tex_name()

        return [
            SimpleNamespace(name=coord.name, tex_name=coord.tex_name, value=coord.value),
            SimpleNamespace(name=vel.name, tex_name=vel.tex_name, value=vel.value),
            SimpleNamespace(name=acc.name, tex_name=acc.tex_name, value=acc.value)
        ]


    # Check that we can create coordinates only indicating the name.
    # derivative names are autocompleted
    for name in valid_object_names:
        props = create_coordinate(name)
        assert props[0].name == name
        assert props[1].name == 'd'  + name
        assert props[2].name == 'dd' + name
        assert props[0].value == props[1].value == props[2].value == 0

    # Check that we can create coordinates by indicating three names for the coordinate
    # and its derivatives as positional arguments.
    for names in islice(combinations(valid_object_names, 3), 20):
        props = create_coordinate(*names)
        assert all(starmap(eq, zip(names, map(attrgetter('name'), props))))

    # Check that we can create coordinates by indicating only a name followed by the
    # initial values of the coordinate and its derivatives
    for name, values in zip(valid_object_names, combinations(valid_numeric_values, 3)):
        props = create_coordinate(name, *values)
        assert props[0].name == name
        assert props[1].name == 'd'  + name
        assert props[2].name == 'dd' + name
        assert all(starmap(eq, zip(values, map(attrgetter('value'), props))))

    for names, values in islice(zip(combinations(valid_object_names, 3), combinations(valid_numeric_values, 3)), 20):
        # Check that we can create coordinates by indicating the names and initial values of the
        # coordinate and its derivatives
        props = create_coordinate(*(names + values))
        assert all(starmap(eq, zip(names, map(attrgetter('name'), props))))
        assert all(starmap(eq, zip(values, map(attrgetter('value'), props))))

        # We can also indicate the latex names as positional arguments...
        tex_names = (r'\alpha', r'\beta', r'\gamma')
        props = create_coordinate(*(names + tex_names + values))
        assert all(starmap(eq, zip(names, map(attrgetter('name'), props))))
        assert all(starmap(eq, zip(values, map(attrgetter('value'), props))))
        assert all(starmap(eq, zip(tex_names, map(attrgetter('tex_name'), props))))


        # We can also indicate only the names and the latex names only
        props = create_coordinate(*(names + tex_names))
        assert all(starmap(eq, zip(names, map(attrgetter('name'), props))))
        assert props[0].value == props[1].value == props[2].value == 0
        assert all(starmap(eq, zip(tex_names, map(attrgetter('tex_name'), props))))


    # We can create coordinates by indicating all the options via keyword arguments
    props = create_coordinate(
        name='a', vel_name='b', acc_name='c',
        tex_name=r'\alpha', vel_tex_name=r'\beta', acc_tex_name=r'\gamma',
        value=1, vel_value=2, acc_value=3
    )
    assert props[0].name == 'a' and props[0].tex_name == r'\alpha' and props[0].value == 1
    assert props[1].name == 'b' and props[1].tex_name == r'\beta' and props[1].value == 2
    assert props[2].name == 'c' and props[2].tex_name == r'\gamma' and props[2].value == 3


    # TypeError is raised if any of the names passed are not strings
    for a, b in islice(combinations(valid_object_names, 2), 10):
        for c in non_strings:
            if isinstance(c, (int, float)):
                continue
            for a, b, c in permutations([a, b, c]):
                with pytest.raises(TypeError):
                    create_coordinate(a, b, c)


    # ValueError is raised if any of the names passed are not valid
    for a, b in islice(combinations(valid_object_names, 2), 10):
        for c in invalid_object_names:
            if isinstance(c, (int, float)):
                continue
            for a, b, c in permutations([a, b, c]):
                with pytest.raises(ValueError):
                    create_coordinate(a, b, c)


    # TypeError is raised if any of the latex names are not strings
    for a, b in islice(combinations(strings, 2), 10):
        for c in non_strings:
            for a, b, c in permutations([a, b, c]):
                with pytest.raises(TypeError):
                    create_coordinate(tex_name=a, vel_tex_name=b, acc_tex_name=c)


    # TypeError is raised if any of the initial numeric values are not valid
    for a, b in islice(combinations(valid_numeric_values, 2), 10):
        for c in invalid_numeric_values:
            for a, b, c in permutations([a, b, c]):
                with pytest.raises(TypeError):
                    create_coordinate('a', value=a, vel_value=b, acc_value=c)


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
