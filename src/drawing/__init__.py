'''
Author: Víctor Ruiz Gómez
Description: Public API for the submodule drawing
'''


# The next variable will contain all public API methods & classes
__all__ = [
    # Main classes
    'Scene', 'Viewer', 'Drawing', 'Drawing2D', 'TextDrawing', 'Drawing3D', 'Geometry',
    # Drawing3D subclasses
    'PointDrawing', 'VectorDrawing', 'FrameDrawing',
    # Geometry subclasses
    'Sphere', 'Cube', 'Cone', 'Cylinder', 'Line', 'LineStrip',
    # stl & scad utilities
    'read_stl', 'write_stl', 'scad2stl', 'scad_to_stl',
    # Other utility classes
    'Transform',
    # viewer functions
    'get_viewer', 'show_viewer', 'close_viewer', 'get_selected_drawing',
    'set_drawing_refresh_rate'
]

# Import all the class & functions of the public API
from .scene import Scene
from .viewer import (VtkViewer as Viewer, get_viewer,
    show_viewer, close_viewer, get_selected_drawing, set_drawing_refresh_rate)
from .drawing import Drawing
from .drawing2D import Drawing2D, TextDrawing
from .drawing3D import Drawing3D, PointDrawing, VectorDrawing, FrameDrawing
from .geometry import Geometry
from .geometry import Sphere, Cube, Cone, Cylinder, Line, LineStrip
from .geometry import read_stl, write_stl
from .scad import scad2stl, scad_to_stl
from .timer import Timer, OneShotTimer
from .transform import Transform
