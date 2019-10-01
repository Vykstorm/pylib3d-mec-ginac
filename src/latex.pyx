'''
Author: Víctor Ruiz Gómez
Description: This module defines the helper function to_latex to convert matrices,
vectors, numeric symbols, ... to latex format
'''


from lib3d_mec_ginac_ext import SymbolNumeric, Vector3D, Matrix, Expr


def to_latex(x):
    '''to_latex(x: Union[SymbolNumeric, Matrix, Expr]) -> str
    Converts the input argument to latex
    :param x: The parameter to convert to latex
    :type x: SymbolNumeric, Vector, Matrix, Expr
    :raises TypeError: If the input argument has an invalid type
    '''
    if isinstance(x, SymbolNumeric):
        # Print a numeric symbol
        tex = x.tex_name or r'\textrm{' + x.name + '}'

    elif isinstance(x, Expr):
        tex = _ginac_print_ex((<Expr>x)._c_handler, latex=True)

    elif isinstance(x, Matrix):
        n, m = x.shape
        rows = [' & '.join([to_latex(x.get(i, j)) for j in range(0, m)]) for i in range(0, n)]
        return r'\begin{pmatrix}' + '\n' + (r'\\' + '\n').join(rows) + '\n' + r'\end{pmatrix}'
    else:
        raise TypeError('Input argument must be a numeric symbol, vector, matrix or expression')

    return tex



def print_latex(x):
    '''
    This method prints the given object in latex form on IPython directly
    (it can be useful for jupyter notebooks)
    '''
    try:
        from IPython.display import display, Math
    except ImportError:
        raise ImportError('You must have installed IPython to use print_latex function')

    display(Math(to_latex(x)))
