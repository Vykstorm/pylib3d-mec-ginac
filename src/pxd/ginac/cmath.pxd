'''
Author: Víctor Ruiz Gómez
Description:
This file declares the GiNaC symbolic functions pow, sin, cos, ... in order to
be used by this library
'''

######## Imports ########

from src.pxd.ginac.cexpr cimport ex



######## Math with symbolic expressions ########

cdef extern from "ginac/power.h" namespace "GiNaC":
    cdef ex pow(ex&, ex&)
