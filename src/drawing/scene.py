'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Scene
'''


######## Imports ########

from vtk import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkNamedColors
from .point import PointDrawing



######## class Scene ########

class DrawingScene:
    '''
    An instance of this class represents a 3D renderable scene.
    '''

    ######## Constructor ########

    def __init__(self):
        # Create the vtk renderer, window & interactor objects
        renderer = vtkRenderer()
        window = vtkRenderWindow()
        interactor = vtkRenderWindowInteractor()

        # Added renderer to the window
        window.AddRenderer(renderer)

        # Set default window size
        window.SetSize(640, 480)

        # Set render window to the interactor
        interactor.SetRenderWindow(window)

        # Initialize internal fields
        self._renderer, self._window, self._interactor = renderer, window, interactor
        self._drawings = []





    ######## Creation routines ########


    def draw_point(self, *args, **kwargs):
        drawing = PointDrawing(*args, **kwargs)
        self._drawings.append(drawing)
        return drawing





    ######## Getters ########


    def get_drawings(self, kind=None):
        '''get_drawings([kind: str]) -> List[Drawing3D]
        Get all the drawings created of the given type.

        :type kind: Must be the type of drawings to query. It can be
            'point', 'vector', 'frame' or 'line'.
            It can also be None. In that case, all the drawings are returned

        :rtype: List[Drawing]

        '''
        pass



    def get_point_drawings(self):
        '''get_point_drawings() -> List[PointDrawing]
        Get all the point drawings created

        :rtype: List[PointDrawing]

        .. seealso:: :func:`get_drawings`

        '''
        return self.get_drawings(kind='point')





    ######## Show / hide scene ########


    def show_scene(self):
        pass


    def hide_scene(self):
        pass






    ######## Properties ########


    @property
    def drawings(self):
        '''
        Only read property that returns a list with all the drawings created.

        :rtype: List[Drawing]

        .. seealso:: :func:`get_drawings`

        '''
        return self.get_drawings()


    @property
    def point_drawings(self):
        '''
        Only read property that returns a list with all the point drawings created.

        :rtype: List[PointDrawing]

        .. seealso:: :func:`get_point_drawings`

        '''
        return self.get_point_drawings()
