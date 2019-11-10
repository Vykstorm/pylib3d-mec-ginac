'''
Author: Víctor Ruiz Gómez
Description:
This file declares the GiNaC symbolic functions pow, sin, cos, ... in order to
be used by this library
'''

######## Imports ########

from src.core.pxd.ginac.cexpr cimport ex



######## Math with symbolic expressions ########

cdef extern from "ginac/power.h" namespace "GiNaC":
    cdef ex pow(ex&, ex&)



######## Trigonometric functions ########

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef ex sin(ex& x)
    cdef ex cos(ex& x)
    cdef ex tan(ex& x)
