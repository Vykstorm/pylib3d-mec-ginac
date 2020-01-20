
######## Imports ########

from lib3d_mec_ginac import *
from math import floor
import pytest




def test_symbol_value_setget(invalid_numeric_values, non_strings):
    '''
    This function is a test for the methods ``get_value`` and ``set_value`` in the
    class System
    '''
    sys = System()
    t, g = sys.get_symbol('t'), sys.get_symbol('g')


    # Set the value of a symbol ( specify the symbol as an instance of the class SymbolNumeric )
    sys.set_value(t, 2)
    sys.set_value(g, 3)
    assert floor(sys.get_value(t)) == 2 and floor(sys.get_value(g)) == 3

    # Set the value of a symbol ( specify the symbol with its name )
    sys.set_value('t', 3)
    sys.set_value('g', 2)
    assert floor(sys.get_value('t') == 3) and floor(sys.get_value('g')) == 2

    # set_value and get_value raises IndexError if the first argument is a string and its
    # not the name of any symbol in the system
    with pytest.raises(IndexError):
        sys.set_value('foo', 1)

    with pytest.raises(IndexError):
        sys.get_value('bar')

    # set_value raises TypeError if the numeric value is not float nor int
    for x in invalid_numeric_values:
        with pytest.raises(TypeError):
            sys.set_value(t, x)

    # Raises TypeError if the first argument of get_value or set_value is not a SymbolNumeric
    # nor string
    for x in non_strings:
        with pytest.raises(TypeError):
            sys.set_value(x, 1)

        with pytest.raises(TypeError):
            sys.get_value(x)



######## Tests for getter methods ########


def test_get_symbol(non_strings):
    '''
    This function is a test for the method ``get_symbol`` in the class System
    '''
    sys = System()

    # get_symbol returns SymbolNumeric instances
    t = sys.get_symbol('t')
    assert isinstance(t, SymbolNumeric)

    # get_symbol raises TypeError if the input argument is not string
    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_symbol(x)

    # get_symbol raises IndexError if the input argument is not the name of
    # an already existing symbol in the system
    with pytest.raises(IndexError):
        sys.get_symbol('foo')




def test_has_symbol(non_strings):
    '''
    This function is a test for the method ``has_symbol`` in the class System
    '''
    sys = System()

    # has_symbol returns True if a symbol with the given name exists, False otherwise
    assert sys.has_symbol('t') and sys.has_symbol('g')
    assert not sys.has_symbol('foo') and not sys.has_symbol('bar')

    # has_symbol raises TypeError if the input argument is not a string
    for x in non_strings:
        with pytest.raises(TypeError):
            sys.has_symbol(x)




def test_get_base():
    '''
    This function is a test for the method ``get_base`` in the class System
    '''
    pass


def test_get_matrix():
    '''
    This function is a test for the method ``get_matrix`` in the class System
    '''
    pass


def test_get_vector():
    '''
    This function is a test for the method ``get_vector`` in the class System
    '''
    pass


def test_get_tensor():
    '''
    This function is a test for the method ``get_tensor`` in the class System
    '''
    pass


def test_get_point():
    '''
    This function is a test for the method ``get_point`` in the class System
    '''
    pass


def test_get_solid():
    '''
    This function is a test for the method ``get_solid`` in the class System
    '''
    pass


def test_get_wrench():
    '''
    This function is a test for the method ``get_wrench`` in the class System
    '''
    pass


def test_get_frame():
    '''
    This function is a test for the method ``get_frame`` in the class System
    '''
    pass




######## Tests for construction methods ########


def test_new_parameter():
    '''
    This function is a test for the method ``new_parameter`` in the class System
    '''
    pass


def test_new_joint_unknown():
    pass


def test_new_input():
    pass


def test_new_coordinate():
    pass


def test_new_aux_coordinate():
    pass


def test_new_base():
    pass


def test_new_matrix():
    pass


def test_new_vector():
    pass


def test_new_tensor():
    pass


def test_new_point():
    pass


def test_new_solid():
    pass


def test_new_wrench():
    pass


def test_new_frame():
    pass