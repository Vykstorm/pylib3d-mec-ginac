'''
Author: Víctor Ruiz Gómez
Description:
Public API of the pylib3d_mec_ginac library.
'''


# The next variable will contain all public API methods & classes
__all__ = []

# Import underline Cython extension
import lib3d_mec_ginac_ext as _ext

# Other imports
from functools import wraps
from re import fullmatch


# Get all definitions in the extension (add them to __all__ and globals())
for name in dir(_ext):
    if name.startswith('_'):
        continue
    obj = getattr(_ext, name)
    if not callable(obj):
        continue
    if obj.__module__ != _ext.__name__:
        continue
    __all__.append(name)
    globals()[name] = obj

# Add extra classes & methods
from .core.system import System
__all__.append('System')



# This only has effect with python>=3.7 (PEP 562)
# It "hides" variables starting with _ from the public API
def __getattr__(name):
    if name.startswith('_') or name not in __all__:
        raise AttributeError(f'{name} is not defined in the pylib3d_mec_ginac library API')
    return globals()[name]

def __dir__():
    return __all__.copy()


# This variable will store the "default" system object.
_default_system = System()

# Expose get_*, new_*, set_* methods of the default system object (add them to __all__ and globals())
def _create_system_global_func(method):
    @wraps(method)
    def func(*args, **kwargs):
        return method(_default_system, *args, **kwargs)
    return func

for name in dir(System):
    if name == 'set_as_default':
        continue
    if not any(map(name.startswith, ('get_', 'set_', 'new_', 'has_', 'reduced_', 'draw_'))) and\
    not any(map(lambda pattern: fullmatch(pattern, name),
        [r'\w+_point_branch', r'rotation_\w+', r'position_\w+', r'angular_\w+',
        r'velocity_\w+', r'acceleration_\w+', 'twist', 'derivative', 'dt', 'jacobian',
        'diff', 'unatomize', r'\w+_wrench', 'evaluate']
    )):
        continue

    __all__.append(name)
    globals()[name] = _create_system_global_func(getattr(System, name))

# Expose draw_* methods of the default system object (add them to __all__ and globals())
from .drawing.scene import Scene as DrawingScene

def _create_scene_global_func(method):
    @wraps(method)
    def func(*args, **kwargs):
        return method(_default_system._scene, *args, **kwargs)
    return func

for name in dir(DrawingScene):
    if not name.startswith('draw_') and\
        name not in (
            'start_simulation', 'stop_simulation', 'resume_simulation', 'pause_simulation',
            'set_update_frequency', 'set_time_multiplier'
            ):
        continue
    __all__.append(name)
    globals()[name] = _create_scene_global_func(getattr(DrawingScene, name))





# Additional methods exposed to the api


def get_default_system():
    '''get_default_system() -> System
    Get the default system instance.

    :rtype: System
    '''
    return _default_system


def set_default_system(system):
    '''set_default_system(system: System)
    Set the default system instance

    :param System system: The system instance to be set as default
    :raises TypeError: If the input argument is not an instance of the class System
    '''
    global _default_system
    if not isinstance(system, System):
        raise TypeError('Input argument must be an instance of the class System')
    _default_system = system


__all__.extend(['get_default_system', 'set_default_system'])
