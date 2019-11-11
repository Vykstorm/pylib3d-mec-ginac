'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


######## Imports ########

from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp
import numpy as np



######## class Drawing3D ########

class Drawing3D:
    '''
    An instance of this class represents any 3D renderable entity with the next
    properties:
    * Has position, rotation, scale and color properties
    * Has a geometry attached (subclases may define it)
    * position and rotation are represented internally as a 3x1 and 3x3 symbolic
        matrices. They are evaluated numerically when the transformation matrix of the drawing
        must be computed.
    * scale property is represented as a vector of 3 numeric elements (the scale on each dimension for
    the drawing)
    '''

    ######## Constructor ########


    def __init__(self, vtk_handler, position=None, rotation=None, scale=None):
        # Validate input arguments
        if not isinstance(vtk_handler, vtkProp):
            raise TypeError('vtk_handler must be a vtkProp instance')

        if position is not None and not isinstance(position, Matrix):
            raise TypeError('position must be a Matrix instance')

        if position.get_size() != 3:
            raise ValueError('position must be a 3x1 or 1x1 Matrix')
        if position.get_num_rows() == 1:
            position = position.transpose()

        if rotation is not None and not isinstance(rotation, Matrix):
            raise TypeError('rotation must be a 3x3 Matrix')


        self._vtk_handler = vtk_handler
        self._position = position
        self._rotation = rotation
        self._position_func = position.get_numeric_function()
        self._rotation_func = rotation.get_numeric_function()
        self._scale = (1, 1, 1)



    ######## Updating ########


    def _update(self):
        '''
        This method updates the transformation matrix of the underline vtk actor.
        '''
        pass





    ######## Getters ########


    def get_position(self):
        '''get_position() -> Matrix
        Get the position of this drawing (a symbolic matrix with size 3x1)

        :rtype: Matrix

        '''
        return self._position


    def get_rotation(self):
        '''get_rotation() -> Matrix
        Get the rotation of this drawing (a symbolic matrix with size 3x3)

        :rtype: Matrix

        '''
        return self._rotation


    def get_transformation(self, system):
        '''get_transformation(system: System) -> ndarray
        Compute the transformation matrix for this drawing numerically.

        :type system: System

        :return: A numpy array of size 4x4
        :rtype: ndarray

        '''
        translation = np.eye(4).astype(np.float64)
        translation[0:3, 3] = system.evaluate(self._position_func).flatten()

        rotation = np.eye(4).astype(np.float64)
        rotation[0:3, 0:3] = system.evaluate(self._rotation_func)

        scale = np.diag(self._scale + (1,)).astype(np.float64)

        return scale @ rotation @ translation





    ######## Properties ########

    @property
    def position(self):
        '''
        Only read property that returns the position of this drawing (a symbolic matrix with size 3x1)

        :rtype: Matrix

        .. seealso:: :func:`get_position`

        '''
        return self.get_position()


    @property
    def rotation(self):
        '''
        Only read property that returns the rotation of this drawing (a symbolic matrix with size 3x3)

        :rtype: Matrix

        .. seealso:: :func:`get_rotation`

        '''
        return self.get_rotation()
