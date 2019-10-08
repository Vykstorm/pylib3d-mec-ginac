'''
Author: Víctor Ruiz Gómez
Description:
This module defines internal helper functions to print symbols, expressions and matrices
in latex format.
'''


######## Custom GiNaC print formatting ########

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




######## Latex printing on IPython  ########


def _print_latex_ipython(text):
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
    display(Math(_parse_text(text).decode()))




######## Expressions, Symbols and Matrices to latex ########


def _symbol_to_latex(self, symbol):
    pass


def _expr_to_latex(self, expr):
    pass


def _matrix_to_latex(self, matrix):
    pass




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
