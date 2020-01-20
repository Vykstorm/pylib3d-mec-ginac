
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




def test_get_base(non_strings):
    '''
    This function is a test for the method ``get_base`` in the class System
    '''
    sys = System()

    base = sys.get_base('xyz')
    assert isinstance(base, Base)

    with pytest.raises(IndexError):
        sys.get_base('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_base(x)



def test_get_vector(non_strings):
    '''
    This function is a test for the method ``get_vector`` in the class System
    '''
    sys = System()
    sys.new_vector('v', 1, 2, 3)
    sys.new_vector('w', 4, 5, 6)

    v, w = sys.get_vector('v'), sys.get_vector('w')
    assert isinstance(v, Vector3D) and isinstance(w, Vector3D)

    with pytest.raises(IndexError):
        sys.get_vector('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_vector(x)




def test_get_tensor(non_strings):
    '''
    This function is a test for the method ``get_tensor`` in the class System
    '''
    sys = System()
    sys.new_tensor('p')
    sys.new_tensor('q')

    v, w = sys.get_tensor('p'), sys.get_tensor('q')
    assert isinstance(v, Tensor3D) and isinstance(w, Tensor3D)

    with pytest.raises(IndexError):
        sys.get_tensor('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_tensor(x)





def test_get_point(non_strings):
    '''
    This function is a test for the method ``get_point`` in the class System
    '''
    sys = System()

    point = sys.get_point('O')
    assert isinstance(point, Point)

    with pytest.raises(IndexError):
        sys.get_point('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_point(x)




def test_get_solid(non_strings):
    '''
    This function is a test for the method ``get_solid`` in the class System
    '''
    sys = System()
    sys.new_base('b', 0, 1, 0)
    sys.new_param('m', 1)
    sys.new_vector('v', 0, 0, 1)
    sys.new_tensor('q')
    sys.new_solid('s', 'O', 'xyz', 'm', 'v', 'q')

    solid = sys.get_solid('s')
    assert isinstance(solid, Solid)

    with pytest.raises(IndexError):
        sys.get_solid('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_solid(x)



def test_get_wrench(non_strings):
    '''
    This function is a test for the method ``get_wrench`` in the class System
    '''
    sys = System()
    sys.new_base('Barm', 0, 1, 0)
    sys.new_param('m', 1)
    sys.new_vector('Oarm_Garm', 0, 0, 1, 'Barm')
    sys.new_tensor('Iarm', base='Barm')
    sys.new_solid('arm', 'O', 'Barm', 'm', 'Oarm_Garm', 'Iarm')
    sys.new_vector('f', 0, 1, 0, 'xyz')
    sys.new_vector('mt', 0, 0, 0, 'xyz')
    sys.new_point('p', position=new_vector('v', 0, 1, 2, 'xyz'))
    sys.new_wrench('w', 'f', 'mt', 'p', 'arm', 'Constraint')

    wrench = sys.get_wrench('w')
    assert isinstance(wrench, Wrench3D)

    with pytest.raises(IndexError):
        sys.get_wrench('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_wrench(x)





def test_get_frame(non_strings):
    '''
    This function is a test for the method ``get_frame`` in the class System
    '''
    sys = System()

    frame = sys.get_frame('abs')
    assert isinstance(frame, Frame)

    with pytest.raises(IndexError):
        sys.get_wrench('foo')

    for x in non_strings:
        with pytest.raises(TypeError):
            sys.get_wrench(x)



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



######## Tests for symbolic computation methods ########



def test_derivative():
    '''
    Test to check the function ``derivative`` in the class System
    '''
    sys = System()

    # We can pass an expression, matrix or vector as the first argument
    # The type of result will be the same as the input type.
    v = sys.new_vector('v')
    b = sys.get_base('xyz')
    f = sys.get_frame('abs')
    m = Matrix(shape=[2, 2])
    assert isinstance(sys.derivative(Expr(1)), Expr)
    assert isinstance(sys.derivative(v), Vector3D)
    assert isinstance(sys.derivative(m), Matrix)

    # base argument can only be specified if the first argument is a vector
    assert isinstance(sys.derivative(v, base=b), Vector3D)
    assert isinstance(sys.derivative(v, base='xyz'), Vector3D)

    with pytest.raises(TypeError):
        sys.derivative(Expr(1), base=b)

    with pytest.raises(TypeError):
        sys.derivative(m, base=b)

    # frame argument can only be specified if the first argument is a vector

    assert isinstance(sys.derivative(v, frame=f), Vector3D)
    assert isinstance(sys.derivative(v, frame='abs'), Vector3D)

    with pytest.raises(TypeError):
        sys.derivative(Expr(1), frame=f)

    with pytest.raises(TypeError):
        sys.derivative(m, frame=f)


    # base & frame arguments cannot be specified at the same time
    with pytest.raises(TypeError):
        sys.derivative(v, base=b, frame=f)


    # a very basic test
    # the next derivatives are computed:
    # x                dx/dt
    # 5             -> 0
    # 4*t           -> 4
    # 4*t**2        -> 8*t
    # t**3 + t ** 2 -> 3*t**2 + 2*t
    t = sys.get_time()
    derivatives = sys.derivative(
        Matrix([ 5, 4*t, 4*t**2, t**3+t**2 ])
    )
    assert derivatives.values == [0, 4, 8*t, 3*t**2 + 2*t]




def test_diff():
    pass


def test_jacobian():
    pass




######## Tests for wrench methods ########
