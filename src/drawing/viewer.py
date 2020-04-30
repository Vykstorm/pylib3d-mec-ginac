'''
Author: Víctor Ruiz Gómez
Description: This file defines the class VtkViewer
'''

######## Import statements ########

# standard imports


# imports from other modules
from .events import EventProducer
from ..utils.singleton import singleton
from .scene import Scene
from .timer import Timer
from ..core.system import get_default_system

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
        self._iren, self._rw = None, None


        # Add the scene associated to the default system as the active scene
        self.add_child(get_default_system().get_scene())

        # Add a timer to render the scene periodically
        timer = Timer(interval=1/30)
        self.add_child(timer)
        timer.start()

        # Add event handlers
        self.add_event_handler(self._on_object_entered, 'object_entered')
        self.add_event_handler(self._on_object_exit, 'object_exit')
        self.add_event_handler(self._on_any_event)
        timer.add_event_handler(lambda *args, **kwargs: self._redraw())


    def _init(self, iren):
        '''
        This method is used to set up the window renderer interactor which must
        be passed as argument
        '''
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




    ######## Viewer routines ########

    def _redraw(self):
        '''
        Redraw all the entities of the scene on the viewer
        '''
        if self._iren is None:
            return
        self._iren.Render()



    ######## Getters ########

    def get_scene(self):
        '''get_scene() -> Scene
        Get the current 3D scene associated to the viewer if any. None otherwise.
        '''
        return next(iter(self.get_children(Scene)), None)



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




def get_viewer():
    '''get_viewer() -> Viewer
    Get the viewer where the 3d scene will be shown

    :rtype: Viewer

    '''
    return VtkViewer()


def show_viewer():
    '''show_viewer()
    Open the viewer window
    '''
    # TODO
    raise NotImplementedError


def close_viewer():
    '''close_viewer()
    Closes the viewer window
    '''
    # TODO
    raise NotImplementedError


def get_selected_drawing():
    '''get_selected_drawing() -> Drawing3D | None
    Get the current 3D drawing selected by the user

    :rtype: Drawing3D | None

    '''
    return None
