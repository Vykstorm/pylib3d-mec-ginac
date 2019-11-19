

from threading import RLock
from vtk import vtkRenderer, vtkRenderWindow, vtkCommand, vtkProp
from vtk import vtkGenericRenderWindowInteractor
from .object import Object



class VtkViewer(Object):
    '''
    This is a helper class to create a window and display 3d objects using vtk
    library
    '''

    def __init__(self):
        super().__init__()

        # Create vtk renderer
        renderer = vtkRenderer()

        # Set default camera position
        renderer.GetActiveCamera().SetPosition(5, 5, 5)

        # Set default background color
        renderer.SetBackground(1, 1, 1)


        # Initialize internal fields
        self._interactor, self._window = None, None
        self._title = ''
        self._renderer = renderer




    def open(self):
        '''open()
        Open the window where the 3d objects will be displayed
        '''
        renderer = self._renderer
        with self.lock:
            if self._interactor is not None:
                raise RuntimeError('Viewer is being shown already')

            # Create the vtk window & interactor
            window = vtkRenderWindow()
            interactor = vtkGenericRenderWindowInteractor()
            self._window, self._interactor = window, interactor

            # Set window title
            window.SetWindowName(self._title)

            # Added renderer to the window
            window.AddRenderer(renderer)

            # Set window size
            window.SetSize(640, 480)

            # Bind window to the interactor
            interactor.SetRenderWindow(window)

            # Initialize & Start interactor
            interactor.Initialize()
            interactor.Start()

            self.fire_event('viewer_open')




    def close(self):
        '''close()
        Closes the window where 3d objects are rendered
        '''
        with self.lock:
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
        with self.lock:
            return self._interactor is not None


    def is_closed(self):
        '''is_closed() -> bool
        This is an alias of ``not is_open()``

        .. seealso:: :func:`is_open`

        '''
        return not self.is_open()



    def set_title(self, title):
        '''set_title(title: str)
        Set the title of the window where 3d objects are being rendered
        '''
        if not isinstance(title, str):
            raise TypeError('title must be a str object')

        with self.lock:
            self._title = title
            if self._interactor is not None:
                # Refresh vtk window title
                self._window.SetWindowName(title)
                self._interactor.Render()
            self.fire_event('title_changed', title)



    def _redraw(self):
        # Redraw the 3d objects and update the view
        with self.lock:
            if self._interactor is not None:
                self._interactor.Render()



    def _add_actor(self, actor):
        assert isinstance(actor, vtkProp)

        with self.lock:
            self._renderer.AddActor(actor)



    def _remove_actor(self, actor):
        assert isinstance(actor, vtkProp)

        with self.lock:
            self._renderer.RemoveActor(actor)




    def _remove_all_actors(self):
        with self.lock:
            # Remove all actors from the renderer
            self._renderer.RemoveAllViewProps()
