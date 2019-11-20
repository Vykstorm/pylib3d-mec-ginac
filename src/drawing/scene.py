

from .object import Object
from .viewer import VtkViewer
from .simulation import Simulation
from .geometry import Geometry
from .color import Color
from threading import RLock
from operator import methodcaller
from itertools import chain


class Scene(Object):
    def __init__(self, system):
        super().__init__()
        self._viewer, self._system = VtkViewer(), system
        self._simulation = Simulation(self, system)

        self.add_event_handler(self._event_handler)
        self.add_child(self._viewer)
        self.add_child(self._simulation)



    def get_viewer(self):
        '''get_viewer() -> Viewer
        Get the viewer object associated to this scene
        '''
        return self._viewer



    def is_simulation_running(self):
        '''is_simulation_running() -> bool
        Returns True if the simulation is running. False otherwise.
        '''
        return self._simulation.is_running()



    def is_simulation_paused(self):
        '''is_simulation_paused() -> bool
        Returns True if the simulation is paused. False otherwise.
        '''
        return self._simulation.is_paused()



    def is_simulation_stopped(self):
        '''is_simulation_stopped() -> bool
        Returns True if the simulation is stopped. False otherwise.
        '''
        return self._simulation.is_stopped()



    def get_simulation_update_frequency(self):
        '''get_simulation_update_frequency() -> float
        Returns the current simulation update frequency (in number of updates per second)

        :rtype: float

        '''
        return self._simulation.get_update_frequency()



    def set_simulation_update_frequency(self, frequency):
        '''set_simulation_update_frequency(frequency: numeric)
        Change the simulation update frequency.

        :param frequency: The new simulation update frequency (in number of updates per second)

        '''
        self._simulation.set_update_frequency(frequency)



    def get_simulation_time_multiplier(self):
        '''get_simulation_time_multiplier() -> float
        Returns the current simulation time multiplier

        :rtype: float

        '''
        return self._simulation.get_time_multiplier()



    def set_simulation_time_multiplier(self, multiplier):
        '''set_simulation_time_multiplier(multiplier: numeric)
        Change the simulation time multiplier

        :param multiplier: The new simulation time multiplier

        '''
        self._simulation.set_time_multiplier(multiplier)



    def get_drawings(self):
        '''get_drawings() -> List[Drawing3D]
        Get all the drawings previously created in the scene
        '''
        return self.get_children(kind=Drawing3D)



    def start_simulation(self):
        '''start_simulation()
        Starts the simulation

        :raises RuntimeError: If the simulation already started

        '''
        self._simulation.start()



    def stop_simulation(self):
        '''stop_simulation()
        Stops the simulation

        :raises RuntimeError: If the simulation is already stopped

        '''
        self._simulation.stop()



    def resume_simulation(self):
        '''resume_simulation()
        Resumes the simulation

        :raises RuntimeError: If the simulation is not paused

        '''
        self._simulation.resume()



    def pause_simulation(self):
        '''pause_simulation()
        Pauses the simulation

        :raises RuntimeError: If the simulation is not running

        '''
        self._simulation.pause()



    def are_drawings_shown(self):
        '''are_drawings_shown() -> bool
        Returns True if the drawing objects are being shown. False otherwise.
        '''
        return self._viewer.is_open()



    def show_drawings(self):
        '''show_drawings()
        Show the drawing objects
        '''
        viewer = self._viewer
        # Open viewer & redraw
        viewer.open()
        self._redraw()



    def hide_drawings(self):
        '''hide_drawings()
        Close the window which shows the drawing objects
        '''
        # Close the viewer
        self._viewer.close()



    def purge_drawings(self):
        '''purge_drawings()
        Remove all the drawing objects created previously
        '''
        viewer = self._viewer
        with self.lock:
            drawings = self.get_drawings()
            # Clear drawings
            drawings.clear()
            # Remove all vtk actors in the viewer
            viewer._remove_all_actors()
            # Redraw
            self._redraw()



    def get_background_color(self):
        '''get_background_color() -> Color
        Get the background color of the viewer

        :rtype: Color

        '''
        return self._viewer.get_background_color()



    def set_background_color(self, *args):
        '''set_background_color(...)
        Change the background color of the viewer
        '''
        self._viewer.set_background_color(*args)



    def add_drawing(self, drawing):
        '''add_drawing(drawing: Drawing3D)
        Add a new drawing object to the scene
        '''
        if not isinstance(drawing, Drawing3D):
            raise TypeError('Input argument must be a Drawing3D instance')
        self.add_child(drawing)




    def draw_point(self, *args, **kwargs):
        # Create point drawing
        # Add point to drawing to the scene
        # TODO
        pass


    def _event_handler(self, event_type, source, *args, **kwargs):
        if event_type == 'simulation_step':
            self._update()
            return

        if isinstance(source, Drawing3D):
            if event_type == 'object_entered':
                with source.lock:
                    source._system = self._system
                self._viewer._add_actor(source.get_actor())

            elif event_type == 'object_exit':
                self._viewer._remove_actor(source.get_actor())

        # Redraw the scene if a drawing object property, geometry or color changed
        if isinstance(source, (Drawing3D, Color)):
            self._redraw()



    def _update(self):
        '''
        Updates the scene
        '''
        with self.lock:
            drawings = self.get_drawings()

            # Update drawings
            for drawing in drawings:
                drawing._update()

            # Redraw scene
            self._redraw()



    def _redraw(self):
        '''
        Redraws the scene
        '''
        viewer = self._viewer
        # Lock this scene and all the drawings, geometry and color objects
        self.lock.acquire()
        objs = tuple(filter(lambda obj: isinstance(obj, (Drawing3D, Geometry, Color)), self.get_predecessors()))
        for obj in objs:
            obj.lock.acquire()

        # Redraw the scene
        viewer._redraw()

        # Unlock everything
        for obj in objs:
            obj.lock.release()
        self.lock.release()




# This import is moved here to avoid circular dependencies
from .drawing import Drawing3D
