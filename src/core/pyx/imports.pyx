'''
Author: Víctor Ruiz Gómez
Description:
This module adds all the needed imports for all the .pyx modules.
This includes:
* Cython declarations from .pxd files to use the C++ standard library, GiNaC
and lib3d-mec-ginac classes & functions

* Python standard modules & third party libraries
'''



######## Cython internal library imports ########

cimport cython
from cython.operator import dereference as c_deref




######## C/C++ standard library imports ########

from libcpp.string cimport string as c_string
from libcpp.vector cimport vector as c_vector

# Math
from libc.math cimport modf as c_modf

# Output streams
from src.core.pxd.cpp cimport ostream as c_ostream
from src.core.pxd.cpp cimport stringstream as c_sstream



######## C++ lib3d-mec-ginac imports ########

# Classes
from src.core.pxd.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.core.pxd.csystem         cimport System         as c_System
from src.core.pxd.cbase           cimport Base           as c_Base
from src.core.pxd.cmatrix         cimport Matrix         as c_Matrix
from src.core.pxd.cvector3D       cimport Vector3D       as c_Vector3D
from src.core.pxd.ctensor3D       cimport Tensor3D       as c_Tensor3D
from src.core.pxd.cpoint          cimport Point          as c_Point
from src.core.pxd.cframe          cimport Frame          as c_Frame
from src.core.pxd.csolid          cimport Solid          as c_Solid
from src.core.pxd.cwrench3D       cimport Wrench3D       as c_Wrench3D


# Global functions
from src.core.pxd.cglobals        cimport atomization          as c_atomization
from src.core.pxd.cglobals        cimport gravity              as c_gravity
from src.core.pxd.cglobals        cimport unatomize            as c_unatomize
from src.core.pxd.cglobals        cimport subs                 as c_subs
from src.core.pxd.cglobals        cimport matrix_list_optimize as c_matrix_list_optimize




######## C++ GiNaC imports ########

from src.core.pxd.ginac.cnumeric cimport numeric as c_numeric
from src.core.pxd.ginac.cexpr    cimport ex      as c_ex
from src.core.pxd.ginac.cbasic   cimport basic   as c_basic
from src.core.pxd.ginac.csymbol  cimport symbol  as c_symbol
from src.core.pxd.ginac.cmatrix  cimport matrix  as c_ginac_matrix
from src.core.pxd.ginac.clst     cimport lst     as c_lst

# Utility functions
from src.core.pxd.ginac.cexpr cimport is_a as c_is_a
from src.core.pxd.ginac.cexpr cimport ex_to as c_ex_to

# Printing classes & functions
from src.core.pxd.ginac.cprint cimport print_context  as c_ginac_printer
from src.core.pxd.ginac.cprint cimport print_python   as c_ginac_python_printer
from src.core.pxd.ginac.cprint cimport print_latex    as c_ginac_latex_printer
from src.core.pxd.ginac.cprint cimport set_print_func as c_ginac_set_print_func

# Symbolic math functions
from src.core.pxd.ginac.cmath cimport pow as c_sym_pow
from src.core.pxd.ginac.cmath cimport sin as c_sym_sin, cos as c_sym_cos, tan as c_sym_tan

# Symbolic math constants
from src.core.pxd.ginac.cmath cimport Pi as c_sym_pi, Catalan as c_sym_catalan, Euler as c_sym_euler




######## Python imports ########

# Collections
from collections import OrderedDict, deque
from collections.abc import Iterable, Mapping, Sized

# Utilities
from functools import partial, partialmethod, wraps
from itertools import chain, starmap, repeat, product
from operator import attrgetter, methodcaller, add
from warnings import warn
from abc import ABC
from types import MethodType
from re import match, finditer, sub
from inspect import Signature, Parameter
import json

# Math
import math
from math import floor

# System & Import system
import sys, os
import subprocess
import importlib

# Third party libraries
from asciitree import LeftAligned
from tabulate import tabulate
import numpy as np
