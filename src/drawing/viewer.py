'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkViewer
'''

######## Import statements ########

# standard imports
from functools import wraps
import warnings

# imports from other modules
from ..utils.events import EventProducer
from ..utils.singleton import singleton
from .scene import Scene
from .timer import Timer
from ..core.system import get_default_system
from ..gui import DefaultGUI, IDEGUI

# vtk imports
from vtk import vtkRenderer, vtkRenderWindow, vtkCommand, vtkProp, vtkRenderWindowInteractor
from vtk import vtkRenderWindowInteractor, vtkPropPicker, vtkInteractorStyleTrackballCamera



######## class VtkViewer ########

@singleton
class VtkViewer(EventProducer):
    '''
    This is a helper class to create a window and display 3d objects using vtk
    library
    '''

    ######## Constructor ########

    def __init__(self):
        super().__init__()
        self._selected_drawing = None
        self._is_open = False


        # Add the scene associated to the default system as the active scene
        self.add_child(get_default_system().get_scene())

        # Add a timer to render the scene periodically
        timer = Timer(interval=1/30)
        self.add_child(timer)
        timer.start()
        self._update_timer = timer

        # Add event handlers
        self.add_event_handler(self._on_object_entered, 'object_entered')
        self.add_event_handler(self._on_object_exit, 'object_exit')
        self.add_event_handler(self._on_any_event)
        timer.add_event_handler(lambda *args, **kwargs: self._refresh())



    def open(self, gui=False):
        '''open(gui: bool)
        Open the viewer

        :param gui: If True, open the graphical user interface which embeds the
            3D viewer and provides an integrated python terminal console to execute
            code. If False ( default value ), just open the 3D viewer.

        '''
        if self._is_open:
            warnings.warn('Viewer is already open')
            return

        # Choose the graphical user interface to use
        gui_class = IDEGUI if gui else DefaultGUI
        gui = gui_class(self)
        iren = gui.build()

        rw = iren.GetRenderWindow()
        self._iren, self._rw = iren, rw

        # Set interaction style
        interaction_style = vtkInteractorStyleTrackballCamera()
        iren.SetInteractorStyle(interaction_style)

        # Add scene renderer to the window
        scene = self.get_scene()
        if scene is not None:
            rw.AddRenderer(scene._renderer)

        iren.CreateRepeatingTimer(1)
        iren.AddObserver(vtkCommand.TimerEvent, self._timer_event)
        iren.AddObserver(vtkCommand.LeftButtonPressEvent, self._click_event)

        self._is_open = True
        try:
            gui.main()
        finally:
            del self._iren, self._rw
            gui.destroy()
            self._is_open = False



    ######## Viewer routines ########

    def _redraw(self):
        '''
        Redraw all the entities of the scene on the viewer
        '''
        if not self._is_open:
            return
        self._iren.Render()



    ######## Getters ########

    def get_scene(self):
        '''get_scene() -> Scene
        Get the current 3D scene associated to the viewer if any. None otherwise.
        '''
        return next(iter(self.get_children(Scene)), None)


    def get_selected_drawing(self):
        '''get_selected_drawing() -> Drawing3D | None
        Get the current 3D drawing selected by the user if any. None otherwise
        '''
        return self._selected_drawing


    def get_drawing_refresh_rate(self):
        '''get_drawing_refresh_rate() -> float
        Get the refresh rate
        '''
        return 1/self._update_timer.get_time_interval()



    ######## Setters ########


    def set_scene(self, scene):
        '''set_scene(scene: Scene)
        Set the 3D scene associated to the viewer.
        :type scene: Scene
        '''
        if not isinstance(scene, Scene):
            raise TypeError('Input argument must be a Scene object')

        current_scene = self.get_scene()
        if current_scene is not None:
            self.remove_child(current_scene)
        self.add_child(scene)


    def set_drawing_refresh_rate(self, freq):
        '''set_refresh_rate(freq: float)

        Change the current refresh rate of the viewer
        '''
        try:
            freq = float(freq)
            if freq <= 0:
                raise ValueError('Drawing refresh rate must be a number greater than zero')
        except TypeError:
            raise TypeError('Argument should be a number')
        self._update_timer.set_time_interval(1/freq)
        self.fire_event('drawing_refresh_rate_changed')




    ######## Event handlers ########


    def _on_object_entered(self, event_type, source, *args, **kwargs):
        # This handler is called when a child object is added to this instance
        if isinstance(source, Scene) and self._rw is not None:
            self._rw.AddRenderer(source._renderer)


    def _on_object_exit(self, event_type, source, *args, **kwargs):
        # This handler is called when a child object is removed from this instance
        if isinstance(source, Scene) and self._rw is not None:
            self._rw.RemoveRenderer(source._renderer)


    def _on_any_event(self, event_type, *args, **kwargs):
        # This handler is invoked when any event is triggered
        #if event_type != 'simulation_step':
        #    self._redraw()
        pass


    def _timer_event(self, *args, **kwargs):
        # This handler is invoked repeatedly

        # Update timers
        self._update_timers()


    def _update_timers(self):
        for timer in self.get_predecessors(kind=Timer):
            timer._update()


    def _refresh(self):
        # Refresh the scene
        scene = self.get_scene()
        if scene is not None:
            scene._update_drawings()
        self._redraw()


    def _click_event(self, *args, **kwargs):
        if not self._is_open:
            return
        # This handler is invoked when the user clicks inside the viewport
        scene = self.get_scene()
        if scene is None:
            return
        renderer = scene._renderer

        # Get mouse click position
        x, y = self._iren.GetEventPosition()
        picker = vtkPropPicker()
        # Get the 3D model which is clicked
        picker.Pick(x, y, 0, renderer)
        # Get the drawing attached to the 3D model clicked
        drawing = scene._get_3D_drawing_by_handler(picker.GetActor())
        # Get the previous selected object and store current selection
        prev_selected_drawing = self._selected_drawing
        self._selected_drawing = drawing

        if drawing is None:
            # Nothing is selected currently
            if prev_selected_drawing is not None:
                prev_selected_drawing.unselect()
        else:
            # A 3D object was selected
            if drawing is not prev_selected_drawing:
                if prev_selected_drawing is not None:
                    prev_selected_drawing.unselect()
                drawing.select()





def get_viewer():
    '''get_viewer() -> Viewer
    Get the viewer where the 3d scene will be shown

    :rtype: Viewer

    '''
    return VtkViewer()


def open_viewer(*args, **kwargs):
    get_viewer().open(*args, **kwargs)
open_viewer.__doc__ = VtkViewer.cls.open.__doc__


def get_selected_drawing():
    return get_viewer().get_selected_drawing()
get_selected_drawing.__doc__ = VtkViewer.cls.get_selected_drawing.__doc__


def get_drawing_refresh_rate():
    return get_viewer().get_drawing_refresh_rate()
get_drawing_refresh_rate.__doc__ = VtkViewer.cls.get_drawing_refresh_rate.__doc__


def set_drawing_refresh_rate(*args, **kwargs):
    return get_viewer().set_drawing_refresh_rate(*args, **kwargs)
set_drawing_refresh_rate.__doc__ = VtkViewer.cls.set_drawing_refresh_rate.__doc__
