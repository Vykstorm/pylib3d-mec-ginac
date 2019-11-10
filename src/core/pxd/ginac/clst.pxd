'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::lst and all its methods
which are going to be used by this library
'''


######## Imports ########

from libcpp.list cimport list

from src.core.pxd.ginac.cbasic cimport basic
from src.core.pxd.ginac.cexpr  cimport ex



######## Class GiNaC::lst ########

cdef extern from "ginac/lst.h" namespace "GiNaC":
    #ctypedef container[list] lst
    cdef cppclass lst:
        size_t nops() const
        ex     op(size_t) const
        lst&   append(const ex&)
