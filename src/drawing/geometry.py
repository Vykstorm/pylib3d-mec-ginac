'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from .object import Object
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor, vtkMapper, vtkAlgorithm



class Geometry(Object):
    '''
    Instances of this class represents a 3D geometry mesh.
    '''
    def __init__(self, handler):
        assert isinstance(handler, (vtkAlgorithm, vtkMapper))

        super().__init__()

        # Validate & parse input arguments
        if isinstance(handler, vtkAlgorithm):
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(handler.GetOutputPort())
        else:
            mapper = handler
        self._mapper = mapper


    def get_mapper(self):
        return self._mapper




class Sphere(Geometry):
    def __init__(self, radius=1, resolution=15):
        source = vtkSphereSource()
        super().__init__(source)
        self._source = source
        self._set_radius(radius)
        self._set_resolution(resolution)


    def _set_radius(self, radius):
        pass


    def _set_resolution(self, resolution):
        pass


    def set_radius(self, radius):
        pass

    def set_resolution(self, resolution):
        pass
