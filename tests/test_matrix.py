'''
Author: Vïctor Ruiz Gómez
Description: Unitary test for the class Matrix
'''


######## Imports ########

import pytest
from lib3d_mec_ginac import *




######## Tests ########


def test_constructor():
    '''
    This is a test for the Matrix class constructor
    '''
    pass


def test_block():
    '''
    This is a test for the static method ``block`` in the class Matrix.
    '''
    a = Matrix([
        [1, 2],
        [3, 4]
    ])
    b = Matrix([
        [5, 6],
        [7, 8]
    ])
    c = Matrix.block(1, 2, a, b)
    assert c.get_shape() == (2, 4)
    assert c.get_values() == [1, 2, 5, 6, 3, 4, 7, 8]
    c = Matrix.block(2, 1, a, b)
    assert c.get_shape() == (4, 2)
    assert c.get_values() == [1, 2, 3, 4, 5, 6, 7, 8]
    c = Matrix.block(2, 2, a, b, a, b)
    assert c.get_shape() == (4, 4)
    assert c.get_values() == [1, 2, 5, 6, 3, 4, 7, 8] * 2

    # The number of varadic arguments ( matrices ) may be equal to n*m
    with pytest.raises(ValueError):
        Matrix.block(1, 1, a, b)
    with pytest.raises(ValueError):
        Matrix.block(1, 2, a)
    with pytest.raises(ValueError):
        Matrix.block(2, 2, a, b, a)

    # All matrices in the same row block may have the same number of rows
    a, b = Matrix(shape=[2, 2]), Matrix(shape=[3, 2])
    with pytest.raises(TypeError):
        Matrix.block(1, 2, a, b)
    with pytest.raises(TypeError):
        Matrix.block(2, 2, a, b, a, b)

    # All matrices in the same column block may have the same number of columns
    a, b = Matrix(shape=[2, 2]), Matrix(shape=[2, 3])
    with pytest.raises(TypeError):
        Matrix.block(2, 1, a, b)
    with pytest.raises(TypeError):
        Matrix.block(2, 2, a, a, b, b)





def test_getset_methods(invalid_numeric_values):
    '''
    This is a test for the methods ``set`` & ``get`` in the class Matrix.
    '''
    m = Matrix([
        [1, 2, 1],
        [2, 4, 2],
        [5, 5, 5]
    ])
    assert m.get(0, 0) == 1
    assert m.get(0, 2) == 1
    assert m.get(1, 1) == 4
    assert m.get(2, 2) == 5
    assert m.get(-1, 0) == 5
    assert m.get(0, -2) ==  2
    m.set(0, 0, 2)
    m.set(0, 2, 3)
    m.set(1, 1, 4)
    m.set(2, 2, 5)
    m.set(-1, 0, 6)
    m.set(0, -2, 7)
    assert m.get(0, 0) == 2
    assert m.get(0, 2) == 3
    assert m.get(1, 1) == 4
    assert m.get(2, 2) == 5
    assert m.get(-1, 0) == 6
    assert m.get(0, -2) == 7


    # Same test but for a matrix with only one row
    m = Matrix([ 1, 2, 3, 4 ])
    assert m.get(0, 0) == 1
    assert m.get(0, 1) == 2
    assert m.get(0, 3) == 4
    assert m.get(0, -2) == 3
    assert m.get(0, -1) == 4
    assert m.get(0) == 1
    assert m.get(1) == 2
    assert m.get(-1) == 4
    m.set(0, 0, 5)
    m.set(0, 1, 6)
    m.set(2, 7)
    m.set(-1, 8)
    assert m.get(0, 0) == 5
    assert m.get(0, 1) == 6
    assert m.get(0, 3) == 8
    assert m.get(0, -2) == 7
    assert m.get(0, -1) == 8
    assert m.get(0) == 5
    assert m.get(1) == 6
    assert m.get(-1) == 8

    # Same as the above but for a matrix with only one column
    m = Matrix([ 1, 2, 3, 4 ], shape=[4, 1])
    assert m.get(0, 0) == 1
    assert m.get(1, 0) == 2
    assert m.get(3, 0) == 4
    assert m.get(-2, 0) == 3
    assert m.get(-1, 0) == 4
    assert m.get(0) == 1
    assert m.get(1) == 2
    assert m.get(-1) == 4
    m.set(0, 0, 5)
    m.set(1, 0, 6)
    m.set(2, 7)
    m.set(-1, 8)
    assert m.get(0, 0) == 5
    assert m.get(1, 0) == 6
    assert m.get(3, 0) == 8
    assert m.get(-2, 0) == 7
    assert m.get(-1, 0) == 8
    assert m.get(0) == 5
    assert m.get(1) == 6
    assert m.get(-1) == 8

    # If indices are wrongs, get & set raises IndexError
    m = Matrix(shape=[3,3])
    for i, j in [(3, 0), (0, 3), (3, 3), (-4, 0), (-4, 0)]:
        with pytest.raises(IndexError):
            m.get(i, j)

        with pytest.raises(IndexError):
            m.set(i, j, 0)

    # If value is not numeric or something that can be converted to an expression,
    # set raises ValueError
    for x in invalid_numeric_values:
        with pytest.raises(TypeError):
            m.set(0, 0, x)




