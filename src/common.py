'''
Author: Víctor Ruiz Gómez
Description: This file defines recurrent Python methods used by multiple .pyx
modules on this library
'''

from inspect import Signature, Parameter
from collections.abc import Iterable


def _apply_signature(params, defaults, args, kwargs):
    assert isinstance(params, Iterable)
    assert isinstance(defaults, dict)

    sig = Signature(
        parameters=[Parameter(param, Parameter.POSITIONAL_OR_KEYWORD, default=defaults.get(param, Parameter.empty)) for param in params]
    )
    bounded_args = sig.bind(*args, **kwargs)
    bounded_args.apply_defaults()
    return bounded_args.args
