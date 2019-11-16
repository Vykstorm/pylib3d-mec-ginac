'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class STLDrawing
'''



######## Imports ########

from .drawing import Drawing3D
from .geometry import _create_geometry_from_stl



######## class STLDrawing ########


class STLDrawing(Drawing3D):


    ######## Constructor ########


    def __init__(self, scene, filename):
        # Validate input arguments

        actor = _create_geometry_from_stl(filename)

        super().__init__(scene, actor)
