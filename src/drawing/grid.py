


######## Import statements ########

from .drawing import Drawing
from vtk import vtkPoints, vtkPolyData, vtkLine, vtkCellArray, vtkPolyDataMapper, vtkActor, vtkUnsignedCharArray
from .color import Color


class GridDrawing(Drawing):
    def __init__(self, size=15, line_space=1):
        assert size >= 1 and line_space > 0
        if size%2 == 0:
            size += 1

        n, s = size, line_space

        linesPolyData = vtkPolyData()
        points = vtkPoints()
        colors = vtkUnsignedCharArray()
        lines = vtkCellArray()

        # Generate grid points
        for i in range(0, n):
            o = (n-1)*s/2
            points.InsertNextPoint((i*s-o,      0,  -o,            ))
            points.InsertNextPoint((i*s-o,      0,  (n-1)*s-o      ))
            points.InsertNextPoint((-o,         0,  i*s-o,         ))
            points.InsertNextPoint(((n-1)*s-o,  0,  i*s-o,         ))

        linesPolyData.SetPoints(points)

        # Create lines & colors
        for i in range(0, 4*n, 2):
            line = vtkLine()
            line.GetPointIds().SetId(0, i)
            line.GetPointIds().SetId(1, i+1)
            lines.InsertNextCell(line)
            colors.SetNumberOfComponents(4)
            if i == 2*(n-1):
                colors.InsertNextTuple((0, 0, 255, 255))
            elif i == 2*n:
                colors.InsertNextTuple((255, 0, 0, 255))
            else:
                colors.InsertNextTuple((125, 125, 125, 125))

        linesPolyData.SetLines(lines)
        linesPolyData.GetCellData().SetScalars(colors)

        mapper = vtkPolyDataMapper()
        mapper.SetInputData(linesPolyData)

        actor = vtkActor()
        actor.SetMapper(mapper)

        super().__init__(actor)
        self.color.alpha = 1
