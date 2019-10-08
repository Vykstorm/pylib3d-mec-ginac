'''
Author: Víctor Ruiz Gómez
Description:
This module defines internal helper routines to validate & parse input arguments of the public API functions.
'''

from collections.abc import Iterable
from inspect import Signature, Parameter
from re import match



def _parse_text(text):
    '''
    Check that input argument is a string or bytes object. If not, raises
    TypeError. The return value is always the input converted as a bytes object.
    '''
    if not isinstance(text, (str, bytes)):
        raise TypeError
    if isinstance(text, str):
        text = text.encode()
    return text




def _parse_name(name, check_syntax=False):
    '''
    Check that input argument is a valid name for numeric symbols, vectors, matrices, ...

    :param name: The name to be validated
    :param check_syntax: If True, the name syntax will also be validated
        Name should be composed with one ore more alphanumeric chars and underscores. Also, the
        first character cannot be a digit.

    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid name
    :returns: The input argument converted to a bytes object on success
    :rtype: bytes
    '''
    try:
        name = _parse_text(name)
    except TypeError:
        raise TypeError('Name must be a str or bytes object')

    if check_syntax and not match(b'^[a-zA-Z_]\w*$', name):
        raise ValueError(f'"{name.decode()}" is not a valid name')

    return name




def _parse_symbol_type(kind):
    '''
    Check that input argument is a valid numeric symbol type, that is, it must be
    equal to one the next values:
    'parameter', 'input', 'joint_unknown', 'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration'

    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid symbol type.
    :returns: The input argument string converted to bytes on success
    :rtype: bytes
    '''
    try:
        kind = _parse_text(kind)
    except TypeError:
        raise TypeError('Symbol type must be a str or bytes object')

    if kind not in _symbol_types:
        raise ValueError(f'Invalid "{kind.decode()}" symbol type')
    return kind




def _parse_numeric_value(value):
    '''
    Convert the input argument to a float value.
    It invokes __float__ metamethod of the input argument if it is not a float object.
    If it doesnt have such method defined, it raises TypeError
    '''
    if not isinstance(value, float):
        try:
            value = float(value)
        except:
            raise TypeError(f'Invalid numeric value')
    return value




def _apply_signature(params, defaults, args=[], kwargs={}):
    '''
    This method emulates the binding process of arbitrary positional and keyword arguments to
    a function signature.

    :param params: Must be a list of strings indicating the name of the parameters
        to bind the input arguments
    :param defaults: Its a dictionary where keys are parameter names and values, their default
        values
    :param args: The input positional arguments to bind to the parameters
    :param kwargs: The input keyword arguments to bind to the parameters
    :rtype: A tuple with the bounded arguments to the parameters specified
    :raises TypeError: If the input positional and keyword arguments cannot be binded to the
        given parameters

    :Example:

    >>> a, b = _apply_signature(
    >>>    ['a', 'b'],
    >>>    {'b': 2},
    >>>    args=[1]
    >>> )
    >>> print(a, b)
    1, 2

    >>> x, y = _apply_signature(['x', 'y'], {}, args=[], kwargs={'x':1})
    TypeError: missing a required argument: 'y'
    '''
    assert isinstance(params, Iterable)
    assert isinstance(defaults, dict)

    sig = Signature(
        parameters=[Parameter(param, Parameter.POSITIONAL_OR_KEYWORD, default=defaults.get(param, Parameter.empty)) for param in params]
    )
    bounded_args = sig.bind(*args, **kwargs)
    bounded_args.apply_defaults()
    return bounded_args.args
