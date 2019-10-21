'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::lst and all its methods
which are going to be used by this library
'''


######## Imports ########


######## Class GiNaC::lst ########

cdef extern from "ginac/lst.h" namespace "GiNaC":
    cdef cppclass lst:
        pass
