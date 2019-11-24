'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''


######## Import statements ########

# standard imports
from itertools import repeat
from collections.abc import Iterable
from operator import gt
from functools import partial

# imports from other modules
from .object import VtkObjectWrapper

# vtk imports
from vtk import vtkPolyDataMapper, vtkActor, vtkMapper, vtkAlgorithm
from vtk import vtkPolyData, vtkPoints, vtkLine, vtkCellArray
from vtk import vtkSphereSource, vtkCubeSource, vtkConeSource, vtkCylinderSource
from vtk import vtkLineSource, vtkSTLReader, vtkSTLWriter



######## Helper methods ########


def _parse_size(value, argname=None):
    assert argname is None or isinstance(argname, str)
    try:
        value = float(value)
        if value < 0:
            raise TypeError
        return value
    except TypeError:
        if argname is None:
            raise TypeError('Input argument must be a positive argument')
        raise TypeError(f'{argname} must be a positive number')


def _parse_resolution(resolution):
    if not isinstance(resolution, int) or resolution <= 0:
        raise TypeError('resolution must be an integer greater than zero')
    return resolution


def _parse_vector3(x, argname=None):
    assert argname is None or isinstance(argname, str)
    try:
        if len(x) not in (1, 3):
            raise TypeError
        if len(x) == 1:
            x = tuple(x[0])
            if len(x) != 3:
                raise TypeError
    except TypeError:
        if argname is None:
            raise TypeError('Input argument must be a list with three number values')
        raise TypeError(f'Invalid number of components specified for {argname}')

    try:
        x = tuple(map(float, x))
        return x
    except TypeError:
        raise TypeError(f'{argname} must be a list of numbers')



def _parse_filename(filename):
    if not isinstance(filename, str):
        raise TypeError('filename must be a str object')
    return filename






_geometry_properties = {
    'radius': {
        'getter': 'get_radius',
        'setter': 'set_radius',
        'parser': partial(_parse_size, argname='radius')
    },
    'height': {
        'getter': 'get_height',
        'setter': 'set_height',
        'parser': partial(_parse_size, argname='height')
    },
    'direction': {
        'getter': 'get_direction',
        'setter': 'set_direction',
        'parser': partial(_parse_vector3, argname='direction')
    },
    'center': {
        'getter': 'get_center',
        'setter': 'set_center',
        'parser': partial(_parse_vector3, argname='center')
    },
    'resolution': {
        'getter': 'get_resolution',
        'setter': 'set_resolution',
        'parser': _parse_resolution
    }
}



######## Metaclass for class Geometry ########

class GeometryMeta(type):
    # Metaclass for the class Geometry
    def _register_property(cls, name):
        assert name in _geometry_properties

        getter, setter, parse = map(_geometry_properties[name].__getitem__, ('getter', 'setter', 'parser'))
        vtk_getter, vtk_setter = map(lambda name: name.title().replace('_', ''), (getter, setter))
        property_changed_event = f'{name}_changed'

        if not hasattr(cls, getter):
            def fget(self):
                assert self._source is not None
                func = getattr(self._source, vtk_getter)
                with self:
                    return func()

            setattr(cls, getter, fget)

        if not hasattr(cls, setter):
            def fset(self, value):
                assert self._source is not None
                func = getattr(self._source, vtk_setter)
                with self:
                    func(parse(value))
                    self.fire_event(property_changed_event)

            setattr(cls, setter, fset)

        if not hasattr(cls, name):
            setattr(cls, name, property(fget=getattr(cls, getter), fset=getattr(cls, setter)))





######## class Geometry ########

