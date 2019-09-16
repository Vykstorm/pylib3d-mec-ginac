

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef cppclass numeric:
        numeric(unsigned long value)
        numeric(double value)

        double to_double() const
