'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class PointDrawing
'''

######## Imports ########

from .geometry import _create_sphere_geometry
from .drawing import Drawing3D
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor



######## class PointDrawing ########

class PointDrawing(Drawing3D):


    ######## Constructor ########

    def __init__(self, viewer,
        radius=0.1, resolution=15):
        # Validate input arguments

        sphere = _create_sphere_geometry(radius, resolution)
        sphere.GetProperty().SetColor(0, 1, 1)

        # Initialize super instance
        super().__init__(viewer, sphere)
