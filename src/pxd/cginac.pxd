'''
Author: Víctor Ruiz Gómez
Description: This file declares all classes, functions & methods of GiNaC
C++ library that are going to be used by this library.
'''


######## Imports ########


# Imports from the standard library
from libcpp.string cimport string


# Imports from other .pxd definition files
from src.pxd.cpp cimport ostream



######## Class GiNaC::print_context & its subclasses ########

cdef extern from "ginac/print.h" namespace "GiNaC":
    cdef cppclass print_context:
        ostream& s

    cdef cppclass print_python(print_context):
        print_python(ostream& os) except +

    cdef cppclass print_latex(print_context):
        print_latex(ostream& os) except +



######## Class GiNaC::basic ########

cdef extern from "ginac/basic.h" namespace "GiNaC":
    cdef cppclass basic:
        pass



######## Class GiNaC::ex ########

cdef extern from "ginac/ex.h" namespace "GiNaC":
    cdef cppclass ex:
        # Constructors
        ex() except +
        ex(const double value) except +
        ex(const basic& value) except +

        # Evaluation
        ex eval() const

        # Arithmetic operations
        ex operator-()
        ex operator+()
        ex operator+(ex& other)
        ex operator-(ex& other)
        ex operator*(ex& other)
        ex operator/(ex& other)

        # Printing
        void print(print_context&, unsigned level=0) const



######## Class GiNaC::symbol ########

cdef extern from "ginac/symbol.h" namespace "GiNaC":
    cdef cppclass symbol:
        void set_name(string& name)


######## Class GiNaC::numeric ########

cdef extern from "ginac/ginac.h" namespace "GiNaC":
    cdef cppclass numeric(basic):
        numeric(double value)

        bint is_integer() const
        bint is_rational() const
        bint is_real() const
        bint is_zero()
        double to_double() const
        long to_long() const
        const numeric real() const
        const numeric imag() const
        const numeric numer() const
        const numeric denom() const


######## Class GiNaC::matrix ########

cdef extern from "ginac/matrix.h" namespace "GiNaC":
    cdef cppclass matrix(basic):
        pass


######## Class GiNaC::power ########

cdef extern from "ginac/power.h" namespace "GiNaC":
    cdef ex pow(ex& base, ex& exp)



######## Function set_print_func ########

cdef extern from "ginac/registrar.h" namespace "GiNaC":
    cdef void set_print_func[T, C](void (*func)(const T&, const C&, unsigned))