def test_getset_operator(invalid_numeric_values):
    '''
    This is a test for the __getitem__ & __setitem__ metamethods in the class Matrix.
    '''
    m = Matrix([
        [1, 2, 1],
        [2, 4, 2],
        [5, 5, 5]
    ])
    assert m[0, 0] == 1
    assert m[0, 2] == 1
    assert m[1, 1] == 4
    assert m[2, 2] == 5
    assert m[-1, 0] == 5
    assert m[0, -2] ==  2
    m[0, 0] = 2
    m[0, 2] = 3
    m[1, 1] = 4
    m[2, 2] = 5
    m[-1, 0] = 6
    m[0, -2] = 7
    assert m[0, 0] == 2
    assert m[0, 2] == 3
    assert m[1, 1] == 4
    assert m[2, 2] == 5
    assert m[-1, 0] == 6
    assert m[0, -2] == 7


    # Same test but for a matrix with only one row
    m = Matrix([ 1, 2, 3, 4 ])
    assert m[0, 0] == 1
    assert m[0, 1] == 2
    assert m[0, 3] == 4
    assert m[0, -2] == 3
    assert m[0, -1] == 4
    assert m[0] == 1
    assert m[1] == 2
    assert m[-1] == 4
    m[0, 0] = 5
    m[0, 1] = 6
    m[2] = 7
    m[-1] = 8
    assert m[0, 0] == 5
    assert m[0, 1] == 6
    assert m[0, 3] == 8
    assert m[0, -2] == 7
    assert m[0, -1] == 8
    assert m[0] == 5
    assert m[1] == 6
    assert m[-1] == 8

    # Same as the above but for a matrix with only one column
    m = Matrix([ 1, 2, 3, 4 ], shape=[4, 1])
    assert m[0, 0] == 1
    assert m[1, 0] == 2
    assert m[3, 0] == 4
    assert m[-2, 0] == 3
    assert m[-1, 0] == 4
    assert m[0] == 1
    assert m[1] == 2
    assert m[-1] == 4
    m[0, 0] = 5
    m[1, 0] = 6
    m[2] = 7
    m[-1] = 8
    assert m[0, 0] == 5
    assert m[1, 0] == 6
    assert m[3, 0] == 8
    assert m[-2, 0] == 7
    assert m[-1, 0] == 8
    assert m[0] == 5
    assert m[1] == 6
    assert m[-1] == 8

    # If indices are wrongs, __getitem__ & __setitem__ raises IndexError
    m = Matrix(shape=[3,3])
    for i, j in [(3, 0), (0, 3), (3, 3), (-4, 0), (-4, 0)]:
        with pytest.raises(IndexError):
            m[i, j]

        with pytest.raises(IndexError):
            m[i, j] = 0

    # If value is not numeric or something that can be converted to an expression,
    # __setitem__ raises ValueError
    for x in invalid_numeric_values:
        with pytest.raises(TypeError):
            m[0, 0] = x





def test_iterator():
    '''
    This is a test for the __iter__ metamethod in the class Matrix
    '''
    sys = System()
    m = Matrix(shape=[3, 3], values=range(0, 9))
    assert list(m) == list(range(0, 9))




def test_subs():
    '''
    This is a test for the method ``subs`` in the class Matrix
    '''
    sys = System()
    a, b = sys.new_parameter('a'), sys.new_parameter('b')
    m = Matrix([ a, a ** 2, b ** 2, a + b ])
    assert m.subs(a, 1).get_values() == [1, 1, b ** 2, 1+b]
    assert m.subs(b, 2).get_values() == [a, a ** 2, 4, a+2]
    assert m.subs([a, b], 3).get_values() == [3, 9, 9, 6]




def test_transpose():
    '''
    This is a test for the method ``transpose`` in the class Matrix
    '''
    m = Matrix(values=range(0, 12), shape=[3, 4])
    p = m.transpose()
    assert p.get_shape() == (4, 3)
    assert p.transpose().get_values() == m.get_values()
