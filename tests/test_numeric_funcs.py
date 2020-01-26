'''
Author: Víctor Ruiz Gómez
Description: This is a unitary test for the class NumericFunction
'''


######## Imports ########

from lib3d_mec_ginac import *
import pytest
import numpy as np
from functools import partial


######## Fixtures ########



######## Tests ########

@pytest.mark.filterwarnings("ignore")
def test_numeric_func_atomization_enabled():
    '''
    This test checks that the numeric function can be created and evauated numerically
    with atomization enabled
    '''
    sys = System()
    # Test numeric function evaluation with atomization enabled
    set_atomization_state('on')
    a, b = sys.new_parameter('a', 2), sys.new_input('b', 3)
    m = Matrix([a, a ** 2 + 1, (a - b) / 4, a * b], shape=[2, 2])
    func = sys.compile_numeric_function(m)
    output = evaluate(func)
    assert isinstance(output, np.ndarray) and output.dtype == np.float64
    assert output.shape == m.shape
    assert list(map(pytest.approx, output.flat)) == [ 2, 5, -0.25, 6 ]



@pytest.mark.filterwarnings("ignore")
def test_numeric_func_atomization_disabled():
    '''
    This test checks that the numeric function can be created and evauated numerically
    with atomization disabled
    '''
    sys = System()
    # Test numeric function evaluation with atomization enabled
    set_atomization_state('off')
    a, b = sys.new_parameter('a', 2), sys.new_input('b', 3)
    m = Matrix([a, a ** 2 + 1, (a - b) / 4, a * b], shape=[2, 2])
    func = sys.compile_numeric_function(m)
    output = evaluate(func)
    assert isinstance(output, np.ndarray) and output.dtype == np.float64
    assert output.shape == m.shape
    assert list(map(pytest.approx, output.flat)) == [ 2, 5, -0.25, 6 ]
