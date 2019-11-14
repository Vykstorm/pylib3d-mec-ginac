'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Scene
'''


######## Imports ########

from .drawing import Drawing3D
from .point import PointDrawing
from .frame import FrameDrawing
from .solid import SolidDrawing
from lib3d_mec_ginac_ext import Point, Frame, Solid

# vtk imports
from vtk import vtkRenderer, vtkRenderWindow, vtkNamedColors, vtkCommand
from vtk import vtkGenericRenderWindowInteractor

# utilities
from math import ceil
from time import time, sleep
from os.path import basename
import sys
from re import match

# multithreading
from threading import RLock, Thread, Event






######## class Scene ########


class Viewer:
    '''
    An instance of this class represents a 3D renderable scene.
    '''

    class Updater(Thread):
        '''
        Helper class to implement timers internally.
        '''
        def __init__(self, viewer):
            super().__init__()
            self._viewer = viewer
            self._close = Event()
            self.daemon = True


        def get_update_frequency(self):
            viewer = self._viewer
            if viewer.is_simulation_running():
                return viewer.get_simulation_update_frequency()
            return 30

        def update(self):
            self._viewer._update()

        def close(self):
            self._close.set()
            self.join()

        def run(self):
            update_delay = 1 / self.get_update_frequency()
            while True:
                self.update()
                if self._close.wait(update_delay):
                    break







    ######## Constructor ########


    def __init__(self, system):

        # Create the vtk renderer
        renderer = vtkRenderer()

        renderer.GetActiveCamera().SetPosition(5, 5, 5)
        renderer.SetBackground(1, 1, 1)


        ## Initialize internal fields
        self._renderer, self._interactor, self._window = renderer, None, None
        self._drawings = [] # list of drawing objects
        self._system = system # system attached to this scene
        self._elapsed_time = 0.0 # elapsed time since the simulation begun
        # timestamp of the last call to _update and last time when drawing objects were updated
        self._last_time, self._last_update_time = None, None
        # update frequency of drawing objects
        self._update_freq = 30

        self._simulation_state = 'inactive' # current simulation state
        self._time_multiplier = 1.0 # time multiplier factor

        # threading lock to modify scene properties and drawing objects attached to it
        # safely from multiple threads
        self._lock = RLock()

        # Viewer.Updater instance to update the viewer periodically on a secondary thread
        self._updater = None



    ######## Getters ########


    def get_simulation_update_frequency(self):
        '''get_simulation_update_frequency() -> float
        Get the desired update frequency in updates per second

        :rtype: float

        '''
        with self._lock:
            return self._update_freq


    get_simulation_update_freq = get_simulation_update_frequency


    def get_simulaton_time_multiplier(self):
        '''get_simulaton_time_multiplier() -> float
        Get the current time multiplier

        :rtype: float

        '''
        with self._lock:
            return self._time_multiplier



    def is_simulation_running(self):
        '''is_simulation_running() -> bool
        Returns True if the simulation is running, False otherwise

        :rtype: bool

        '''
        with self._lock:
            return self._simulation_state == 'running'


    def is_simulation_paused(self):
        '''is_simulation_paused() -> bool
        Returns True if the simulation is paused, False otherwise

        :rtype: bool

        '''
        with self._lock:
            return self._simulation_state == 'paused'


    def is_simulation_stopped(self):
        '''is_simulation_stopped() -> bool
        Returns True if the simulation is inactive (stopped), False otherwise

        :rtype: bool

        '''
        with self._lock:
            return self._simulation_state == 'inactive'


    def are_drawings_shown(self):
        '''are_drawings_shown() -> bool
        Returns True if the drawings are being rendered

        :rtype: bool

        '''
        with self._lock:
            return self._interactor is not None


    def get_simulation_elapsed_time(self):
        '''get_simulation_elapsed_time() -> float
        Returns the total number of seconds that the simulation was running.

        :rtype: float

        '''
        with self._lock:
            if self._simulation_state == 'inactive':
                raise RuntimeError('Simulation has not started yet')
            return self._elapsed_time





    ######## Setters ########


    def set_simulation_update_frequency(self, freq):
        '''set_simulation_update_frequency(freq: numeric)
        Set the desired scene update frequency in updates per second (Default is 30)

        :type freq: numeric

        .. note:: The real update frequency will be lower or equal than the desired update
            frequency.

        '''
        if not isinstance(freq, (int, float)):
            raise TypeError('Input argument must be int or float')
        freq = float(freq)
        if freq <= 0:
            raise ValueError('update frequency must be a number greater than zero')

        with self._lock:
            self._update_freq = freq



    set_simulation_update_freq = set_simulation_update_frequency



    def set_simulation_time_multiplier(self, multiplier):
        '''set_simulation_time_multiplier(multiplier: numeric)
        Set the time multiplier for the simulation

        :type multiplier: numeric

        '''
        if not isinstance(multiplier, (int, float)):
            raise TypeError('Input argument must be int or float')
        multiplier = float(multiplier)
        if multiplier <= 0:
            raise ValueError('time multiplier must be a number greater than zero')
        with self._lock:
            self._time_multiplier = multiplier






    ######## Creation routines ########


    def _add_drawing(self, drawing):
        assert isinstance(drawing, Drawing3D)
        with self._lock:
            self._drawings.append(drawing)
            self._renderer.AddActor(drawing._vtk_handler)


    def _fv_draw(self, point, cls, **kwargs):
        # Get symbolic position & rotation matrices for the drawing
        OC = self._system.position_vector('O', point)
        base = OC.get_base()
        position = self._system.rotation_matrix('xyz', base) * OC
        rotation = self._system.rotation_matrix('xyz', base).transpose()
        drawing = cls(self, position, rotation, **kwargs)
        self._add_drawing(drawing)
        return drawing


    def draw_point(self, point, **kwargs):
        '''draw_point(...)
        Draw the given point

        '''
        # Validate & parse point argument
        if not isinstance(point, (Point, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(point, str):
            point = self._system.get_point(point)

        return self._fv_draw(point, PointDrawing, **kwargs)



    def draw_frame(self, frame, **kwargs):
        '''draw_frame(...)
        Draw the given frame
        '''
        # Validate & parse frame argument
        if not isinstance(frame, (Frame, str)):
            raise TypeError('Input argument must be a Frame or str instance')
        if isinstance(frame, str):
            frame = self._system.get_frame(frame)

        return self._fv_draw(frame.get_point(), FrameDrawing, **kwargs)



    def draw_solid(self, solid, **kwargs):
        '''draw_solid(...)
        Draw the given solid
        '''
        # Validate & parse solid argument
        if not isinstance(solid, (Solid, str)):
            raise TypeError('Input argument must be a Solid or str instance')
        if isinstance(solid, str):
            solid = self._system.get_solid(solid)

        return self._fv_draw(solid.get_point(), SolidDrawing, **kwargs)






    ######## Updating ########


    def _update(self):
        '''
        Update this scene.
        '''
        with self._lock:
            if self._simulation_state == 'running':
                current_time = time()

                # Compute elapsed time since the simulation begun
                if self._last_time is None:
                    self._last_time = current_time

                self._elapsed_time += (current_time - self._last_time) * self._time_multiplier
                self._last_time = current_time

                # Make sure to update the scene with the desired update frequency
                update_delay = 1 / self._update_freq
                if self._last_update_time is None or (current_time - self._last_update_time) >= update_delay:
                    self._last_update_time = current_time
                    # Update simulation state
                    self._update_simulation()

                    # Update drawings
                    self._update_drawings()

            if self._interactor is not None:
                # Redraw scene
                self._interactor.Render()





    def _update_drawings(self):
        '''
        Update all drawings
        '''
        with self._lock:
            for drawing in self._drawings:
                drawing._update()



    def _update_simulation(self):
        '''
        Update scene simulation
        '''
        with self._lock:
            # Update time symbol numeric value
            self._system.get_time().set_value(self._elapsed_time)






    ######## Show/hide scene  ########


    def show_drawings(self):
        '''show_drawings()
        Show the drawing objects
        '''
        system, renderer = self._system, self._renderer
        with self._lock:
            if self._interactor is not None:
                raise RuntimeError('Drawings are being shown already')


            # Create the interactor and the window
            window = vtkRenderWindow()
            interactor = vtkGenericRenderWindowInteractor()
            self._window, self._interactor = window, interactor

            # Set window title
            result = match('(.*)\.py$', sys.argv[0])
            title = result.group(1) if result else sys.argv[0]
            window.SetWindowName(title)

            # Added renderer to the window
            window.AddRenderer(renderer)

            # Set default window size
            window.SetSize(640, 480)

            # Set render window to the interactor
            interactor.SetRenderWindow(window)

            # Enable user interface interactor
            interactor.Initialize()

            # Add a callback which is executed when the user press the 'x' button
            # on the window
            ## TODO

            # Start interactor
            interactor.Start()

            # Update drawings
            self._update_drawings()






    def hide_drawings(self):
        '''hide_drawings()
        Remove the window showing the drawing objects
        '''
        with self._lock:
            if self._interactor is None:
                raise RuntimeError('Drawings are not being shown yet')

            self._window.Finalize()
            self._interactor.TerminateApp()
            self._interactor, self._window = None, None






    ######## Simulation controls  ########


    def start_simulation(self):
        '''show_drawings()
        Start the simulation (also open the window where drawing objects should be
        rendered)
        '''
        with self._lock:
            if self._simulation_state != 'inactive':
                raise RuntimeError('Simulation already started')

            # Initialize simulation state and variables
            self._simulation_state = 'running'
            self._start_time = time()
            self._last_update_time = None
            self._elapsed_time = 0.0
            self._system.get_time().set_value(0)

            # update viewer periodically
            self._updater = Viewer.Updater(self)
            self._updater.start()




    def stop_simulation(self):
        '''stop_simulation()
        Stop the simulation (also close the window where drawings are rendered)

        .. seealso:: :func:`start_simulation`

        '''
        with self._lock:
            if self._simulation_state == 'inactive':
                raise RuntimeError('Simulation has not started yet')

            self._simulation_state = 'inactive'
            self._updater.close()
            self._updater = None





    def pause_simulation(self):
        '''
        Calling this method causes the simulation to be paused

        .. seealso:: :func:`resume_simulation`

        '''
        with self._lock:
            if self._simulation_state != 'running':
                raise RuntimeError('Simulation is not running yet')

            self._simulation_state = 'paused'




    def resume_simulation(self):
        '''
        Calling this method causes the simulation to be resumed

        .. seealso:: :func:`pause_simulation`

        '''
        with self._lock:
            if self._simulation_state != 'paused':
                if self._simulation_state == 'inactive':
                    raise RuntimeError('Simulation has not started yet')
                raise RuntimeError('Simulation is running already')

            self._simulation_state = 'running'
            self._last_time = self._last_update_time = None






    ######## Properties ########


    @property
    def simulation_update_frequency(self):
        '''
        Property that can be used to get/set the desired scene update frequency

        .. seealso::
            :func:`set_simulation_update_frequency`
            :func:`get_simulation_update_frequency`

        '''
        return self.get_simulation_update_frequency()


    @simulation_update_frequency.setter
    def simulation_update_frequency(self, freq):
        self.set_simulation_update_frequency(freq)


    simulation_update_freq = simulation_update_frequency


    @property
    def simulation_time_multiplier(self):
        '''
        Property that can be used to get/set the time multiplier

        .. seealso::
            :func:`set_simulation_time_multiplier`
            :func:`get_simulation_time_multiplier`

        '''
        return self.get_simulation_time_multiplier()


    @simulation_time_multiplier.setter
    def simulation_time_multiplier(self, multiplier):
        self.set_simulation_time_multiplier(multiplier)
