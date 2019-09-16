

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef cppclass numeric:
        numeric(double value)

        double to_double() const
        const numeric real() const
        const numeric imag() const
