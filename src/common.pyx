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




######## C helper methods, variables & types ########


# C type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list

# C type alias representing a list of bases (std::vector[Base*])
ctypedef c_vector[c_Base*] c_base_list

# Same for std::vector[Matrix*]
ctypedef c_vector[c_Matrix*] c_matrix_list
