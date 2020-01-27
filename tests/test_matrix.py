'''
Author: Vïctor Ruiz Gómez
Description: Unitary test for the class Matrix
'''


######## Imports ########

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
    pass


def test_getset_methods():
    '''
    This is a test for the methods ``set`` & ``get`` in the class Matrix.
    '''
    pass


def test_getset_operator():
    '''
    This is a test for the __getitem__ & __setitem__ metamethods in the class Matrix.
    '''
    pass


def test_iterator():
    '''
    This is a test for the __iter__ metamethod in the class Matrix
    '''
    pass



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
