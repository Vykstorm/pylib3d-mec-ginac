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
from .drawing import __all__ as _drawing_api
from .drawing import *
__all__.extend(_drawing_api)


# Add extra classes & methods (ui submodule)
from .ui import __all__ as _ui_api
from .ui import *
__all__.extend(_ui_api)


# Add extra classes & methods (utils submodule)
from .utils import __all__ as _utils_api
from .utils import *
__all__.extend(_utils_api)


# Apply default runtime configuration
from .config import runtime_config
set_atomization_state(runtime_config.ATOMIZATION)
set_gravity_direction(runtime_config.GRAVITY_DIRECTION)
