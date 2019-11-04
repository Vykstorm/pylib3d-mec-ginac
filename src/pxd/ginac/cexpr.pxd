'''
Author: Víctor Ruiz Gómez
Description: This file declares the C++ Class GiNaC::ex and all its methods
which are going to be used by this library
'''


######## Imports ########

from src.pxd.ginac.cprint cimport print_context
from src.pxd.ginac.cbasic cimport basic
from src.pxd.cvector3D cimport Vector3D
from src.pxd.ctensor3D cimport Tensor3D
from src.pxd.cwrench3D cimport Wrench3D



######## Class GiNaC::ex ########

cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        # Constructors
        ex() except +
        ex(const double) except +
        ex(const basic&) except +
        ex(long) except +

        # Queries
        bint is_equal(ex&)
        bint is_zero()

        # Evaluation
        ex eval() const

        # Arithmetic operations
        ex operator-()
        ex operator+()
        ex operator+(ex&)
        ex operator-(ex&)
        ex operator*(ex&)
        ex operator/(ex&)
        Vector3D operator*(Vector3D&)
        Tensor3D operator*(Tensor3D&)
        Wrench3D operator*(Wrench3D&)


        # Printing
        void print(print_context&, unsigned=0) const


    bint is_a[T](const ex&)
    T& ex_to[T](const ex&)
