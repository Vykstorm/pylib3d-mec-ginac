

from threading import RLock
from vtk import vtkRenderer, vtkRenderWindow, vtkCommand
from vtk import vtkGenericRenderWindowInteractor



class VtkViewer:
    '''
    This is a helper class to create a window and display 3d objects using vtk
    library
    '''

    def __init__(self):
        # Create vtk renderer
        renderer = vtkRenderer()

        # Set default camera position
        renderer.GetActiveCamera().SetPosition(5, 5, 5)

        # Set default background color
        renderer.SetBackground(1, 1, 1)


        # Initialize internal fields
        self._lock = RLock()
        self._interactor, self._window = None, None
        self._title = ''
        self._renderer = renderer




    def open(self):
        '''open()
        Open the window where the 3d objects will be displayed
        '''
        renderer = self._renderer
        with self._lock:
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




    def close(self):
        '''close()
        Closes the window where 3d objects are rendered
        '''
        with self._lock:
            interactor, window = self._interactor, self._window
            if interactor is None:
                raise RuntimeError('Viewer is not open yet')

            # Destroy vtk window & interactor
            window.Finalize()
            interactor.TerminateApp()
            self._interactor, self._window = None, None



    def is_open(self):
        '''is_open() -> bool
        Returns True after calling to open(). Otherwise, or after calling close(),
        this method returns False
        '''
        with self._lock:
            return self._interactor is not None


    def is_closed(self):
        '''is_closed() -> bool
        This is an alias of ``not is_open()``

        .. seealso:: :func:`is_open`

        '''
        return not self.is_open()


    def redraw(self):
        '''redraw()
        Redraw the 3d objects and update the view
        '''
        with self._lock:
            if self._interactor is not None:
                self._interactor.Render()


    def set_title(self, title):
        '''set_title(title: str)
        Set the title of the window where 3d objects are being rendered
        '''
        if not isinstance(title, str):
            raise TypeError('title must be a str object')

        with self._lock:
            self._title = title
            if self._interactor is not None:
                # Refresh vtk window title
                self._window.SetWindowName(title)
                self._interactor.Render()


    def add_actor(self, actor):
        '''add_actor(actor)
        Add a new 3d object to the view.

        :param actor: Must be a vtk.vtkProp instance (normally vtk.vtkActor objects)

        '''
        with self._lock:
            self._renderer.AddActor(actor)


    def remove_all_actors(self):
        '''remove_all_actors()
        Remove all the 3d objects previosuly created.
        '''
        with self._lock:
            # Remove all actors from the renderer
            self._renderer.RemoveAllViewProps()
