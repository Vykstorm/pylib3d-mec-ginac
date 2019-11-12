'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class PointDrawing
'''

######## Imports ########

from .drawing import Drawing3D
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor



######## class PointDrawing ########

class PointDrawing(Drawing3D):


    ######## Constructor ########

    def __init__(self, scene, position=None, rotation=None, scale=None, radius=0.1, center=(0, 0, 0), resolution=15):
        # Validate input arguments


        # Create geometry
        source = vtkSphereSource()
        source.SetRadius(radius)
        source.SetCenter(*center)
        source.SetThetaResolution(resolution)
        source.SetPhiResolution(resolution)

        # Create underline vtk actor
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)

        # Initialize super instance
        super().__init__(scene, actor, position, rotation, scale)
