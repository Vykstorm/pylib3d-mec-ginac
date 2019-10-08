'''
Author: Víctor Ruiz Gómez
Description:
This module defines internal helper functions to print symbols, expressions and matrices
in latex or string format.
'''



######## Custom GiNaC latex print formatting ########

# This function will tell GiNaC how to format numeric values in latex format.
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


# Register the function above in GiNaC using set_print_func
c_ginac_set_print_func[c_numeric, c_ginac_latex_printer](_c_ginac_print_numeric_latex)




######## GiNaC expressions to latex ########


cdef _ginac_expr_to_latex(c_ex x):
    # Converts a GiNaC expression to a string using the latex printer
    cdef c_ginac_printer* c_printer = new c_ginac_latex_printer(c_sstream())
    x.print(c_deref(c_printer))
    text = (<bytes>(<c_sstream*>&c_printer.s).str()).decode()
    del c_printer
    return text






######## Latex printing on IPython  ########


cpdef _print_latex_ipython(str text):
    '''
    This function displays the given latex text on IPython.
    :param text: The latex text to be displayed
    :type text: str or bytes
    :parm TypeError: If the given text is not string or bytes
    :raises ImportError: If the library IPython couldnt be loaded
    '''
    try:
        from IPython.display import display, Math
    except ImportError:
        raise ImportError('You must have installed IPython to render latex')
    display(Math(text))




######## Expressions, Symbols and Matrices to latex ########


cpdef _symbol_to_latex(SymbolNumeric symbol):
    '''
    Converts a numeric symbol to latex.
    The latex name of the symbol is returned if its not an empty string.
    Otherwise, it returns the name of the symbol wrapped with a textrm statement: '\\textrm{name}'
    '''
    return symbol.get_tex_name() or r'\textrm{' + symbol.get_name()  + '}'



cpdef _expr_to_latex(Expr expr):
    '''
    Converts an expression to latex.
    It uses the routines provided by GiNaC behind the scenes.
    '''
    return _ginac_expr_to_latex(expr._c_handler)



cpdef _matrix_to_latex(Matrix matrix):
    '''
    Converts a matrix to latex.
    It uses the routines provided by GiNaC behind the scenes.
    '''
    assert isinstance(matrix, Matrix)
    return _ginac_expr_to_latex(c_ex(matrix._get_c_handler().get_matrix()))



def _to_latex(obj):
    # Converts any given object to latex
    if isinstance(obj, SymbolNumeric):
        return _symbol_to_latex(obj)
    if isinstance(obj, Expr):
        return _expr_to_latex(obj)
    if isinstance(obj, Matrix):
        return _matrix_to_latex(obj)

    if isinstance(obj, bytes):
        return obj.decode()
    if isinstance(obj, str):
        return obj
    return r'\textrm{' + str(obj) + '}'



def to_latex(*args):
    '''
    Convert one or more objects in a single latex inline formula.
    Objects can be of any kind; numeric symbols, expressions, matrices, vectors and tensors are
    printed nicely. The rest of objects are converted to a string using the metamethod
    __str__ and wrapped in a latex textrm statement: '\\textrm{str(object))}'


        :Example:

        >> to_latex(new_param('a', tex_name='\\alpha'))
        '\\alpha'

        >> u, x = new_param('u', tex_name='\\upsilon'), new_param('x', tex_name=r'\chi')
        >> to_latex(u, x)
        '\\upsilon\:\\chi'

        >> to_latex(u, '\\times', x, '=', u * x)
        '\\upsilon\\:\\times\\:\\chi\\:=\\: \\upsilon \\chi'

        >> to_latex(new_matrix(shape=[3, 3]))
        '\\left(\\begin{array}{ccc}0&0&0\\\\0&0&0\\\\0&0&0\\end{array}\\right)'

    '''
    return r'\:'.join(map(_to_latex, args))




def print_latex(*args):
    '''
    This method calls to_latex to convert the input arguments to an inline latex formula.
    Then, the formula is displayed on IPython.

    :raise ImportError: If IPython module couldnt be imported
    '''
    _print_latex_ipython(to_latex(*args))






######## Symbol latex name autogeneration ########

# This variable holds a mapping to translate the latin alphabet to greek (in latex)
# both upper and lowercase (its used by the method below)
# Note that 'r' prefix is used to tell python not to escape '\' characters: r'\' == '\\'
_latin_to_greek_latex = {
    'a': r'\alpha',
    'b': r'\beta',
    'c': r'\gamma',        'C': r'\Gamma',
    'd': r'\delta',        'D': r'\Delta',
    'e': r'\varepsilon',
    'h': r'\eta',
    'i': r'\iota',
    'k': r'\kappa',
    'l': r'\lambda',       'L': r'\Lambda',
    'm': r'\mu',
    'n': r'\nu',
    'p': r'\rho',
    's': r'\sigma',        'S': r'\Sigma',
    't': r'\tau',
    'u': r'\upsilon',      'U': r'\Upsilon',
    'x': r'\chi'
}


