'''
Author: Víctor Ruiz Gómez
Description: Public API for the submodule drawing
'''


# The next variable will contain all public API methods & classes
__all__ = [
    # Main classes
    'Scene', 'Viewer', 'Drawing3D', 'Geometry',
    # Drawing3D subclasses
    'PointDrawing', 'VectorDrawing', 'FrameDrawing',
    # Geometry subclasses
    'Sphere', 'Cube', 'Cone', 'Cylinder', 'Line', 'LineStrip',
    # stl & scad utilities
    'read_stl', 'write_stl', 'scad2stl', 'scad_to_stl',
    # Other utility classes
    'Timer', 'OneShotTimer', 'Color', 'Transform'
]

# Import all the class & functions of the public API
from .scene import Scene
from .viewer import VtkViewer as Viewer
from .drawing import Drawing3D, PointDrawing, VectorDrawing, FrameDrawing
from .geometry import Geometry
from .geometry import Sphere, Cube, Cone, Cylinder, Line, LineStrip
from .geometry import read_stl, write_stl
from .scad import scad2stl, scad_to_stl
from .timer import Timer, OneShotTimer
from .color import Color
from .transform import Transform





# Additional classes & functions of this submodule

_viewer = Viewer()

def get_viewer():
    '''get_viewer() -> Viewer
    Get the viewer where the 3d scene will be shown

    :rtype: Viewer

    '''
    return _viewer

__all__.append('get_viewer')
