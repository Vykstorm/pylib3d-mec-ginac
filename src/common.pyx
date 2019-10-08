'''
Author: Víctor Ruiz Gómez
Description: This file contains all Cython/Python imports used by the extension
modules and helper methods/variables/types
'''



######## C type aliases ########

# C type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list

# C type alias representing a list of bases (std::vector[Base*])
ctypedef c_vector[c_Base*] c_base_list

# Same for std::vector[Matrix*]
ctypedef c_vector[c_Matrix*] c_matrix_list



######## C helper functions ########

cdef Expr _expr_from_c(c_ex x):
    # Converts GiNac::ex to Python class Expr instance
    expr = Expr()
    expr._c_handler = x
    return expr


cdef Matrix _matrix_from_c(c_Matrix* x):
    # Converts C++ Matrix object to Python class Matrix instance
    # (it doesnt make a copy, only stores the given pointer to the C++ matrix)
    mat = Matrix()
    mat._c_handler, mat._owns_c_handler = x, False
    return mat


cdef Matrix _matrix_from_c_value(c_Matrix x):
    # Converts C++ Matrix object to Python class Matrix instance
    # It performs a copy of the given C++ matrix
    mat = Matrix()
    cdef c_Matrix* c_mat = new c_Matrix(x.get_matrix())
    c_mat.set_name(x.get_name())

    mat._c_handler, mat._owns_c_handler = c_mat, True
    return mat


cdef Vector3D _vector_from_c(c_Vector3D* x):
    # Converts C++ Vector3D object to Python class Vector3D instance
    # It doesnt make a copy of the contents of the C++ Vector
    v = Vector3D()
    v._c_handler, v._owns_c_handler = x, False
    return v


cdef Vector3D _vector_from_c_value(c_Vector3D x):
    # Converts C++ Vector3D object to Python class Vector3D instance
    # It performs a copy of the contents of the given C++ Vector3D
    v = Vector3D()
    v._c_handler = new c_Vector3D(x.get_Name(), x.get(0, 0), x.get(1, 0), x.get(2, 0), x.get_Base())
    v._owns_c_handler = True
    return v


cdef Tensor3D _tensor_from_c(c_Tensor3D* x):
    # Converts C++ Tensor3D object to Python class Tensor3D instance
    # It doesnt make a copy of the contents of the C++ tensor
    tensor = Tensor3D()
    tensor._c_handler, tensor._owns_c_handler = x, False
    return tensor


cdef Tensor3D _tensor_from_c_value(c_Tensor3D x):
    # Convert C++ Tensor3D object to Python class Tensor3D instance
    # It perform a copy of the contents of the given C++ Vector3D
    tensor = Tensor3D()
    tensor._c_handler = new c_Tensor3D(x, x.get_Base())
    tensor._c_handler.set_name(x.get_name())
    tensor._owns_c_handler = True
    return tensor




cdef _ginac_print_ex(c_ex x, bint latex=0):
    # Prints a GiNaC::ex to a Python unicode string
    # The expression will be formatted with latex if latex is set to True
    cdef c_ginac_printer* c_printer
    if latex:
        c_printer = new c_ginac_latex_printer(c_sstream())
    else:
        c_printer = new c_ginac_python_printer(c_sstream())

    x.print(c_deref(c_printer))
    text = (<bytes>(<c_sstream*>&c_printer.s).str()).decode()
    del c_printer
    return text





######## Python helper variables ########

## The next variables are used to auto-generate System.get_* methods (getters)

# All numeric symbol types
_symbol_types = frozenset(map(str.encode, (
    'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration',
    'parameter', 'joint_unknown', 'input'
)))

# All symbol types that cannot be created by the user (they are generated
# automatically when other kind of symbols are created)
_derivable_symbol_types = frozenset(map(str.encode, (
    'velocity', 'acceleration', 'aux_velocity', 'aux_acceleration'
)))

# All geometric types
_geom_obj_types = frozenset(map(str.encode, (
    'base', 'matrix', 'vector', 'point', 'frame'
)))
