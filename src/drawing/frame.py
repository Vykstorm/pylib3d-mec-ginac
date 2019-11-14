
'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class FrameDrawing
'''

######## Imports ########

from .geometry import _create_sphere_geometry, _create_arrow_geometry, _create_assembly_geometry
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
        origin = _create_sphere_geometry(origin_radius, origin_resolution)
        x_axis, x_axis_shaft, x_axis_tip = _create_arrow_geometry()
        y_axis, y_axis_shaft, y_axis_tip = _create_arrow_geometry()
        z_axis, z_axis_shaft, z_axis_tip = _create_arrow_geometry()

        x_axis_tip.GetProperty().SetColor(1, 0, 0)
        y_axis_tip.GetProperty().SetColor(0, 1, 0)
        z_axis_tip.GetProperty().SetColor(0, 0, 1)

        y_axis.SetOrientation(0, 0, 90)
        z_axis.SetOrientation(0, -90, 0)

        actor = _create_assembly_geometry(origin, x_axis, y_axis, z_axis)


        # Initialize super instance
        super().__init__(scene, actor, position, rotation, scale)
