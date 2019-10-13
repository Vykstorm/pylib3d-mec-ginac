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
from src.pxd.ctensor3D       cimport Tensor3D       as c_Tensor3D
from src.pxd.cpoint          cimport Point          as c_Point
from src.pxd.cframe          cimport Frame          as c_Frame
from src.pxd.csolid          cimport Solid          as c_Solid
from src.pxd.cwrench3D       cimport Wrench3D       as c_Wrench3D



######## C++ GiNaC imports ########

from src.pxd.ginac.cnumeric cimport numeric as c_numeric
from src.pxd.ginac.cexpr    cimport ex      as c_ex
from src.pxd.ginac.cbasic   cimport basic   as c_basic
from src.pxd.ginac.cmatrix  cimport matrix  as c_ginac_matrix

# Printing classes & functions
from src.pxd.ginac.cprint cimport print_context  as c_ginac_printer
from src.pxd.ginac.cprint cimport print_python   as c_ginac_python_printer
from src.pxd.ginac.cprint cimport print_latex    as c_ginac_latex_printer
from src.pxd.ginac.cprint cimport set_print_func as c_ginac_set_print_func

# Symbolic math functions
from src.pxd.ginac.cmath cimport pow as c_pow





######## Python imports ########

# Collections
from collections import OrderedDict
from collections.abc import Iterable, Mapping, Sized

# Utilities
from functools import partial, partialmethod, wraps
from itertools import chain, starmap, repeat
from operator import attrgetter
from warnings import warn
from abc import ABC
from types import MethodType

# Math
from math import floor


# Third party libraries
from asciitree import LeftAligned
from tabulate import tabulate
