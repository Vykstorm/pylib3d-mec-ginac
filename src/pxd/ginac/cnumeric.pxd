'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::numeric and all its methods that
are going to be used by this library
'''

######## Imports ########

from src.pxd.ginac.cbasic cimport basic



######## Class GiNaC::numeric ########

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef cppclass numeric(basic):
        numeric(double)
        numeric(long)

        bint is_integer() const
        bint is_rational() const
        bint is_real() const
        bint is_zero() const
        int compare(numeric& other) const

        double to_double() const
        long to_long() const
        const numeric real() const
        const numeric imag() const
        const numeric numer() const
        const numeric denom() const
