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
from src.pxd.cpp cimport ostream as c_ostream
from src.pxd.cpp cimport stringstream as c_sstream



######## C++ lib3d-mec-ginac imports ########

from src.pxd.csymbol_numeric cimport symbol_numeric as c_symbol_numeric
from src.pxd.csystem         cimport System         as c_System
from src.pxd.cbase           cimport Base           as c_Base
from src.pxd.cmatrix         cimport Matrix         as c_Matrix
from src.pxd.cvector3D       cimport Vector3D       as c_Vector3D
from src.pxd.cpoint          cimport Point          as c_Point
from src.pxd.cframe          cimport Frame          as c_Frame
from src.pxd.ctensor3D       cimport Tensor3D       as c_Tensor3D




######## C++ GiNaC imports ########

from src.pxd.cginac cimport numeric as c_numeric
from src.pxd.cginac cimport ex      as c_ex
from src.pxd.cginac cimport basic   as c_basic
from src.pxd.cginac cimport matrix  as c_ginac_matrix

# Printing classes & functions
from src.pxd.cginac cimport print_context  as c_ginac_printer
from src.pxd.cginac cimport print_python   as c_ginac_python_printer
from src.pxd.cginac cimport print_latex    as c_ginac_latex_printer
from src.pxd.cginac cimport set_print_func as c_ginac_set_print_func

# Symbolic math functions
from src.pxd.cginac cimport pow as c_pow





######## Python imports ########

# Collections
from collections import OrderedDict
from collections.abc import Iterable

# Utilities
from functools import partial, partialmethod, wraps
from itertools import chain, starmap
from operator import attrgetter
from warnings import warn
from re import match
from abc import ABC
from types import MethodType
from inspect import Signature, Parameter

# Math
from math import floor

# Third party libraries
from asciitree import LeftAligned
from tabulate import tabulate
