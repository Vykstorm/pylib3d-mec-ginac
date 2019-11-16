
'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class FrameDrawing
'''

######## Imports ########

from .geometry import _create_sphere_geometry, _create_arrow_geometry, _create_assembly_geometry
from .drawing import Drawing3D
from vtk import vtkAssembly, vtkSphereSource, vtkPolyDataMapper, vtkActor
from collections.abc import Iterable
from itertools import repeat



######## class FrameDrawing ########

class FrameDrawing(Drawing3D):

    ######## Constructor ########

    def __init__(self, viewer,
        axis_size=1, axis_shaft_radius=0.03, axis_tip_radius=0.1, axis_tip_size=0.25,
        axis_shaft_resolution=10, axis_tip_resolution=25, origin_radius=0.06, origin_resolution=15):

        # Validate input arguments
        if isinstance(axis_size, Iterable):
            axis_size = tuple(axis_size)
            if len(axis_size) != 3:
                raise ValueError
        else:
            axis_size = tuple(repeat(axis_size, 3))


        # Create geometry
        origin = _create_sphere_geometry(origin_radius, origin_resolution)
        x_axis_shaft, x_axis_tip = _create_arrow_geometry(size=axis_size[0])
        y_axis_shaft, y_axis_tip = _create_arrow_geometry(size=axis_size[1])
        z_axis_shaft, z_axis_tip = _create_arrow_geometry(size=axis_size[2])

        x_axis = _create_assembly_geometry(x_axis_shaft, x_axis_tip)
        y_axis = _create_assembly_geometry(y_axis_shaft, y_axis_tip)
        z_axis = _create_assembly_geometry(z_axis_shaft, z_axis_tip)

        # Setup geometry properties
        x_axis_tip.GetProperty().SetColor(1, 0, 0)
        y_axis_tip.GetProperty().SetColor(0, 1, 0)
        z_axis_tip.GetProperty().SetColor(0, 0, 1)

        # Adjust geometry local transformations
        y_axis.SetOrientation(0, 0, 90)
        z_axis.SetOrientation(0, -90, 0)

        # Ensamble geometry
        frame = _create_assembly_geometry(
            origin, x_axis, y_axis, z_axis
        )

        # Initialize super instance
        super().__init__(viewer, frame)
