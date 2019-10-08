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



######## Python helper methods ########

def _parse_text(text):
    '''
    Check that input argument is a string or bytes object. If not, raises
    TypeError. The return value is the input converted to a bytes object.
    '''
    if not isinstance(text, (str, bytes)):
        raise TypeError
    if isinstance(text, str):
        text = text.encode()
    return text


def _parse_name(name, check_syntax=False):
    '''
    Check that input argument is a valid name for numeric symbols, vectors, matrices, ...

    :param name: The name to be validated
    :param check_syntax: If True, the name syntax will be validated
        Name should be composed with one ore more alphanumeric chars and underscores. Also, the
        first character cannot be a digit.

    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid name
    :returns: The input argument converted to a bytes object on success
    :rtype: bytes
    '''
    try:
        name = _parse_text(name)
    except TypeError:
        raise TypeError('Name must be a str or bytes object')

    if check_syntax and not match(b'^[a-zA-Z_]\w*$', name):
        raise ValueError(f'"{name.decode()}" is not a valid name')

    return name



def _parse_tex_name(tex_name):
    '''
    Check that input argument is a valid latex name for numeric symbols, vector, matrices, ...
    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid latex name
    :returns: The input argument converted to a bytes object on success
    :rtype: bytes
    '''
    try:
        return _parse_text(tex_name)
    except TypeError:
        raise TypeError('Latex name must be a str or bytes object')



def _parse_symbol_type(kind):
    '''
    Check that input argument is a valid numeric symbol type. It raises an exception
    otherwise.

    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid symbol type.
    :returns: The input argument string converted to bytes on success
    :rtype: bytes

    '''
    try:
        kind = _parse_text(kind)
    except TypeError:
        raise TypeError('Symbol type must be a str or bytes object')

    if kind not in _symbol_types:
        raise ValueError(f'Invalid "{kind.decode()}" symbol type')
    return kind


def _parse_geom_obj_type(kind):
    '''
    Check that input argument is a valid geometric object type. It raises an exception
    otherwise.

    :raises TypeError: If the input argument is not str or bytes object
    :raises ValueError: If the input argument is not a valid geometric type.
    :returns: The input argument string converted to bytes on success
    :rtype: bytes
    '''
    try:
        kind = _parse_text(kind)
    except TypeError:
        raise TypeError('Geometric object type must be a str or bytes object')

    if kind not in _geom_obj_types:
        raise ValueError(f'Invalid "{kind.decode()}" geometric object type')
    return kind


def _parse_numeric_value(value):
    '''
    Convert the input argument to a float value.
    It invokes __float__ metamethod of the input argument if it is not a float object.
    If it doesnt have such method defined, it raises TypeError
    '''
    if not isinstance(value, float):
        try:
            value = float(value)
        except:
            raise TypeError(f'Invalid numeric value')
    return value


def _apply_signature(params, defaults, args, kwargs):
    '''
    This method emulates the binding process of arbitrary positional and keyword arguments to
    a function signature.

    :param params: Must be a list of strings indicating the name of the parameters
        to bind the input arguments
    :param defaults: Its a dictionary where keys are parameter names and values, the default
        parameter values
    :param args: The input positional arguments to bind to the signature
    :param kwargs: The input keyword arguments to bing to the signature
    :rtype: A tuple with the bounded arguments to the parameters specified
    '''
    assert isinstance(params, Iterable)
    assert isinstance(defaults, dict)

    sig = Signature(
        parameters=[Parameter(param, Parameter.POSITIONAL_OR_KEYWORD, default=defaults.get(param, Parameter.empty)) for param in params]
    )
    bounded_args = sig.bind(*args, **kwargs)
    bounded_args.apply_defaults()
    return bounded_args.args






_latin_to_greek_latex = {
    'a': r'\alpha',
    'b': r'\beta',
    'c': r'\gamma', 'C': r'\Gamma',
    'd': r'\delta', 'D': r'\Delta',
    'e': r'\varepsilon',
    'h': r'\eta',
    'i': r'\iota',
    'k': r'\kappa',
    'l': r'\lambda', 'L': r'\Lambda',
    'm': r'\mu',
    'n': r'\nu',
    'p': r'\rho',
    's': r'\sigma', 'S': r'\Sigma',
    't': r'\tau',
    'u': r'\upsilon', 'U': r'\Upsilon',
    'x': r'\chi'
}


def _gen_latex_name(name):
    '''
    Generate a latex name for the symbol name specified (this is used when the user doesnt
    specify the symbol latex name explicitly to autogenerate it).

    :Example:

    gen_latex_name('a') # '\\alpha'
    gen_latex_name('U') # '\\Upsilon'
    gen_latex_name('p_2') # '\\rho_2'
    gen_latex_name('s2') # '\\sigma_2'
    gen_latex_name('foo') # ''
    '''
    if not isinstance(name, (str, bytes)):
        raise TypeError('Name must be a str or bytes object')

    if isinstance(name, bytes):
        name = name.decode()

    result = match('^([a-zA-Z]+)_?(\d*)$', name)
    if not result:
        return (r'\textrm{' + name  + '}').encode()

    name, subindex = result.group(1), result.group(2)
    if name in _latin_to_greek_latex:
        name = _latin_to_greek_latex[name]
    else:
        name = r'\textrm{' + name + '}'

    return (name if not subindex else f'{name}_' + '{' + subindex + '}').encode()




def _print_latex_ipython(text):
    # Print latex code in Ipython.
    try:
        from IPython.display import display, Math
    except ImportError:
        raise ImportError('You must have installed IPython to render latex')
    display(Math(text))





######## Custom GiNaC print formatting ########

cdef void _c_ginac_print_numeric_latex(const c_numeric& num, const c_ginac_latex_printer& c, unsigned level):
    if not num.is_integer() and not num.is_rational() and not num.is_real():
        # For the moment, its supposed that we only work with integers, reals or rationals
        raise RuntimeError('Latex printing on numbers only supports integers, rationals and reals')

    if num.is_zero():
        c.s << 0
        return

    if num.is_rational():
        if num.denom().compare(c_numeric(1)) == 0:
            c.s << num.numer()
        else:
            c.s << <c_string>b'\\frac{'
            c.s << num.numer()
            c.s << <c_string>b'}{'
            c.s << num.denom()
            c.s << <c_string>b'}'
        return

    cdef double value = num.to_double()
    cdef double intpart
    if c_modf(value, &intpart) == 0.0:
        c.s << <long>value
    else:
        c.s << value


# Register the function above on GiNaC using set_print_func
c_ginac_set_print_func[c_numeric, c_ginac_latex_printer](_c_ginac_print_numeric_latex)
