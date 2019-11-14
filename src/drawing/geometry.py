'''
Author: Víctor Ruiz Gómez
Description:
This file defines the helper functions to build 3d geometry (with VTK)
'''


from vtk import vtkPolyDataMapper, vtkActor, vtkAssembly
from vtk import vtkSphereSource, vtkConeSource, vtkCylinderSource, vtkLineSource
from vtk import vtkPolyData, vtkPoints, vtkCellArray, vtkLine, vtkCubeSource
from vtk import vtkSTLReader


def _create_vtk_actor(source):
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
    origin = vtkActor()
    origin.SetMapper(mapper)
    return origin


def _create_assembly_geometry(*args):
    assembly = vtkAssembly()
    for part in args:
        assembly.AddPart(part)
    return assembly


def _create_sphere_geometry(radius=1, resolution=15):
    source = vtkSphereSource()
    source.SetRadius(radius)
    source.SetThetaResolution(resolution)
    source.SetPhiResolution(resolution)
    return _create_vtk_actor(source)


def _create_box_geometry(size=1):
    source = vtkCubeSource()
    source.SetXLength(size[0])
    source.SetYLength(size[1])
    source.SetZLength(size[2])
    return _create_vtk_actor(source)


def _create_cone_geometry(height=1, radius=0.25, direction=(0, 1, 0), resolution=20):
    source = vtkConeSource()
    source.SetDirection(*direction)
    source.SetHeight(height)
    source.SetRadius(radius)
    source.SetResolution(resolution)
    return _create_vtk_actor(source)


def _create_cylinder_geometry(height=1, radius=0.25, resolution=20):
    source = vtkCylinderSource()
    source.SetHeight(height)
    source.SetRadius(radius)
    source.SetResolution(resolution)
    return _create_vtk_actor(source)


def _create_line_geometry(start, end):
    source = vtkLineSource()
    source.SetPoint1(*start)
    source.SetPoint2(*end)
    return _create_vtk_actor(source)


def _create_line_strip_geometry(points):
    points = tuple(points)
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

    mapper = vtkPolyDataMapper()
    mapper.SetInputData(lines_data)
    actor = vtkActor()
    actor.SetMapper(mapper)
    return actor



def _create_arrow_geometry(size=1, shaft_radius=0.03, tip_radius=0.1, tip_size=0.25,
    shaft_resolution=10, tip_resolution=25):

    shaft_size = size - tip_size

    # Create the shaft
    shaft = _create_cylinder_geometry(height=shaft_size, radius=shaft_radius, resolution=shaft_resolution)
    shaft.SetPosition(shaft_size/2, 0, 0)
    shaft.SetOrientation(0, 0, 90)

    # Create the tip
    tip = _create_cone_geometry(radius=tip_radius, height=tip_size, resolution=tip_resolution, direction=(1, 0, 0))
    tip.SetPosition(shaft_size+tip_size/2, 0, 0)

    return _create_assembly_geometry(shaft, tip), shaft, tip




def _create_geometry_from_stl(filename):
    reader = vtkSTLReader()
    reader.SetFileName(filename)
    return _create_vtk_actor(reader)
