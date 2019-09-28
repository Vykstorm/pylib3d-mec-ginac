'''
Author: Víctor Ruiz Gómez

Public API of the pylib3d_mec_ginac library.
'''


# The next variable will contain all public API methods & classes
__all__ = []

# Import underline extension
import lib3d_mec_ginac_ext as _ext

# Other imports
from inspect import isclass, isfunction


# Get all definitions in the extension (add them to __all__ and globals())
for name in dir(_ext):
    if name.startswith('_'):
        continue
    obj = getattr(_ext, name)
    if not isclass(obj) and not isfunction(obj):
        continue
    if obj.__module__ != _ext.__name__:
        continue
    __all__.append(name)
    globals()[name] = obj

# Add extra classes & methods
from .system import System
__all__.append('System')



# This only has effect with python>=3.7 (PEP 562)
# It "hides" variables starting with _ from the public API
def __getattr__(name):
    if name.startswith('_') or name not in __all__:
        raise AttributeError(f'{name} is not defined in the pylib3d_mec_ginac library API')
    return globals()[name]

def __dir__():
    return __all__.copy()


# This will store the "default" system object.
_default_system = System()

# Expose get_* and new_*, set_* methods of the default system object (add them to __all__ and globals())
for name in dir(System):
    if not any(map(name.startswith, ('get_', 'set_', 'new_'))):
        continue
    method = getattr(_default_system, name)
    __all__.append(name)
    globals()[name] = method
