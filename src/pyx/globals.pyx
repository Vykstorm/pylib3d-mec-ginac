'''
Author: Víctor Ruiz Gómez
Description:
This file implements global function helpers
'''




######## Change gravity direction ########


def set_gravity_direction(state):
    '''set_gravity(state: int | str)
    Toggle gravity down or up.

    :param state:
        * If its True, 1 or "up", gravity is turned up.
        * If its False, 0 or "down", gravity is turned down.

    '''
    global c_gravity

    if not isinstance(state, (int, str)):
        raise TypeError('Input argument must be str or int')

    if isinstance(state, str):
        if state not in ('up', 'down'):
            raise TypeError('Possible values for gravity state are "up" and "down"')
        state = state == 'up'
    else:
        state = bool(state)

    c_gravity = state



def set_gravity_up():
    '''
    Toggle gravity up.
    '''
    set_gravity_direction(1)


def set_gravity_down():
    '''
    Toggle gravity down.
    '''
    set_gravity_direction(0)




def get_gravity_direction():
    '''get_gravity_direction() -> int
    Get the gravity direction. Returns 1 if it is turned up, and 0 if its down.

    :rtype: int

    '''
    return int(c_gravity)



# Default gravity direction is "down"
set_gravity_down()





######## Change atomization ########


def set_atomization_state(state):
    '''set_atomization_state(state: int | str)
    Toggle atomization on or off

    :param state:
        * If its True, 1 or "on", atomization is enabled
        * If its False, 0 or "off", atomization is disabled

    '''
    global c_atomization

    if not isinstance(state, (int, str)):
        raise TypeError('Input argument must be str or int')

    if isinstance(state, str):
        if state not in ('on', 'off'):
            raise TypeError('Possible values for atomization state are "on" and "off"')
        state = state == 'on'
    else:
        state = bool(state)

    c_atomization = state



def enable_atomization():
    '''
    Toggle atomization on
    '''
    set_atomization_state(1)


def disable_atomization():
    '''
    Toggle atomization off
    '''
    set_atomization_state(0)



def get_atomization_state():
    '''
    Returns 1 if atomization is enabled. 0 othwerwise.

    :rtype: int

    '''
    return int(c_atomization)


# Default atomizatio state is "enabled"
enable_atomization()




######## Unatomize ########


def unatomize(x):
    '''unatomize(x: Expr | Matrix | Wrench3D) -> Expr | Matrix | Wrench3D
    Unatomize the given expression, matrix or wrench
    '''

    if not isinstance(x, (Expr, Matrix, Wrench3D)):
        raise TypeError('Input argument must be an expression, matrix or wrench')

    if isinstance(x, Expr):
        # unatomize expression
        return _expr_from_c(c_unatomize((<Expr>x)._c_handler))

    if isinstance(x, Vector3D):
        # unatomize vector
        return _vector_from_c_value(c_unatomize(c_deref(<c_Vector3D*>(<Vector3D>x)._get_c_handler())))

    if isinstance(x, Tensor3D):
        # unatomize tensor
        return _tensor_from_c_value(c_unatomize(c_deref(<c_Tensor3D*>(<Tensor3D>x)._get_c_handler())))

    if isinstance(x, Wrench3D):
        # unatomize wrench
        return _wrench_from_c_value(c_unatomize(c_deref((<Wrench3D>x)._c_handler)))

    # unatomize matrix
    return _matrix_from_c_value(c_unatomize(c_deref((<Matrix>x)._get_c_handler())))




######## Recursive substitution ########


def subs(matrix, symbols, repl):
    '''subs(matrix: Matrix, symbols: Matrix | List[SymbolNumeric] | SymbolNumeric, repl: numeric) -> Matrix
    Performs a substitution of a vector of symbols or a symbol with a numeric value in all
    of the elements of the given matrix.

    * Replace a symbol with a numeric value:

        :Example:

        >>> a, b = new_param('a'), new_param('b')
        >>> m = Matrix([[a ** 2, a ** b], [b ** a, b ** 2]])
        >>> m
        ╭            ╮
        │ a**2  a**b │
        │ b**a  b**2 │
        ╰            ╯
        >>> subs(m, a, 0)
        ╭             ╮
        │ 0  (0.0)**b │
        │ 1      b**2 │
        ╰             ╯
        >>> subs(m, a, 1)
        ╭         ╮
        │ 1     1 │
        │ b  b**2 │
        ╰         ╯
        >>> subs(m, b, 1)
        ╭         ╮
        │ a**2  a │
        │    1  1 │
        ╰         ╯

    * Replace multiple symbols with a numeric value:

        :Example:

        >>> m = Matrix([[a ** 2, a - b], [b - a, b ** 2]])
        >>> m
        ╭            ╮
        │ a**2   a-b │
        │ -a+b  b**2 │
        ╰            ╯
        >>> subs(m, [a, b], 2)
        ╭      ╮
        │ 4  0 │
        │ 0  4 │
        ╰      ╯
        >>> q = Matrix([a, b])
        >>> subs(m, q, 1)
        ╭      ╮
        │ 1  0 │
        │ 0  1 │
        ╰      ╯


    :param symbols: Must be a matrix or a list of symbols to be replaced. It can also
        be a single symbol.
        If its a matrix, it must have a single row or column.
    :type symbols: Matrix, List[SymbolNumeric], SymbolNumeric

    :param repl: The numeric value which will be used to replace the symbols with

    :type repl: numeric

    :rtype: Matrix

    '''
    if not isinstance(matrix, Matrix):
        raise TypeError('First argument must be a matrix object')
    return matrix.subs(symbols, repl)




######## Matrix list optimization ########

cpdef matrix_list_optimize(matrix):
    '''matrix_list_optimize(matrix: Matrix) -> Matrix, List[Tuple[Expr, Expr]]
    '''
    if not isinstance(matrix, Matrix):
        raise TypeError('Input argument must be a Matrix object')

    cdef c_lst atom_lst
    cdef c_lst expr_lst

    c_matrix_list_optimize(c_deref(<c_Matrix*>(<Matrix>matrix)._get_c_handler()), atom_lst, expr_lst)

    atoms = [_expr_from_c(atom_lst.op(i)) for i in range(0, atom_lst.nops())]
    exprs = [_expr_from_c(expr_lst.op(i)) for i in range(0, expr_lst.nops())]
    return matrix, list(zip(atoms, exprs))
