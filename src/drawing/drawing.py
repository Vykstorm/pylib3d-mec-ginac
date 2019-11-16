'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


######## Imports ########

from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4
import numpy as np
from itertools import product
from functools import reduce
from operator import matmul



######## class Drawing3D ########

class Drawing3D:
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    ######## Constructor ########


    def __init__(self, viewer, vtk_handler):
        # Validate input arguments

        # Initialize internal fields
        self._vtk_handler = vtk_handler
        self._viewer, self._system = viewer, viewer._system
        self._transformation_funcs = []
        self._children, self._parent = [], None
        self._transformation = None

        # Initialize vtk actor user matrix
        self._vtk_handler.SetUserMatrix(vtkMatrix4x4())



    def _add(self, child):
        # Add a new drawing object as child of this one (parent transformations will be
        # applied to all children objects)
        self._children.insert(0, child)
        child._parent = self





    ######## Transformations ########


    def translate(self, position):
        '''
        Add a translation transformation to this drawing object (Transformations
        are applied from the first to the last one added)

        :param position: Must be a symbolic matrix with 3 elements representing
            the coordinates for the translation operation on each dimension

        '''
        if not isinstance(position, Matrix):
            position = Matrix(shape=(3, 1), values=position)
        elif position.get_size() != 3:
            raise TypeError('position must be a matrix with 3 elements')

        if position.get_num_rows() == 1:
            position = position.transpose()

        func = position.get_numeric_function()

        def _compute_translation_matrix():
            m = np.eye(4).astype(np.float64)
            m[0:3, 3] = self._system.evaluate(func).flatten()
            return m
        self._transformation_funcs.append(_compute_translation_matrix)



    def rotate(self, rotation):
        '''
        Add a rotation transformation to this drawing object (Transformations
        are applied from the first to the last one added)

        :param rotation: Must be a symbolic matrix of size 3x3 that will be the
            rotation transformation matrix.

        '''
        if not isinstance(rotation, Matrix):
            rotation = Matrix(shape=(3, 3), values=rotation)
        elif rotation.shape != (3, 3):
            raise TypeError('rotation must be a 3x3 matrix')

        func = rotation.get_numeric_function()

        def _compute_rotation_matrix():
            m = np.eye(4).astype(np.float64)
            m[0:3, 0:3] = self._system.evaluate(func)
            return m
        self._transformation_funcs.append(_compute_rotation_matrix)



    def rotate_to_dir(self, direction):
        '''
        Add a rotation transformation to this drawing object using a direction vector.
        (Transformations are applied from the first to the last one added)

        :param direction: Must be a symbolic matrix of size 1x3 or 3x1 that will be the
            direction vector.

        '''
        if not isinstance(direction, Matrix):
            direction = Matrix(shape=(3, 3), values=direction)
        elif direction.size != 3:
            raise TypeError('direction must be a 3x3 matrix')

        if direction.get_module() == 0:
            raise ValueError('direction must have non zero module')

        direction = direction.normalize()
        func = direction.get_numeric_function()

        def _compute_rotation_matrix():
            dx, dy, dz = tuple(self._system.evaluate(func).flatten())
            c1, s1 = np.sqrt(dx ** 2 + dy ** 2), dz
            c2, s2 = (1, 0) if c1 == 0 else (dx / c1, dy / c1)

            return np.array([
                [dx, -s2,  -s1*c2,  0],
                [dy,  c2,  -s1*s2,  0],
                [dz,   0,      c1,  0],
                [0,    0,        0, 1],
            ], dtype=np.float64)


        self._transformation_funcs.append(_compute_rotation_matrix)





    def scale(self, scale):
        '''
        Add a scale transformation to this drawing object (Transformation are
        applied from the first to the last one added)

        :param scale: Must be a symbolic matrix with three elements (each representing
            the scale on each axis)

        '''
        if not isinstance(scale, Matrix):
            scale = Matrix(shape=(3, 1), values=scale)
        elif scale.get_size() != 3:
            raise TypeError('scale must be a matrix with 3 elements')

        if scale.get_num_rows() == 1:
            scale = scale.transpose()

        func = scale.get_numeric_function()

        def _compute_scale_matrix():
            return np.diag(tuple(self._system.evaluate(func).flatten()) + (1,)).astype(np.float64)
        self._transformation_funcs.append(_compute_scale_matrix)




    ######## Updating ########


    def _update(self):
        # Update the transformation matrix for this drawing object
        self._update_transformation()

        # Update vtk user matrix with our transformation matrix
        self._update_vtk_user_matrix()

        # Update child drawings
        self._update_children()



    def _update_transformation(self):
        funcs = self._transformation_funcs
        local_transformations = map(lambda func: func(), funcs)
        transformation = reduce(matmul, local_transformations, np.eye(4).astype(np.float64))

        # Append parent transformation
        if self._parent is not None:
            transformation = self._parent._transformation @ transformation
        self._transformation = transformation



    def _update_children(self):
        # Update child drawings
        for child in self._children:
            child._update()



    def _update_vtk_user_matrix(self):
        # Update vtk user matrix with our transformation matrix previously computed
        matrix = self._vtk_handler.GetUserMatrix()
        for index, value in zip(product(range(0, 4), range(0, 4)), self._transformation.flatten()):
            i, j = index
            matrix.SetElement(i, j, value.item())