class Geometry(VtkObjectWrapper, metaclass=GeometryMeta):
    '''
    Instances of this class represents a 3D geometry mesh.
    '''
    def __init__(self, handler):
        assert isinstance(handler, (vtkAlgorithm, vtkPolyData))

        # Validate & parse input arguments
        mapper = vtkPolyDataMapper()
        if isinstance(handler, vtkAlgorithm):
            mapper.SetInputConnection(handler.GetOutputPort())
        else:
            mapper.SetInputData(handler)

        self._source = handler
        super().__init__(mapper)



    @classmethod
    def from_stl(self, filename):
        filename = _parse_filename(filename)
        reader = vtkSTLReader()
        reader.SetFileName(filename)
        reader.Update()
        return Geometry(reader)


    def to_stl(self, filename):
        filename = _parse_filename(filename)
        writer = vtkSTLWriter()
        writer.SetFileName(filename)
        if isinstance(self._source, vtkAlgorithm):
            writer.SetInputConnection(self._source.GetOutputPort())
        else:
            writer.SetInputData(self._source)
        writer.Write()




def read_stl(filename):
    return Geometry.from_stl(filename)



def write_stl(geometry, filename):
    if not isinstance(geometry, Geometry):
        raise TypeError('geometry must be an isntance of the class Geometry')
    geometry.to_stl(filename)






######## class Sphere ########

class Sphere(Geometry):
    '''
    This represents a sphere geometry
    '''
    def __init__(self, radius=1, center=(0, 0, 0), resolution=15):
        super().__init__(vtkSphereSource())
        self.set_radius(radius)
        #self.set_resolution(resolution)
        self.set_center(center)
        self.set_resolution(resolution)


    def get_resolution(self):
        with self:
            return self._source.GetThetaResolution()


    def set_resolution(self, resolution):
        resolution = _parse_resolution(resolution)
        with self:
            self._source.SetThetaResolution(resolution)
            self._source.SetPhiResolution(resolution)
            self.fire_event('resolution_changed')


Sphere._register_property('radius')
Sphere._register_property('center')
Sphere._register_property('resolution')




######## class Cube ########

class Cube(Geometry):
    '''
    This represents a cube geometry
    '''
    def __init__(self, size=1, center=(0, 0, 0)):
        super().__init__(vtkCubeSource())
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


    size = property(fget=get_size, fset=set_size)

Cube._register_property('center')




######## class Cylinder ########

class Cylinder(Geometry):
    '''
    Represents a cylinder geometry
    '''
    def __init__(self, height=1, radius=0.25, center=(0, 0, 0), resolution=15):
        super().__init__(vtkCylinderSource())
        self.set_height(height)
        self.set_radius(radius)
        self.set_resolution(resolution)
        self.set_center(center)


Cylinder._register_property('height')
Cylinder._register_property('radius')
Cylinder._register_property('resolution')
Cylinder._register_property('center')




######## class Cone ########

class Cone(Geometry):
    '''
    Represents a cone geometry
    '''
    def __init__(self, height=1, radius=0.25, center=(0, 0, 0), direction=(1, 0, 0), resolution=15):
        Geometry.__init__(self, vtkConeSource())
        self.set_height(height)
        self.set_radius(radius)
        self.set_resolution(resolution)
        self.set_center(center)
        self.set_direction(direction)


Cone._register_property('height')
Cone._register_property('radius')
Cone._register_property('resolution')
Cone._register_property('center')
Cone._register_property('direction')




######## class Line ########

class Line(Geometry):
    '''
    Represents a line geometry
    '''
    def __init__(self, start, end):
        super().__init__(vtkLineSource())
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




######## class LineStrip ########

class LineStrip(Geometry):
    '''
    Represents a line strip geometry
    '''
    def __init__(self, points):
        if not isinstance(points, Iterable):
            raise TypeError('Input argument must be an iterable')
        try:
            points = tuple(map(_parse_vector3, points))
        except TypeError:
            raise TypeError('All points must be a a list of three number values')

        n = len(points)


        lines_data = vtkPolyData()

        # Create the set of points
        _points = vtkPoints()
        for point in points:
            _points.InsertNextPoint(*point)

        lines_data.SetPoints(_points)

        # Connect the points using lines
        lines = vtkCellArray()

        for i in range(1, n):
            line = vtkLine()
            line.GetPointIds().SetId(0, i-1)
            line.GetPointIds().SetId(1, i)
            lines.InsertNextCell(line)

        lines_data.SetLines(lines)
        super().__init__(lines_data)
