

from .viewer import VtkViewer
from .simulation import Simulation
from threading import RLock
from operator import methodcaller
from itertools import chain


class Scene:
    def __init__(self, system):
        self._viewer, self._system = VtkViewer(), system
        self._simulation = Simulation(self, system)
        self._drawings = []
        self._lock = RLock()


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
        viewer._redraw()



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
        with self._lock:
            drawings = self._drawings
            # Clear drawings
            drawings.clear()
            # Remove all vtk actors in the viewer
            viewer.remove_all_actors()
            # Redraw
            viewer._redraw()



    def add_drawing(self, drawing):
        '''add_drawing(drawing: Drawing3D)
        Add a new drawing object to the scene
        '''
        viewer = self._viewer

        with self._lock:
            drawings = self._drawings

            # Add the drawing to the list of drawings
            drawings.append(drawing)

            # Add drawing actor to the viewer
            viewer.add_actor(drawing.get_actor())
            for child in drawing.get_children():
                viewer.add_actor(child.get_actor())

            # Update drawing
            drawing._update()

            # Redraw
            viewer._redraw()




    def draw_point(self, *args, **kwargs):
        # Create point drawing
        # Add point to drawing to the scene
        # TODO
        pass



    def _update(self):
        '''
        Updates the scene
        '''
        viewer = self._viewer
        with self._lock:
            drawings = self._drawings

            # Update drawings
            for drawing in drawings:
                drawing._update()

            # Redraw scene
            viewer._redraw()
