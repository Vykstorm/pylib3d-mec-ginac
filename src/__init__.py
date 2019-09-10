'''
Author: Víctor Ruiz Gómez

Public API of the pylib3d_mec_ginac library.
'''


# This variable lists all variables in the public API
__all__ = ['System']


# This only has effect with python>=3.7 (PEP 562)
# It "hides" variables starting with _ from the public API
def __getattr__(name):
    if name.startswith('_') or name not in __all__:
        raise AttributeError(f'{name} is not defined in the pylib3d_mec_ginac library API')
    return getattr(globals(), name)

def __dir__():
    return __all__.copy()


# Import extension definitions
import lib3d_mec_ginac_ext as _ext

# Class System
System = _ext.SystemWrapper
