'''
Author: Víctor Ruiz Gómez

Public API of the pylib3d_mec_ginac library.
'''


# The next variable will contain all public API methods & classes
__all__ = []

# Import underline extension
import lib3d_mec_ginac_ext as _ext

# Get all definitions in the extension (add them to __all__ and globals())
for name in dir(_ext):
    if name.startswith('_'):
        continue
    obj = getattr(_ext, name)
    if obj.__module__ != _ext.__name__:
        continue
    __all__.append(name)
    globals()[name] = obj



# This only has effect with python>=3.7 (PEP 562)
# It "hides" variables starting with _ from the public API
def __getattr__(name):
    if name.startswith('_') or name not in __all__:
        raise AttributeError(f'{name} is not defined in the pylib3d_mec_ginac library API')
    return globals()[name]

def __dir__():
    return __all__.copy()
