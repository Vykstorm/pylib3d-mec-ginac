'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from .object import Object
from threading import RLock
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor
from vtk import vtkActor, vtkMatrix4x4



class Geometry(Object):
    '''
    Instances of this class represents a 3D geometry mesh.
    '''
    def __init__(self, r=1):
        super().__init__()

        # Validate & parse input arguments
        source = vtkSphereSource()
        source.SetRadius(float(r))
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        actor = vtkActor()
        actor.SetMapper(mapper)

        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())
        # Set default properties for the actor
        actor.VisibilityOn()

        # Initialize internal fields
        self._actor = actor



    def get_actor(self):
        return self._actor
