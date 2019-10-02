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
    '''

    def parse(x):
        if isinstance(x, SymbolNumeric):
            # Print a numeric symbol
            return x.tex_name or r'\textrm{' + x.name + '}'

        elif isinstance(x, Expr):
            return _ginac_print_ex((<Expr>x)._c_handler, latex=True)

        elif isinstance(x, Matrix):
            n, m = x.shape
            rows = [' & '.join([to_latex(x.get(i, j)) for j in range(0, m)]) for i in range(0, n)]
            return r'\begin{pmatrix}' + '\n' + (r'\\' + '\n').join(rows) + '\n' + r'\end{pmatrix}'
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
