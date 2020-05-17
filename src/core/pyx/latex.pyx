'''
Author: Víctor Ruiz Gómez
Description:
This file defines helper classes & functions to print matrices, expressions, symbols, ...
in latex format
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




######## Class LatexObjectPrinter ########


cdef class LatexPrinter(Printer):
    '''
    This is an specialization of the class Printer to print objects of this library
    in latex format.
    '''

    cdef _print_c_expr(self, c_ex expr):
        cdef c_ginac_printer* c_printer = new c_ginac_latex_printer(c_sstream())
        expr.print(c_deref(c_printer))
        text = (<bytes>(<c_sstream*>&c_printer.s).str()).decode()
        del c_printer
        return text


    cpdef print_expr(self, Expr expr):
        # This method is used to print a expression
        return self._print_c_expr(expr._c_handler)



    cpdef print_symbol(self, SymbolNumeric symbol):
        # This method is used to print a numeric symbol
        return symbol.get_tex_name() or r'\textrm{' + symbol.get_name()  + '}'



    cpdef print_matrix(self, Matrix matrix):
        # This method is used to print a matrix (including vectors and tensors)
        #s = repr(self._print_c_expr(c_ex(matrix._get_c_handler().get_matrix())))
        values = tuple(map(to_latex, matrix))
        n, m = matrix.get_shape()
        lines = [' & '.join([to_latex(matrix.get(i, j)) for j in range(0, m)]) for i in range(0, n)]
        return r'\begin{bmatrix}' + '\n' + (r'\\' + '\n').join(lines) + '\n' + r'\end{bmatrix}'





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




######## Utility global functions ########


def to_latex(*args):
    '''
    Convert one or more objects in a single latex inline formula.
    Objects can be of any kind; numeric symbols, expressions, matrices, vectors and tensors are
    printed nicely. The rest of objects are converted to a string using the metamethod
    __str__ and wrapped in a latex textrm statement: '\\textrm{str(object))}'


        :Example:

        >>> to_latex(new_param('a', tex_name='\\alpha'))
        '\\alpha'

        >>> u, x = new_param('u', tex_name='\\upsilon'), new_param('x', tex_name=r'\chi')
        >>> to_latex(u, x)
        '\\upsilon\:\\chi'

        >>> to_latex(u, '\\times', x, '=', u * x)
        '\\upsilon\\:\\times\\:\\chi\\:=\\: \\upsilon \\chi'

        >>> to_latex(new_matrix(shape=[3, 3]))
        '\\left(\\begin{array}{ccc}0&0&0\\\\0&0&0\\\\0&0&0\\end{array}\\right)'
        
    '''
    printer = LatexPrinter()
    def _to_latex(x):
        try:
            return printer.print(x)
        except NotImplementedError:
            return '\\textrm{' + str(x) + '}'

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
