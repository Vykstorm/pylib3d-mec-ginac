

cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        ex(const double value) except +
