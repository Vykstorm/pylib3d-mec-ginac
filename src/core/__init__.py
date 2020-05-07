'''
Author: Víctor Ruiz Gómez
Description: This file defines the public API of the core submodule
'''

## Internal imports (to execute this script)

# Standard imports
from functools import wraps
from re import fullmatch
from ..drawing.scene import Scene

# Extension imports
import lib3d_mec_ginac_ext as _cython_ext

# Module imports
from .system import System, get_default_system, set_default_system
from .integration import NumericIntegration
from .assembly import AssemblyProblemSolver
from ..drawing.simulation import Simulation
from ..config import runtime_config



# This variable will store all the public classes & methods
__all__ = []


# This only has effect with python>=3.7 (PEP 562)
# It "hides" variables starting with _ from the public API
def __getattr__(name):
    if name.startswith('_') or name not in __all__:
        raise AttributeError(f'{name} is not defined in the pylib3d_mec_ginac library API')
    return globals()[name]

def __dir__():
    return __all__.copy()




# Add cython extension classes, functions
for name in dir(_cython_ext):
    if name.startswith('_'):
        continue
    obj = getattr(_cython_ext, name)
    if not callable(obj):
        continue
    if obj.__module__ != _cython_ext.__name__:
        continue
    __all__.append(name)
    globals()[name] = obj

# Add symbolic math constants
for name in ('pi', 'euler', 'tau'):
    sym_cte, num_cte = getattr(_cython_ext, name.title()), getattr(_cython_ext, name)
    __all__.extend([name, name.title()])
    globals()[name] = num_cte
    globals()[name.title()] = sym_cte

E, e = _cython_ext.Euler, _cython_ext.euler
__all__.extend(['e', 'E'])




# Add classes & functions from core submodule
__all__.extend([
    'System', 'get_default_system', 'set_default_system',
    'NumericIntegration', 'AssemblyProblemSolver'
])





# Expose get_*, new_*, set_* methods of the default system object (add them as global functions)
def _create_system_global_func(method):
    @wraps(method)
    def func(*args, **kwargs):
        return method(get_default_system(), *args, **kwargs)
    return func

for name in dir(System):
    if name == 'set_as_default':
        continue
    if not any(map(name.startswith, ('get_', 'set_', 'new_', 'has_', 'reduced_'))) and\
    not any(map(lambda pattern: fullmatch(pattern, name),
        [r'\w+_point_branch', r'rotation_\w+', r'position_\w+', r'angular_\w+',
        r'velocity_\w+', r'acceleration_\w+', 'twist', 'derivative', 'dt', 'jacobian',
        'diff', 'unatomize', r'\w+_wrench', r'export_\w+', r'compile_\w+',
        'save_state', 'restore_previous_state', 'evaluate']
    )):
        continue

    __all__.append(name)
    globals()[name] = _create_system_global_func(getattr(System, name))



# Expose methods of the 3d scene manager associated to the default system object (add them as global functions)
def _create_scene_global_func(method):
    @wraps(method)
    def func(*args, **kwargs):
        return method(get_default_system().get_scene(), *args, **kwargs)
    return func

for name in dir(Scene):
    if not any(map(name.startswith, ['draw_', 'get_', 'set_', 'is_', 'are_'])) and\
        name not in (
            'start_simulation', 'stop_simulation',
            'resume_simulation', 'pause_simulation', 'purge_drawings', 'record_simulation',
            'toogle_drawings', 'show_grid', 'hide_grid'
            ):
        continue
    __all__.append(name)
    globals()[name] = _create_scene_global_func(getattr(Scene, name))



# Expose methods of the simulation attached the scene instance associated to the default system object
def _create_simulation_global_func(method):
    @wraps(method)
    def func(*args, **kwargs):
        return method(get_default_system()._scene._simulation, *args, **kwargs)
    return func

for name in dir(Simulation):
    if not any(map(lambda pattern: fullmatch(pattern, name),
        [r'\w*integration\w*', 'assembly_problem']
    )):
        continue

    __all__.append(name)
    globals()[name] = _create_simulation_global_func(getattr(Simulation, name))