def _gen_latex_name(name):
    '''
    Generate a latex name for the symbol name specified (that is, when the user doesnt
    specify the symbol latex name explicitly to autogenerate it).

    * If the given name is a letter of the latin alphabet, it is translated to its
    corresponding greek letter in latex (if it has one):

        :Example:

        >>> gen_latex_name('a')
        '\\alpha'
        >>> gen_latex_name('U') #
        '\\Upsilon'

    * If the name satisfies the above condition but also has a suffix that consists
    of an optional underscore, followed by a number, its translated to latex as before and a subindex
    is added to it:

        :Example:

        >> get_latex_name('s_2')
        '\\sigma_2'
        >> gen_latex_name('s3')
        '\\sigma3'

    * If the name has more than one letter, the latex name is the given name
    wrapped in a textrm statement: '\\textrm{text}'

        :Example:

        >> gen_latex_name('foo')
        '\\textrm{foo}'

        # You can also add subindices to it:
        >> gen_latex_name('foo_2')
        '\\textrm{foo}_2'

    '''
    name = _parse_text(name)

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







######## GiNaC expressions to strings ########

cdef _ginac_expr_to_str(c_ex x):
    # Converts a GiNaC expression to a string
    cdef c_ginac_printer* c_printer = new c_ginac_python_printer(c_sstream())
    x.print(c_deref(c_printer))
    text = (<bytes>(<c_sstream*>&c_printer.s).str()).decode()
    del c_printer
    return text




######## Expressions, Symbols and Matrices to text (terminal mode) ########



cpdef _symbol_to_str(SymbolNumeric symbol):
    # Prints a numeric symbol to a string.
    return f'{symbol.get_name()} = {round(symbol.get_value(), 4)}'



cpdef _matrix_to_str(Matrix matrix):
    # Prints a matrix object to a string nicely

    values = tuple(map(str, matrix.get_values()))
    n, m = matrix.get_shape()
    if m == 1:
        m, n = n, 1

    col_sizes = [max([len(values[i*m + j]) for i in range(0, n)])+1 for j in range(0, m)]
    delimiters = '[]' if n == 1 or m == 1 else '\u2502'*2

    lines = []
    for i in range(0, n):
        line = ' '.join([values[i*m + j].rjust(col_size) for j, col_size in zip(range(0, m), col_sizes)])
        line = delimiters[0] + line + ' ' + delimiters[1]
        lines.append(line)

    if n > 1 and m > 1:
        # Insert decoratives
        row_width = len(lines[0]) - 2
        head = '\u256d' + ' '*row_width + '\u256e'
        tail = '\u2570' + ' '*row_width + '\u256f'
        lines.insert(0, head)
        lines.append(tail)

    return '\n'.join(lines)




cpdef _expr_to_str(Expr expr):
    '''
    Prints an expression to a string.
    It uses the GiNaC printing routines behind the scenes
    '''
    x = _ginac_expr_to_str(expr._c_handler)

    try:
        # Try to format the expression as a number (remove decimals if its integer)
        x = float(x)
        if floor(x) == x:
            x = floor(x)
        else:
            x = round(x, 4)
        return str(x)
    except:
        # Otherwise, returns the whole expression as-is
        return x



cpdef _base_to_str(Base base):
    # Prints a base object to a string
    s = f'Base {base.name}'

    if base.has_previous():
        ancestors = []
        prev = base.get_previous()
        ancestors.append(prev)
        while prev.has_previous():
            prev = prev.get_previous()
            ancestors.append(prev)

        s += ', ancestors: ' + ' -> '.join(map(attrgetter('name'), ancestors))

    return s




cpdef _point_to_str(Point point):
    # Prints a point object to a string
    #if self.has_previous():
    #    return f'Point "{self.name}", position = {self.offset} (base {self.offset.base.name}), previous = {self.previous.name}'
    if not point.has_previous():
        return 'Origin point'

    name = point.name
    previous_name = point.previous.name
    x, y, z = point.offset.x, point.offset.y, point.offset.z
    base_name = point.offset.base.name


    return tabulate([[
        point.name, x, y, z, base_name, previous_name
    ]], headers=('name', 'x', 'y', 'z', 'base', 'previous'), tablefmt='plain')




cpdef _frame_to_str(Frame frame):
    # Prints a frame object to a string
    # TODO
    return 'Frame object'



def _to_str(obj):
    '''
    Converts an object to a string.
    If the input object is a numeric symbol, matrix, expression, base, point or
    frame, returns the object as a string formatted nicely (when visualized on a
    terminal)
    '''
    if isinstance(obj, SymbolNumeric):
        return _symbol_to_str(obj)
    if isinstance(obj, Matrix):
        return _matrix_to_str(obj)
    if isinstance(obj, Expr):
        return _expr_to_str(obj)
    if isinstance(obj, Base):
        return _base_to_str(obj)
    if isinstance(obj, Point):
        return _point_to_str(obj)
    if isinstance(obj, Frame):
        return _frame_to_str(obj)
    return f'{obj.__class__.__name__} object'
