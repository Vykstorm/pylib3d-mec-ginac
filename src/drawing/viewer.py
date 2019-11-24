'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkViewer
'''

######## Import statements ########

# imports from other modules
from .object import Object
from .color import Color

# vtk imports
from vtk import vtkRenderer, vtkRenderWindow, vtkCommand, vtkProp
from vtk import vtkRenderWindowInteractor





######## class VtkViewer ########

class VtkViewer(Object):
    '''
    This is a helper class to create a window and display 3d objects using vtk
    library
    '''

    def __init__(self):
        super().__init__()

        # Initialize internal fields
        self._interactor, self._window = None, None
        self._title = ''


        self.add_event_handler(self._event_handler)




    def _event_handler(self, event_type, source, *args, **kwargs):
        # This method is called when any event is fired by child object (or the viewer)

        if isinstance(source, Scene):
            if event_type == 'object_entered':
                # A scene was attached to the viewer
                window.AddRenderer(source._renderer)
            elif event_type == 'object_exit':
                # The scene was detached from the viewer
                window.RemoveRenderer(source._renderer)


        # For any change, redraw the scene
        self._redraw()




    def open(self):
        '''open()
        Open the window where the 3d objects will be displayed
        '''
        with self:
            if self._interactor is not None:
                raise RuntimeError('Viewer is being shown already')

            # Create the vtk window & interactor
            window = vtkRenderWindow()
            interactor = vtkRenderWindowInteractor()
            self._window, self._interactor = window, interactor

            # Set window title
            window.SetWindowName(self._title)

            # Set window size
            window.SetSize(640, 480)

            # Bind window to the interactor
            interactor.SetRenderWindow(window)

            # Bind scene renderer to the window
            scene = self.get_scene()
            if scene is not None:
                window.AddRenderer(scene._renderer)


            # Fire viewer open event
            self.fire_event('viewer_open')

            # Initialize & Start interactor
            interactor.Initialize()
            interactor.Start()





    def close(self):
        '''close()
        Closes the window where 3d objects are rendered
        '''
        with self:
            interactor, window = self._interactor, self._window
            if interactor is None:
                raise RuntimeError('Viewer is not open yet')

            # Destroy vtk window & interactor
            window.Finalize()
            interactor.TerminateApp()
            self._interactor, self._window = None, None

            self.fire_event('viewer_close')



    def is_open(self):
        '''is_open() -> bool
        Returns True after calling to open(). Otherwise, or after calling close(),
        this method returns False
        '''
        with self:
            return self._interactor is not None


    def is_closed(self):
        '''is_closed() -> bool
        This is an alias of ``not is_open()``

        .. seealso:: :func:`is_open`

        '''
        return not self.is_open()



    def get_scene(self):
        '''get_scene() -> Scene
        Get the 3D scene associated to the viewer if any. None otherwise.
        '''
        return next(iter(self.get_children(Scene)), None)



    def set_scene(self, scene):
        '''set_scene(scene: Scene)
        Set the 3D scene associated to the viewer.
        :type scene: Scene
        '''
        if not isinstance(scene, Scene):
            raise TypeError('Input argument must be a Scene object')
        with self:
            current_scene = self.get_scene()
            if current_scene is not None:
                self.remove_child(current_scene)
            self.add_child(scene)





    def set_title(self, title):
        '''set_title(title: str)
        Set the title of the window where 3d objects are being rendered
        '''
        if not isinstance(title, str):
            raise TypeError('title must be a str object')

        with self:
            self._title = title
            if self._interactor is not None:
                # Refresh vtk window title
                self._window.SetWindowName(title)
                self._interactor.Render()
            self.fire_event('title_changed', title)




    def _redraw(self):
        # Redraw the 3d objects and update the view
        with self:
            if self._interactor is None:
                return
            self._interactor.Render()




_viewer = VtkViewer()

def get_viewer():
    '''get_viewer() -> Viewer
    Get the viewer where the 3d scene will be shown

    :rtype: Viewer

    '''
    return _viewer





from .scene import Scene
