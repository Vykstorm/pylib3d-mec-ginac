'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class VectorDrawing
'''

######## Imports ########

from .drawing import Drawing3D
from .geometry import _create_arrow_geometry



######## class VectorDrawing ########

class VectorDrawing(Drawing3D):


    ######## Constructor ########



    def __init__(self, scene, *args, **kwargs):
        # Validate input arguments

        arrow, shaft, tip = _create_arrow_geometry(size=1)
        tip.GetProperty().SetColor(1, 1, 0)

        super().__init__(scene, arrow, *args, **kwargs)


    #def _update_transformation(self):
    #    pass
