'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class VectorDrawing
'''

######## Imports ########

from .drawing import Drawing3D
from .geometry import _create_cylinder_geometry, _create_cone_geometry
from vtk import vtkActor


######## class VectorDrawing ########

class VectorDrawing(Drawing3D):


    ######## Constructor ########


    def __init__(self, viewer, size=1):
        # Validate input arguments


        # Create vector geometry (origin + shaft + tip)
        shaft_geom = _create_cylinder_geometry(height=1, radius=0.03)
        tip_geom = _create_cone_geometry(height=0.2, radius=0.1, direction=(1, 0, 0))

        # Adjust geometry local transformations
        shaft_geom.SetOrientation(0, 0, 90)
        shaft_geom.SetPosition(0.5, 0, 0)
        tip_geom.SetPosition(0.2, 0, 0)

        # Setup geometry properties
        tip_geom.GetProperty().SetColor(1, 1, 0)

        # Create subdrawings
        tip = Drawing3D(viewer, tip_geom)
        shaft = Drawing3D(viewer, shaft_geom)

        # Initialize super instance
        super().__init__(viewer, vtkActor())

        # Add subdrawings to this drawing
        self._add(shaft)
        self._add(tip)

        # Scale the shaft and translate the tip
        shaft.scale([size, 1, 1])
        tip.translate([size - 0.2, 0, 0])
