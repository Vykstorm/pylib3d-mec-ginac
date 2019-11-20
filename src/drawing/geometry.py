'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from .object import VtkObjectWrapper
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor, vtkMapper, vtkAlgorithm



class Geometry(VtkObjectWrapper):
    '''
    Instances of this class represents a 3D geometry mesh.
    '''
    def __init__(self, handler):
        assert isinstance(handler, (vtkAlgorithm, vtkMapper))

        # Validate & parse input arguments
        if isinstance(handler, vtkAlgorithm):
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(handler.GetOutputPort())
        else:
            mapper = handler
        super().__init__(mapper)




class Sphere(Geometry):
    def __init__(self, radius=1, resolution=15):
        source = vtkSphereSource()
        super().__init__(source)
        self._source = source
        self.set_radius(radius)
        self.set_resolution(resolution)

    def get_radius(self):
        with self:
            return self._source.GetRadius()


    def get_resolution(self):
        with self:
            return self._source.GetPhiResolution()


    def set_radius(self, radius):
        try:
            radius = float(radius)
            if radius < 0:
                raise TypeError
        except TypeError:
            raise TypeError('radius must be a positive number')
        with self:
            self._source.SetRadius(radius)
            self.fire_event('radius_changed')


    def set_resolution(self, resolution):
        if not isinstance(resolution, int) or resolution <= 0:
            raise TypeError('resolution must be an integer greater than zero')
        with self:
            self._source.SetPhiResolution(resolution)
            self._source.SetThetaResolution(resolution)
            self.fire_event('resolution_changed')


    @property
    def radius(self):
        return self.get_radius()

    @radius.setter
    def radius(self, value):
        self.set_radius(value)


    @property
    def resolution(self):
        return self.get_resolution()

    @resolution.setter
    def resolution(self, value):
        self.set_resolution(value)
