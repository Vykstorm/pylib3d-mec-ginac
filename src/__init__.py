'''
Author: Víctor Ruiz Gómez
Description:
Public API of the pylib3d_mec_ginac library.
'''


# The next variable will contain all public API methods & classes
__all__ = []

# Add extra classes & methods (core submodule)
from .core import __all__ as _core_api
from .core import *
__all__.extend(_core_api)


# Add extra classes & methods (drawing submodule)
try:
    from .drawing import __all__ as _drawing_api
    from .drawing import *
    __all__.extend(_drawing_api)
except ImportError:
    # No problem, graphical environment was not installed
    pass


# Apply default runtime configuration
from .config import runtime_config
set_atomization_state(runtime_config.ATOMIZATION)
set_gravity_direction(runtime_config.GRAVITY_DIRECTION)
