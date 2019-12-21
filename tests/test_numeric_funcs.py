


import pytest
from pytest import approx
from lib3d_mec_ginac import *
from itertools import chain
import numpy as np
from itertools import product
from random import random, randrange


######## Test ########

def test_numeric_funcs_evaluation_return_type():
    s = System()
    a, b, c, d = s.new_param('a', 1), s.new_param('b', 2), s.new_param('c', 3), s.new_param('d', 4)
    h, i = s.new_input('h', 5), s.new_input('i', 6)
    j, k = s.new_joint_unknown('j', 7), s.new_joint_unknown('k', 8)
    l, dl, ddl = s.new_coordinate('l', 9)
    p, dp, ddp = s.new_aux_coordinate('p', 10)

    matrices = [
        Matrix([
            [a, b],
            [c, d]
        ]),
        Matrix([[0]]),
        Matrix([
            [a ** 2, i + 1, l - 1],
            [b * 2, h / 2, p + a],
            [j - a, k * a, c / a]
        ]),
        Matrix([
            [l, dl, ddl],
            [p, dp, ddp]
        ]),
        Matrix([[1, Pi, Euler, a, Tau]])
    ]

    funcs = tuple(chain([s.get_numeric_function(matrices[0])], map(s.get_numeric_function, matrices[1:])))

    for func, matrix in zip(funcs, matrices):
        # Test that numeric function evaluation result is a numpy ndarray with float64 values (a view)
        result = evaluate(func)
        assert isinstance(result, np.ndarray)
        assert result.dtype == np.float64
        assert result.base is not None

        # The shape of the matrix is the same as the shape of the numeric function evaluation result
        assert matrix.shape == result.shape




def test_numeric_funcs_evaluation_values():
    # Test that checks if numeric function evaluation is performed correctly

    system = System()
    assert evaluate( system.get_numeric_func(Matrix([[0]])) )[0] == 0
    assert evaluate( system.get_numeric_func(Matrix([[Pi]])) )[0] == pi
    assert evaluate( system.get_numeric_func(Matrix([[Euler]])) )[0] == euler
    assert evaluate( system.get_numeric_func(Matrix([[Tau]])) )[0] == tau

    a = system.new_param('a')
    b, c = system.new_input('b'), system.new_joint_unknown('c')
    h, dh, ddh = system.new_coordinate('h')

    for atomization_state, c_optimized in product(('off', 'on'), (False, True)):
        set_atomization_state(atomization_state)

        func = system.get_numeric_func( Matrix([[a]]), c_optimized=c_optimized)
        for i in range(0, 10):
            a.value = random()
            assert evaluate(func)[0] == approx(a.value)

        func = system.get_numeric_func( Matrix( [[ a ** 2 + b, a ** 2 + c * b ]] ), c_optimized=c_optimized )

        for i in range(0, 10):
            a.value, b.value, c.value = randrange(10), randrange(10), randrange(5)
            result = evaluate( func ).flatten()

            assert result[0] == a.value ** 2 + b.value
            assert result[1] == a.value ** 2 + c.value * b.value

        func = system.get_numeric_func( Matrix( [[ h / 2 + dh, h / 2 - ddh ]] ), c_optimized=c_optimized )

        for i in range(0, 10):
            h.value, dh.value, ddh.value = randrange(10), randrange(10), randrange(5)
            result = evaluate( func ).flatten()
            assert result[0] == h.value / 2 + dh.value
            assert result[1] == h.value / 2 - ddh.value
