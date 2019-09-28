'''
Author: Víctor Ruiz Gómez
Description: This file contains all Cython/Python imports used by the extension
modules and helper methods/variables/types
'''


######## Imports ########

# Import cython internal library
cimport cython
from cython.operator import dereference as c_deref

# C++ standard library imports
from libcpp.string cimport string as c_string
from libcpp.vector cimport vector as c_vector
from libcpp.map cimport map as c_map
from libcpp.utility cimport pair as c_pair
from src.pxd.cpp cimport stringstream as c_sstream

# Import lib3d-mec-ginac C++ classes
from src.pxd.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.pxd.csystem cimport System as c_System
from src.pxd.cbase cimport Base as c_Base
from src.pxd.cmatrix cimport Matrix as c_Matrix

# Import GiNaC C++ classes
from src.pxd.cginac cimport numeric as c_numeric
from src.pxd.cginac cimport ex as c_ex
from src.pxd.cginac cimport basic as c_basic
from src.pxd.cginac cimport print_python as c_print_context
from src.pxd.cginac cimport matrix as c_ginac_matrix


# Python imports (builtins)
from collections import OrderedDict
from collections.abc import Mapping, Iterable
from inspect import Signature, Parameter
from functools import partial, partialmethod, wraps
from itertools import chain
from operator import attrgetter
from math import floor

# Python imports (external libraries)
from asciitree import LeftAligned



######## C type aliases ########

# C type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list

# C type alias representing a list of bases (std::vector[Base*])
ctypedef c_vector[c_Base*] c_base_list

# Same for std::vector[Matrix*]
ctypedef c_vector[c_Matrix*] c_matrix_list



######## C helper functions ########

cdef Expr _expr_from_c(c_ex x):
    # Converts GiNac::ex to Python class Expr instance
    expr = Expr()
    expr._c_handler = x
    return expr


cdef Matrix _matrix_from_c(c_Matrix* x):
    # Converts C++ Matrix object to Python class Matrix instance
    m = Matrix()
    m._c_handler, m._owns_c_handler = x, False
    return m


######## Python helper variables ########

## The next variables are used to auto-generate System.get_* methods (getters)

# All numeric symbol types
_symbol_types = frozenset(map(str.encode, (
    'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration',
    'parameter', 'joint_unknown', 'input'
)))

# All symbol types that cannot be created by the user (they are generated
# automatically when other kind of symbols are created)
_derivable_symbol_types = frozenset(map(str.encode, (
    'velocity', 'acceleration', 'aux_velocity', 'aux_acceleration'
)))

# All geometric types
_geom_obj_types = frozenset(map(str.encode, (
    'base', 'matrix'
)))



######## Python helper methods ########


def _parse_symbol_type(kind):
    if not isinstance(kind, (str, bytes)):
        raise TypeError(f'Symbol type must be a str or bytes object')

    if isinstance(kind, str):
        kind = kind.encode()

    if kind not in _symbol_types:
        raise ValueError(f'Invalid "{kind.decode()}" symbol type')

    return kind


def _parse_symbol_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Symbol name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name


def _parse_symbol_tex_name(tex_name):
    if not isinstance(tex_name, (str, bytes)):
        raise TypeError(f'Symbol latex name must be a str or bytes object')

    if isinstance(tex_name, str):
        tex_name = tex_name.encode()

    return tex_name


def _parse_symbol_value(value):
    if not isinstance(value, float):
        try:
            value = float(value)
        except:
            raise TypeError(f'Invalid symbol numeric value')
    return value


def _parse_geom_obj_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Base name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name

def _parse_geom_obj_name(name):
    if not isinstance(name, (str, bytes)):
        raise TypeError(f'Name must be a str or bytes object')

    if isinstance(name, str):
        name = name.encode()

    return name


def _parse_geom_obj_type(kind):
    if not isinstance(kind, (str, bytes)):
        raise TypeError(f'Type must be a str or bytes object')

    if isinstance(kind, str):
        kind = kind.encode()

    if kind not in _geom_obj_types:
        raise ValueError(f'Invalid "{kind.decode()}" geometric object type')
    return kind


def _apply_signature(params, defaults, args, kwargs):
    assert isinstance(params, Iterable)
    assert isinstance(defaults, dict)

    sig = Signature(
        parameters=[Parameter(param, Parameter.POSITIONAL_OR_KEYWORD, default=defaults.get(param, Parameter.empty)) for param in params]
    )
    bounded_args = sig.bind(*args, **kwargs)
    bounded_args.apply_defaults()
    return bounded_args.args
