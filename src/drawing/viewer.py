'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkViewer
'''

######## Import statements ########

# standard imports
from threading import Condition, RLock, Event
from time import sleep
from operator import methodcaller, eq
from functools import partial

# imports from other modules
from .events import EventProducer
from .color import Color
from ..core.system import get_default_system

# vtk imports
from vtk import vtkRenderer, vtkRenderWindow, vtkCommand, vtkProp
from vtk import vtkRenderWindowInteractor, vtkPropPicker, vtkInteractorStyleTrackballCamera





######## class VtkViewer ########

class VtkViewer(EventProducer):
    '''
    This is a helper class to create a window and display 3d objects using vtk
    library
    '''

    ######## Constructor ########

    def __init__(self):
        lock = RLock()
        super().__init__(lock)

        # Default title for the viewer window
        title = 'lib3d-mec-ginac 3D viewer'


        # Initialize internal fields
        self._interactor, self._window = None, None
        self._prev_viewport_size = None
        self._selected_drawing = None
        self._title = title
        self._open_request = False
        self._redraw_request = False
        self._prev_viewport_size = None
        self._selected_drawing = None
        self._state = 'closed'
        self._cv = Condition(lock=lock)
        self._is_main_running = Event()


        # Add event handlers
        self.add_event_handler(self._on_any_event)
        self.add_event_handler(self._on_resized, 'resized')
        self.add_event_handler(self._on_object_entered, 'object_entered')




    ######## Event handlers ########



    def _on_resized(self, *args, **kwargs):
        # This function is called when the window is resized
        scene = self.get_scene()
        if scene is not None:
            # We need to update scene 2D drawings (because their positions could be
            # relative to the viewport size)
            scene._update_2D_drawings()


    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if isinstance(source, Scene) and self._interactor is not None:
            # A new scene was attached to the viewer
            self._window.AddRenderer(source._renderer)


    def _on_object_exit(self, event_type, source, *args, **kwargs):
        if isinstance(source, Scene) and self._interactor is not None:
            # The scene was detached from the viewer
            self._window.RemoveRenderer(source._renderer)
            if self._selected_drawing is not None:
                self._selected_drawing.unselect()
                self._selected_drawing = None


    def _on_any_event(self, *args, **kwargs):
        # If any event happened, redraw the scene
        self._redraw()




    def _wait_until_open_request(self):
        # Wait until the open request is sent
        while not self._open_request:
            self._cv.wait()
        # Clear open request flag
        self._open_request = False


    def _initialize(self):
        # Create interactor & window
        window, interactor = vtkRenderWindow(), vtkRenderWindowInteractor()
        self._window, self._interactor = window, interactor

        # Set window title
        window.SetWindowName(self._title)

        # Set window size
        window.SetSize(640, 480)

        # Bind window to the interactor
        interactor.SetRenderWindow(window)

        # Initialize interactor
        interactor.Initialize()

        # Create a repeating timer which redraws the scene and sleeps the event loop thread half
        # of the time to release the GIL
        def timer_event_handler(*args, **kwargs):
            self._update()
            # Sleep the main thread to free the GIL for a while
            sleep(0.02)


        interactor.CreateRepeatingTimer(10)
        interactor.AddObserver(vtkCommand.TimerEvent, timer_event_handler)

        # Add an event handler which is invoked when the window is modified. This will trigger the event
        # 'resized' when the viewport size is changed
        def modified_event_handler(*args, **kwargs):
            renderer = self.get_scene()._renderer
            current_size = renderer.GetSize()
            prev_size = self._prev_viewport_size
            if prev_size is None or current_size != prev_size:
                self.fire_event('resized')
            self._prev_viewport_size = current_size

        interactor.AddObserver(vtkCommand.ModifiedEvent, modified_event_handler)

        # Add an event handler which is invoked when the user clicks on the screen. This will manage
        # 3D object selection
        def click_event_handler(*args, **kwargs):
            scene = self.get_scene()
            renderer = scene._renderer

            # Get mouse click position
            x, y = interactor.GetEventPosition()
            picker = vtkPropPicker()
            # Get the 3D model which is clicked
            picker.Pick(x, y, 0, renderer)
            # Get the drawing attached to the 3D model clicked
            drawing = scene._get_3D_drawing_by_handler(picker.GetActor())
            # Select the drawing clicked (and unselect the previous selected drawing if any)
            with self:
                prev_selected_drawing = self._selected_drawing

                if drawing is not None:
                    if self._selected_drawing != drawing:
                        self._selected_drawing = None
                        if prev_selected_drawing is not None:
                            prev_selected_drawing.unselect()
                        self._selected_drawing = drawing
                        drawing.select()
                else:
                    # User clicker to the screen but it didnt select anything
                    if prev_selected_drawing is not None:
                        self._selected_drawing = None
                        prev_selected_drawing.unselect()


        interactor.AddObserver(vtkCommand.LeftButtonPressEvent, click_event_handler)


        # Bind scene to the renderer
        scene = self.get_scene()
        if scene is not None:
            window.AddRenderer(scene._renderer)


        # Set interaction style
        interaction_style = vtkInteractorStyleTrackballCamera()
        interactor.SetInteractorStyle(interaction_style)





    def _destroy(self):
        # Destroy vtk window & interactor (if not done yet)
        if self._interactor is not None:
            self._window.Finalize()
            self._interactor.TerminateApp()
            self._window, self._interactor = None, None


    def _main_event_loop(self):
        self._interactor.Start()


    def _main(self):
        cv = self._cv

        # Create interactor & window
        self._initialize()

        # Change viewer state & fire open event
        self._state = 'open'
        cv.notify()
        self.fire_event('open')

        # Attach the scene of the default system if no scene was attached yet
        if self.get_scene() is None:
            self.set_scene(get_default_system().get_scene())

        # Start main event loop
        cv.release()
        self._main_event_loop()
        cv.acquire()

        # Window was closed by close() method or by the user
        self._destroy()

        # Change viewer state & fire close event
        self._state = 'closed'
        cv.notify()
        self.fire_event('closed')



    def main(self, open=False):
        self._is_main_running.set()
        self._cv.acquire()
        if open:
            self._main()
        while True:
            # Wait until an open request is sent
            self._wait_until_open_request()

            self._main()




    def open(self):
        '''open()
        Open the viewer
        '''
        cv = self._cv
        with cv:
            if self._is_main_running.is_set():
                if self._state == 'open':
                    raise RuntimeError('viewer already open')

                self._open_request = True
                cv.notify()
                while self._state == 'closed':
                    cv.wait()
            else:
                self._main()





    def close(self):
        '''close()
        Closes the viewer
        '''
        # TODO
        cv = self._cv
        with cv:
            if self._state == 'closed':
                raise RuntimeError('viewer is not open yet')
            self._destroy()
            while self._state == 'open':
                cv.wait()





    def is_open(self):
        '''is_open() -> bool
        Returns True after calling to open(). Otherwise, or after calling close(),
        this method returns False
        '''
        with self:
            return self._state == 'open'


    def is_closed(self):
        '''is_closed() -> bool
        This is an alias of ``not is_open()``

        .. seealso:: :func:`is_open`

        '''
        return not self._state == 'closed'



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



    def get_selected_drawing(self):
        '''get_selected_drawing() -> Drawing3D | None
        Get the current selected 3D drawing by the user if any. None otherwise.
        '''
        with self:
            return self._selected_drawing



    def _update(self):
        # Redraw the scene if requested
        with self:
            if self._state == 'open':
                if self._redraw_request:
                    self._interactor.Render()
                self._redraw_request = False

    def _redraw(self):
        # Redraw the 3d objects and update the view
        with self:
            self._redraw_request = True



# This import is moved here to avoid circular dependencies
from .scene import Scene







_viewer = VtkViewer()


def get_viewer():
    '''get_viewer() -> Viewer
    Get the viewer where the 3d scene will be shown

    :rtype: Viewer

    '''
    return _viewer


def show_viewer():
    '''show_viewer()
    Open the viewer window
    '''
    get_viewer().open()


def close_viewer():
    '''close_viewer()
    Closes the viewer window
    '''
    get_viewer().close()


def get_selected_drawing():
    '''get_selected_drawing() -> Drawing3D | None
    Get the current 3D drawing selected by the user

    :rtype: Drawing3D | None

    '''
    return get_viewer().get_selected_drawing()
