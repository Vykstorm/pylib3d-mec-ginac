'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Scene
'''


######## Imports ########

from .drawing import Drawing3D
from .point import PointDrawing
from .frame import FrameDrawing
from lib3d_mec_ginac_ext import Point, Frame

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
        Helper class responsible of updating the viewer periodically running
        on a secondary thread
        '''
        def __init__(self, viewer):
            super().__init__()
            self._viewer = viewer
            self._close = Event()
            self.daemon = True


        def run(self):
            update_delay = 1 / min(30, self._viewer.get_simulation_update_frequency())
            while True:
                if self._close.is_set():
                    break

                # Update viewer each update_interval time interval
                self._viewer._update()
                sleep(.5 * update_delay)





    ######## Constructor ########


    def __init__(self, system):

        # Create the vtk renderer
        renderer = vtkRenderer()


        ## Initialize internal fields
        self._renderer = renderer
        self._drawings = [] # list of drawing objects
        self._system = system # system attached to this scene
        self._elapsed_time = 0.0 # elapsed time since the simulation begun
        # timestamp of the last call to _update and last time when drawing objects were updated
        self._last_time, self._last_update_time = None, None
        # update frequency of drawing objects
        self._update_freq = 30
        # Viewer.Updater instance to update the viewer periodically on a secondary thread
        self._updater = None

        self._simulation_state = 'inactive' # current simulation state
        self._time_multiplier = 1.0 # time multiplier factor

        # threading lock to modify scene properties and drawing objects attached to it
        # safely from multiple threads
        self._lock = RLock()




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

        rtype: float

        '''
        with self._lock:
            return self._time_multiplier





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




    def draw_point(self, point, **kwargs):
        '''draw_point(...)
        Draw the given point

        '''
        # Validate & parse point argument
        if not isinstance(point, (Point, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(point, str):
            point = self._system.get_point(point)

        # Get symbolic position & rotation matrices for the drawing
        OC = self._system.position_vector('O', point)
        base = OC.get_base()
        position = self._system.rotation_matrix('xyz', base) * OC
        rotation = self._system.rotation_matrix('xyz', base).transpose()

        drawing = PointDrawing(self, position, rotation, **kwargs)
        self._add_drawing(drawing)
        return drawing



    def draw_frame(self, frame, **kwargs):
        '''draw_frame(...)
        Draw the given frame
        '''
        # Validate & parse frame argument
        if not isinstance(frame, (Frame, str)):
            raise TypeError('Input argument must be a Frame or str instance')
        if isinstance(frame, str):
            frame = self._system.get_frame(frame)

        # Get symbolic position & rotation matrices for the drawing
        OC = self._system.position_vector('O', frame.get_point())
        base = OC.get_base()
        position = self._system.rotation_matrix('xyz', base) * OC
        rotation = self._system.rotation_matrix('xyz', base).transpose()

        drawing = FrameDrawing(self, position, rotation, **kwargs)
        self._add_drawing(drawing)
        return drawing






    ######## Updating ########


    def _update(self):
        '''
        Update this scene.
        '''
        self._lock.acquire()
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

        # Redraw scene
        self._interactor.Render()

        self._lock.release()




    def _update_drawings(self):
        '''
        Update all drawings
        '''
        for drawing in self._drawings:
            drawing._update()



    def _update_simulation(self):
        '''
        Update scene simulation
        '''
        # Update time symbol numeric value
        self._system.get_time().set_value(self._elapsed_time)









    ######## Simulation controls  ########


    def start_simulation(self):
        '''show_drawings()
        Start the simulation (also open the window where drawing objects should be
        rendered)
        '''
        system, renderer = self._system, self._renderer
        with self._lock:
            if self._simulation_state != 'inactive':
                raise RuntimeError('Simulation already started')


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


            # Initialize simulation state and variables
            self._simulation_state = 'running'
            self._start_time = time()
            self._last_update_time = None
            self._elapsed_time = 0.0
            self._system.get_time().set_value(0)


            # Start interactor
            interactor.Start()

            # Update view periodically
            self._update()
            self._updater = Viewer.Updater(self)
            self._updater.start()





    def stop_simulation(self):
        '''stop_simulation()
        Stop the simulation (also close the window where drawings are rendered)

        .. seealso:: :func:`start_simulation`

        '''
        with self._lock:
            if self._simulation_state == 'inactive':
                raise RuntimeError('Simulation was not started yet')

            updater = self._updater
            updater._close.set()
            updater.join()
            self._updater = None

            self._window.Finalize()
            self._interactor.TerminateApp()
            del self._interactor, self._window

            self._simulation_state = 'inactive'




    def pause_simulation(self):
        '''
        Calling this method causes the simulation to be paused

        .. seealso:: :func:`resume_simulation`

        '''
        with self._lock:
            if self._simulation_state != 'running':
                raise RuntimeError('Simulation is not running')

            self._simulation_state = 'paused'



    def resume_simulation(self):
        '''
        Calling this method causes the simulation to be resumed

        .. seealso:: :func:`pause_simulation`

        '''
        with self._lock:
            if self._simulation_state != 'paused':
                raise RuntimeError('Simulation is not paused')

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
