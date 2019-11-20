'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from .object import VtkObjectWrapper
from vtk import vtkPolyDataMapper, vtkActor, vtkMapper, vtkAlgorithm
from vtk import vtkSphereSource, vtkCubeSource, vtkConeSource, vtkCylinderSource
from vtk import vtkLineSource
from itertools import repeat
from collections.abc import Iterable
from operator import gt
from functools import partial


def _parse_size(value, argname):
    try:
        value = float(value)
        if value < 0:
            raise TypeError
        return value
    except TypeError:
        raise TypeError(f'{argname} must be a positive number')


def _parse_resolution(resolution):
    if not isinstance(resolution, int) or resolution <= 0:
        raise TypeError('resolution must be an integer greater than zero')
    return resolution


def _parse_vector3(x, argname):
    try:
        if len(x) not in (1, 3):
            raise TypeError
        if len(x) == 1:
            x = tuple(x[0])
            if len(x) != 3:
                raise TypeError
    except TypeError:
        raise TypeError(f'Invalid number of components specified for {argname}')

    try:
        x = tuple(map(float, x))
        return x
    except TypeError:
        raise TypeError(f'{argname} must be a list of numbers')




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
    '''
    This represents a sphere geometry
    '''
    def __init__(self, radius=1, center=(0, 0, 0), resolution=15):
        source = vtkSphereSource()
        super().__init__(source)
        self._source = source
        self.set_radius(radius)
        self.set_resolution(resolution)
        self.set_center(center)


    def get_radius(self):
        with self:
            return self._source.GetRadius()


    def get_resolution(self):
        with self:
            return self._source.GetPhiResolution()


    def set_radius(self, radius):
        radius = _parse_size(radius, 'radius')
        with self:
            self._source.SetRadius(radius)
            self.fire_event('radius_changed')


    def set_resolution(self, resolution):
        resolution = _parse_resolution(resolution)
        with self:
            self._source.SetPhiResolution(resolution)
            self._source.SetThetaResolution(resolution)
            self.fire_event('resolution_changed')


    def get_center(self):
        with self:
            return self._source.GetCenter()


    def set_center(self, *args):
        center = _parse_vector3(args, 'center')
        with self:
            self._source.SetCenter(*center)
            self.fire_event('center_changed')


    radius = property(fget=get_radius, fset=set_radius)
    resolution = property(fget=get_resolution, fset=set_resolution)
    center = property(fget=get_center, fset=set_center)





class Cube(Geometry):
    '''
    This represents a cube geometry
    '''
    def __init__(self, size=1, center=(0, 0, 0)):
        source = vtkCubeSource()
        super().__init__(source)
        self._source = source
        self.set_size(size)
        self.set_center(center)


    def get_size(self):
        source = self._source
        with self:
            return source.GetXLength(), source.GetYLength(), source.GetZLength()


    def set_size(self, *args):
        try:
            if len(args) not in (1, 3):
                raise TypeError
            if len(args) == 1:
                arg = args[0]
                if isinstance(arg, Iterable):
                    size = tuple(arg)
                    if len(size) != 3:
                        raise TypeError
                else:
                    size = repeat(arg, 3)
            else:
                size = args
        except TypeError:
            raise TypeError('Invalid number of arguments specified')

        try:
            size = tuple(map(float, size))
        except TypeError:
            raise TypeError('All size values must be numbers')

        if any(map(partial(gt, 0), size)):
            raise ValueError('All size values must be positive numbers')

        sx, sy, sz = size
        source = self._source
        with self:
            source.SetXLength(sx)
            source.SetYLength(sy)
            source.SetZLength(sz)
            self.fire_event('size_changed')


    def get_center(self):
        with self:
            return self._source.GetCenter()


    def set_center(self, *args):
        center = _parse_vector3(args, 'center')
        with self:
            self._source.SetCenter(*center)
            self.fire_event('center_changed')


    size = property(fget=get_size, fset=set_size)
    center = property(fget=get_center, fset=set_center)





class Cylinder(Geometry):
    '''
    Represents a cylinder geometry
    '''
    def __init__(self, height=1, radius=0.25, center=(0, 0, 0), resolution=15):
        source = vtkCylinderSource()
        super().__init__(source)
        self._source = source
        self.set_height(height)
        self.set_radius(radius)
        self.set_resolution(resolution)
        self.set_center(center)


    def get_height(self):
        with self:
            return self._source.GetHeight()


    def set_height(self, height):
        height = _parse_size(height, 'height')
        with self:
            self._source.SetHeight(height)
            self.fire_event('height_changed')


    def get_radius(self):
        with self:
            return self._source.GetRadius()


    def set_radius(self, radius):
        radius = _parse_size(radius, 'radius')
        with self:
            self._source.SetRadius(radius)
            self.fire_event('radius_changed')


    def get_resolution(self):
        with self:
            return self._source.GetResolution()


    def set_resolution(self, resolution):
        resolution = _parse_resolution(resolution)
        with self:
            self._source.SetResolution(resolution)
            self.fire_event('resolution_changed')


    def get_center(self):
        with self:
            return self.GetCenter()

    def set_center(self, *args):
        center = _parse_vector3(args, 'center')
        with self:
            self._source.SetCenter(*center)
            self.fire_event('center_changed')


    radius = property(fget=get_radius, fset=set_radius)
    height = property(fget=get_height, fset=set_height)
    resolution = property(fget=get_resolution, fset=set_resolution)
    center = property(fget=get_center, fset=set_center)




class Cone(Cylinder):
    def __init__(self, height=1, radius=0.25, center=(0, 0, 0), direction=(1, 0, 0), resolution=15):
        source = vtkConeSource()
        Geometry.__init__(self, source)
        self._source = source
        self.set_height(height)
        self.set_radius(radius)
        self.set_resolution(resolution)
        self.set_center(center)
        self.set_direction(direction)

    def get_direction(self):
        with self:
            return self.GetDirection()

    def set_direction(self, *args):
        direction = _parse_vector3(args, 'direction')
        with self:
            self._source.SetDirection(*direction)
            self.fire_event('direction_changed')


    direction = property(fget=get_direction, fset=set_direction)




class Line(Geometry):
    def __init__(self, start, end):
        source = vtkLineSource()
        super().__init__(source)
        self._source = source
        self.set_start(start)
        self.set_end(end)


    def get_start(self):
        with self:
            return self._source.GetPoint1()

    def get_end(self):
        with self:
            return self._source.GetPoint2()

    def set_start(self, *args):
        point = _parse_vector3(args, 'start')
        with self:
            self._source.SetPoint1(*point)
            self.fire_event('start_point_changed')

    def set_end(self, *args):
        point = _parse_vector3(args, 'start')
        with self:
            self._source.SetPoint2(*point)
            self.fire_event('end_point_changed')

    start = property(fget=get_start, fset=set_start)
    end = property(fget=get_end, fset=set_end)
