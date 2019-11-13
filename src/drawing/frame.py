
'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class FrameDrawing
'''

######## Imports ########

from .drawing import Drawing3D
from vtk import vtkAssembly, vtkSphereSource, vtkPolyDataMapper, vtkActor



######## class FrameDrawing ########

class FrameDrawing(Drawing3D):

    ######## Constructor ########

    def __init__(self, scene, position=None, rotation=None, scale=None,
        axis_size=1, axis_shaft_radius=0.03, axis_tip_radius=0.1, axis_tip_size=0.25,
        axis_shaft_resolution=10, axis_tip_resolution=25, origin_radius=0.06, origin_resolution=15):

        # Validate input arguments


        # Create geometry
        origin_geom = vtkSphereSource()
        origin_geom.SetRadius(origin_radius)
        origin_geom.SetThetaResolution(origin_resolution)
        origin_geom.SetPhiResolution(origin_resolution)

        # Create underline vtk actor

        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(origin_geom.GetOutputPort())
        origin = vtkActor()
        origin.SetMapper(mapper)



        actor = vtkAssembly()
        actor.AddPart(origin)

        # Initialize super instance
        super().__init__(scene, actor, position, rotation, scale)
