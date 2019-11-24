'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Transform
'''


######## Import statements ########

from lib3d_mec_ginac_ext import Matrix, SymbolNumeric, Expr, cos, sin
import numpy as np
from collections.abc import Iterable
from itertools import repeat, chain
from functools import reduce
from operator import matmul, mul, methodcaller, attrgetter



######## class Transform ########

class Transform:
    '''
    Instances of this class represents a geometry transformation (scale, rotation,
    translation).
    Internally they are represented as 4x4 matrices (either symbolic or numerical)
    '''
    def __init__(self, matrix):
        if not isinstance(matrix, (Matrix, np.ndarray)):
            raise TypeError('Input argument must be a Matrix or a numpy array')

        if matrix.shape != (4, 4):
            raise ValueError('matrix shape must be 4x4')

        if isinstance(matrix, np.ndarray):
            matrix = np.array(matrix, copy=False, dtype=np.float64, order='C')
            self._evaluate = lambda system: matrix
        else:
            numeric_func = matrix.get_numeric_function()
            self._evaluate = lambda system: system.evaluate(numeric_func)
        self._matrix = matrix



    def evaluate(self, system):
        '''evaluate(system: System) -> ndarray
        Evaluate this transformation numerically. Return a numpy array of size 4x4
        '''
        return self._evaluate(system)


    @property
    def _symbolic(self):
        if isinstance(self._matrix, Matrix):
            return self._matrix
        return Matrix(self._matrix)



    def concatenate(self, other):
        '''concatenate(other: Transform) -> ComposedTransform
        Concatenate this transformation with another.

        :rtype: ComposedTransform

        '''
        return ComposedTransform(self, other)



    @classmethod
    def identity(cls):
        '''identity() -> Transform
        Get the identity transformation
        '''
        return cls(np.eye(4))


    @classmethod
    def translation(cls, *args):
        '''translation(...) -> Transform
        Create a translation transformation with the given coordinates. Coordinates
        can be symbols, expressions or numbers.

            :Example:

            >>> Transform.translation([a, b, c ** 2])
            ╭               ╮
            │ 1  0  0     a │
            │ 0  1  0     b │
            │ 0  0  1  c**2 │
            │ 0  0  0     1 │
            ╰               ╯

            :Example:

            >>> Transform.translation(1, 2, 3)
            ╭            ╮
            │ 1  0  0  1 │
            │ 0  1  0  2 │
            │ 0  0  1  3 │
            │ 0  0  0  1 │
            ╰            ╯


        Coordinates can be given as three separate position arguments

            :Example:

            >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
            >>> Transform.translation(a, b, c)
            ╭            ╮
            │ 1  0  0  a │
            │ 0  1  0  b │
            │ 0  0  1  c │
            │ 0  0  0  1 │
            ╰            ╯

        :rtype: Transformation


        '''
        if len(args) not in (1, 3):
            raise TypeError('Expected one or three positional arguments')
        if len(args) == 3:
            m = tuple(args)
        else:
            m = args[0]
            if not isinstance(m, Iterable):
                raise TypeError('Input argument must be iterable')
            m = tuple(m)
            if len(m) != 3:
                raise TypeError('Input argument must be a list of three values')

        if not all(map(lambda x: isinstance(x, (SymbolNumeric, Expr, float, int)), m)):
            raise TypeError('All input values must be numbers, expressions or symbols')


        tx, ty, tz = m
        if any(map(lambda x: isinstance(x, (SymbolNumeric, Expr)), m)):
            m = Matrix([
                [1, 0, 0, tx],
                [0, 1, 0, ty],
                [0, 0, 1, tz],
                [0, 0, 0,  1]
            ])
        else:
            m = np.eye(4).astype(np.float64)
            m[0, 3], m[1, 3], m[2, 3] = tx, ty, tz

        return cls(m)




    @classmethod
    def rotation(cls, matrix):
        '''rotation(matrix: Matrix | ndarray) -> Transform

        Create a rotation transformation with the given 3x3 rotation matrix
        (it can be a symbolic matrix or a numpy array)

            :Example:

            >>> a = new_base('a', 'xyz')
            >>> rotation_matrix(a, 'xyz')
            ╭         ╮
            │ 1  0  0 │
            │ 0  1  0 │
            │ 0  0  1 │
            ╰         ╯
            >>> Transform.rotation(rotation_matrix(a, 'xyz'))
            ╭            ╮
            │ 1  0  0  0 │
            │ 0  1  0  0 │
            │ 0  0  1  0 │
            │ 0  0  0  1 │
            ╰            ╯

        :rtype: Transformation

        '''
        if not isinstance(matrix, (Matrix, np.ndarray)):
            raise TypeError('Input argument must be a Matrix or a numpy array')

        try:
            if isinstance(matrix, Matrix):
                if matrix.get_shape() != (3, 3):
                    raise TypeError
            else:
                if matrix.shape != (3, 3):
                    raise TypeError
        except TypeError:
            raise TypeError('Input argument must be an array of size 3x3')


        if isinstance(matrix, Matrix):
            m = Matrix.block(1, 2, matrix, Matrix(shape=[3, 1]))
            m = Matrix.block(2, 1, m, Matrix(shape=[1, 4]))
            m[3, 3] = 1
        else:
            m = np.eye(4).astype(np.float64)
            m[0:3, 0:3] = matrix

        return cls(m)




    @classmethod
    def rotation_over_axis(cls, phi, axis):
        if not isinstance(phi, (SymbolNumeric, Expr)):
            try:
                phi = float(phi)
            except TypeError:
                raise TypeError('phi must be symbol, expression or number')
        else:
            phi = Expr(phi)

        try:
            axis = tuple(axis)
            if len(axis) != 3:
                raise TypeError
        except TypeError:
            raise TypeError('axis must be a list of three values')

        if not any(map(lambda value: isinstance(value, (SymbolNumeric, Expr)), axis)):
            try:
                axis = tuple(map(float, axis))
            except TypeError:
                raise TypeError('axis must be a list of three values (symbols, expresssions or numbers)')
        else:
            axis = tuple(map(Expr, axis))


        if isinstance(phi, Expr) or any(map(lambda value: isinstance(value, Expr), axis)):
            axis, phi = Matrix(shape=(1, 3), values=axis), Expr(phi)
            axis_skew = axis.get_skew()
            return cls.rotation(Matrix.eye(3) + sin(phi) * axis_skew + (1 - cos(phi)) * (axis_skew * axis_skew))

        a, b, c = axis
        sp, cp = sin(phi), cos(phi)
        return cls.rotation(np.array([
            [1+(-1+cp)*(b**2+c**2),  -sp*c-(-1+cp)*a*b,      -(-1+cp)*a*c+sp*b],
            [sp*c-(-1+cp)*a*b,       1+(-1+cp)*(c**2+a**2),  -sp*a-(-1+cp)*b*c],
            [-(-1+cp)*a*c-sp*b,      sp*a-(-1+cp)*b*c,       1+(-1+cp)*(b**2+a**2)]
        ] ,dtype=np.float64))



    @classmethod
    def xrotation(cls, phi):
        return cls.rotation_over_axis(phi, (1, 0, 0))

    @classmethod
    def yrotation(cls, phi):
        return cls.rotation_over_axis(phi, (0, 1, 0))

    @classmethod
    def zrotation(cls, phi):
        return cls.rotation_over_axis(phi, (0, 0, 1))





    @classmethod
    def scale(cls, *args):
        '''scale(...) -> Transformation

        Create a scale transformation with the given scale factors. Factor values
        can be numbers, expressions or symbols

            :Example:

            >>> Transform.scale([a, b, c ** 2])
            ╭               ╮
            │ a  0     0  0 │
            │ 0  b     0  0 │
            │ 0  0  c**2  0 │
            │ 0  0     0  1 │
            ╰               ╯

            :Example:

            >>> Transform.scale([1, 2, 3])
            ╭            ╮
            │ 1  0  0  0 │
            │ 0  2  0  0 │
            │ 0  0  3  0 │
            │ 0  0  0  1 │
            ╰            ╯

        Factors can be specified as three separate positional arguments

            :Example:

            >>> Transform.scale(a, b, c)
            ╭            ╮
            │ a  0  0  0 │
            │ 0  b  0  0 │
            │ 0  0  c  0 │
            │ 0  0  0  1 │
            ╰            ╯

        :rtype: Transformation

        '''
        if len(args) not in (1, 3):
            raise TypeError('Expected one or three positional arguments')
        if len(args) == 3:
            m = tuple(args)
        else:
            m = args[0]
            if isinstance(m, Iterable):
                m = tuple(m)
                if len(m) != 3:
                    raise TypeError('Input argument must be a list of three values')
            else:
                m = tuple(repeat(m, 3))

        if not all(map(lambda x: isinstance(x, (SymbolNumeric, Expr, float, int)), m)):
            raise TypeError('All input values must be numbers, expressions or symbols')

        sx, sy, sz = m
        if any(map(lambda x: isinstance(x, (SymbolNumeric, Expr)), m)):
            m = Matrix([
                [sx, 0, 0, 0],
                [0, sy, 0, 0],
                [0, 0, sz, 0],
                [0, 0, 0,  1]
            ])
        else:
            m = np.eye(4).astype(np.float64)
            m[0, 0], m[1, 1], m[2, 2] = sx, sy, sz

        return cls(m)


    @staticmethod
    def rotation_from_dir(*args):
        '''rotation_from_dir(...) -> Transformation
        Create a rotation transformation from a direction vector. Vector components
        can be numbers, symbols.

            :Example:

            >>> R = Transform.rotation_from_dir([1, a, b])
            >>> R
            Rotation transformation from direction: 1, a, b
            >>> system = get_default_system()
            >>> R.evaluate(system)
            array([[ 1., -0., -0.,  0.],
                   [ 0.,  1., -0.,  0.],
                   [ 0.,  0.,  1.,  0.],
                   [ 0.,  0.,  0.,  1.]])
            >>> set_value('a', 0.5)
            >>> set_value('b', 0.5)
            >>> R.evaluate(system)
            array([[ 0.81649658, -0.4472136 , -0.36514837,  0.        ],
                   [ 0.40824829,  0.89442719, -0.18257419,  0.        ],
                   [ 0.40824829,  0.        ,  0.91287093,  0.        ],
                   [ 0.        ,  0.        ,  0.        ,  1.        ]])


        Direction components can also be specified as three different positional arguments:

            :Example:

            >>> R = Transform.rotation_from_dir(1, 0.5, 0.5)
            >>> R
            Rotation transformation from direction: 1, 0.5, 0.5
            >>> system = get_default_system()
            >>> R.evaluate(system)
            array([[ 0.81649658, -0.4472136 , -0.36514837,  0.        ],
                   [ 0.40824829,  0.89442719, -0.18257419,  0.        ],
                   [ 0.40824829,  0.        ,  0.91287093,  0.        ],
                   [ 0.        ,  0.        ,  0.        ,  1.        ]])


        :rtype: Transformation

        '''

        if len(args) not in (1, 3):
            raise TypeError('Expected one or three positional arguments')
        if len(args) == 3:
            m = tuple(args)
        else:
            m = args[0]
            if not isinstance(m, Iterable):
                raise TypeError('Input argument must be iterable')
            m = tuple(m)
            if len(m) != 3:
                raise TypeError('Input argument must be a list of three values')

        if not all(map(lambda x: isinstance(x, (SymbolNumeric, Expr, float, int)), m)):
            raise TypeError('All input values must be numbers, expressions or symbols')

        # This can be optimized!
        direction = Matrix(m)
        func = direction.get_numeric_function()


        class RotationFromDirTransform(Transform):
            def __init__(self):
                pass

            def evaluate(self, system):
                dx, dy, dz = system.evaluate(func).flat
                m = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
                if m == 0:
                    # If the direction module has zero module, just return the identity matrix
                    return np.eye(4).astype(np.float64)

                dx, dy, dz = dx / m, dy / m, dz / m

                c1, s1 = np.sqrt(dx ** 2 + dy ** 2), dz
                c2, s2 = (1, 0) if c1 == 0 else (dx / c1, dy / c1)
                return np.array([
                    [dx, -s2,  -s1*c2,  0],
                    [dy,  c2,  -s1*s2,  0],
                    [dz,   0,      c1,  0],
                    [0,    0,        0, 1],
                ], dtype=np.float64)

            def __str__(self):
                return f'Rotation transformation from direction: {", ".join(map(str, direction))}'


        return RotationFromDirTransform()



    def __and__(self, other):
        # Implements the and logical operator to concatenate transformations
        return self.concatenate(other)


    def __str__(self):
        return str(self._symbolic)


    def __repr__(self):
        return self.__str__()






######## class ComposedTransform ########

class ComposedTransform(Transform):
    '''
    Instances of this class represents a concatenation of different transformations.
    Use the operator '&' to concatenate transformations.

        :Example:


        >>> a, b, c = new_param('a'), new_param('b'), new_param('c')
        >>> T = Transform.translation(a, b, c)
        >>> T
        ╭            ╮
        │ 1  0  0  a │
        │ 0  1  0  b │
        │ 0  0  1  c │
        │ 0  0  0  1 │
        ╰            ╯
        >>> S = Transform.scale(1, 2, 3)
        >>> S
        ╭            ╮
        │ 1  0  0  0 │
        │ 0  2  0  0 │
        │ 0  0  3  0 │
        │ 0  0  0  1 │
        ╰            ╯
        >>> Q = T & S
        >>> Q
        ╭            ╮
        │ 1  0  0  a │
        │ 0  2  0  b │
        │ 0  0  3  c │
        │ 0  0  0  1 │
        ╰            ╯
        >>> set_value('a', 2)
        >>> set_value('b', 4)
        >>> set_value('c', 6)
        >>> Q.evaluate(get_default_system())
        array([[1., 0., 0., 2.],
               [0., 2., 0., 4.],
               [0., 0., 3., 6.],
               [0., 0., 0., 1.]])

    '''
    def __init__(self, *args):
        if not args:
            raise TypeError('At least one input must be specified')
        for arg in args:
            if not isinstance(arg, Transform):
                raise TypeError('Input arguments must be Transform objects')
        self._items = args


    def evaluate(self, system):
        return reduce(matmul, map(methodcaller('evaluate', system), self._items))


    @property
    def _symbolic(self):
        return reduce(mul, map(attrgetter('_symbolic'), self._items))


    def concatenate(self, other):
        return ComposedTransform(*chain(self._items, [other]))
