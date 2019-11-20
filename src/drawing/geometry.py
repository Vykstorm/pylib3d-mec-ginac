'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from .object import Object
from threading import RLock
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor, vtkMapper



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
        self._mapper = mapper


    def get_mapper(self):
        return self._mapper
