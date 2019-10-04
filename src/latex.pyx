'''
Author: Víctor Ruiz Gómez
Description: This module defines the helper function to_latex to convert matrices,
vectors, numeric symbols, ... to latex format
'''


from lib3d_mec_ginac_ext import SymbolNumeric, Vector3D, Matrix, Expr



def to_latex(*args, **kwargs):
    '''
    This function can be used to format one or multiple objects (matrices, symbols or expresions)
    to latex.

    :Example:

    s=System()
    a = s.new_param('a', r'\alpha')
    b = s.new_param('b', r'\beta')
    c = s.new_param('c', r'\gamma')
    v = s.new_vector('v', a, b, c)

    to_latex(a) # '\\alpha'
    to_latex(a, b) # '\\alpha\\beta'
    to_latex(a, r'\times', c) # '\\alpha\\times\\beta'
    to_latex(r'{} \bmod {}^2 + {}', a, b, c) # '\\alpha \bmod \\beta^2 + \\gamma'

    to_latex(v) # '\\begin{pmatrix}\n\\alpha\\\\\n\\beta\\\\\n\\gamma\n\\end{pmatrix}'
    to_latex(v.module) # '\\sqrt{\\beta^{2}+\\gamma^{2}+\\alpha^{2}}'
    '''

    def parse(x):
        if isinstance(x, SymbolNumeric):
            # Print a numeric symbol
            return x.tex_name or r'\textrm{' + x.name + '}'

        elif isinstance(x, Expr):
            return _ginac_print_ex((<Expr>x)._c_handler, latex=True)

        elif isinstance(x, Matrix):
            return _ginac_print_ex(c_ex((<Matrix>x)._get_c_handler().get_matrix()), latex=True)
        return x


    if args and isinstance(args[0], str):
        format, args = args[0], args[1:]
    else:
        if kwargs:
            raise TypeError('No keyword arguments allowed if format string is not specified')
        format = None


    args = tuple(map(parse, args))

    if format is None:
        return ''.join(map(str, args))

    kwargs = dict(zip(kwargs.keys(), map(parse, kwargs.values())))
    return str.format(format, *args, **kwargs)



def print_latex(*args, **kwargs):
    '''
    This function calls to_latex with the given arguments and displays the resulting
    latex code into IPython directly (it can be useful for jupyter notebooks)
    '''
    try:
        from IPython.display import display, Math
    except ImportError:
        raise ImportError('You must have installed IPython to use print_latex function')

    display(Math(to_latex(*args, **kwargs)))




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

    result = match('^([a-zA-Z])_?(\d*)$', name)
    if not result:
        return name.encode()
    letter, subindex = result.group(1), result.group(2)

    if letter in _latin_to_greek_latex:
        letter = _latin_to_greek_latex[letter]

    return (letter if not subindex else f'{letter}_' + '{' + subindex + '}').encode()
