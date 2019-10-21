'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::lst and all its methods
which are going to be used by this library
'''


######## Imports ########

from libcpp.list cimport list

from src.pxd.ginac.cbasic cimport basic
from src.pxd.ginac.cexpr  cimport ex



######## Class GiNaC::container  ########

cdef extern from "ginac/container.h" namespace "GiNaC":
    cdef cppclass container[C](basic):
        size_t nops() const
        ex     op(size_t i) const



######## Class GiNaC::lst ########

cdef extern from "ginac/lst.h" namespace "GiNaC":
    ctypedef container[list] lst
