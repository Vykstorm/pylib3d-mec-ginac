'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Scene
'''


######## Imports ########


from vtk import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor, vtkNamedColors
from .drawing import Drawing3D
from .point import PointDrawing
from lib3d_mec_ginac_ext import Point
from threading import Thread
from math import ceil
from time import time
from os.path import basename
import sys
from re import match




######## class Scene ########


class Scene:
    '''
    An instance of this class represents a 3D renderable scene.
    '''

    class Viewer(Thread):
        def __init__(self, scene):
            super().__init__()
            # Set thread as daemon
            self.daemon = True

            # Initialize internal fields
            self._scene = scene


        def run(self):
            scene = self._scene
            interactor, window = scene._interactor, scene._window

            # Start rendering the scene and show the window
            window.Render()
            scene.update()
            interactor.Start()




    ######## Constructor ########


    def __init__(self, system):
        # Create the vtk renderer, window & interactor objects
        renderer = vtkRenderer()
        window = vtkRenderWindow()
        interactor = vtkRenderWindowInteractor()

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

        # Initialize internal fields
        self._renderer, self._window, self._interactor = renderer, window, interactor
        self._drawings = []
        self._system = system
        self._elapsed_time = 0.0
        self._last_time, self._last_update_time = None, None
        self._update_freq = 30
        self._update_timer = None
        self._viewer = None
        self._simulation_state = 'inactive'
        self._time_multiplier = 1.0





    ######## Getters ########


    def get_update_frequency(self):
        '''get_update_frequency() -> float
        Get the desired update frequency in updates per second

        :rtype: float

        '''
        return self._update_freq


    get_update_freq = get_update_frequency


    def get_time_multiplier(self):
        '''get_time_multiplier() -> float
        Get the current time multiplier

        rtype: float

        '''
        return self._time_multiplier






    ######## Setters ########


    def _create_update_timer(self):
        assert self._viewer is not None
        if self._update_timer is not None:
            self._interactor.DestroyTimer(self._update_timer)
        self._update_timer = self._interactor.CreateRepeatingTimer(min(30, ceil(1000 / self._update_freq)))



    def set_update_frequency(self, freq):
        '''set_update_frequency(freq: numeric)
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

        self._update_freq = float(freq)
        if self._viewer is not None:
            self._create_update_timer()


    set_update_freq = set_update_frequency



    def set_time_multiplier(self, multiplier):
        '''set_time_multiplier(multiplier: numeric)
        Set the time multiplier for the simulation

        :type multiplier: numeric

        '''
        if not isinstance(multiplier, (int, float)):
            raise TypeError('Input argument must be int or float')
        multiplier = float(multiplier)
        if multiplier <= 0:
            raise ValueError('time multiplier must be a number greater than zero')
        self._time_multiplier = multiplier






    ######## Creation routines ########


    def _add_drawing(self, drawing):
        assert isinstance(drawing, Drawing3D)
        self._drawings.append(drawing)
        self._renderer.AddActor(drawing._vtk_handler)




    def draw_point(self, point, *args, **kwargs):
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





    ######## Updating ########


    def update(self):
        '''
        Update this scene.
        '''
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
                self.update_simulation()

                # Update drawings
                self.update_drawings()

        # Redraw scene
        self._interactor.Render()




    def update_drawings(self):
        '''
        Update all drawings
        '''
        for drawing in self._drawings:
            drawing.update()



    def update_simulation(self):
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
        interactor, system = self._interactor, self._system

        # Create scene viewer
        viewer = Scene.Viewer(self)
        self._viewer = viewer

        # Enable user interface interactor
        interactor.Initialize()

        # Create a timer to update scene objects periodically
        self._create_update_timer()

        # Register a callback to update the scene on each time interval
        interactor.AddObserver('TimerEvent', lambda *args: self.update())

        # Initialize simulation
        self._simulation_state = 'running'
        self._start_time = time()
        self._elapsed_time = 0.0
        self._system.get_time().set_value(0)

        # Run the viewer
        viewer.start()
        #viewer.join()



    def stop_simulation(self):
        '''stop_simulation()
        Stop the simulation (also close the window where drawings are rendered)

        .. seealso:: :func:`start_simulation`

        '''
        self._simulation_state = 'inactive'
        self._interactor.TerminateApp()
        self._viewer = None




    def pause_simulation(self):
        '''
        Calling this method causes the simulation to be paused

        .. seealso:: :func:`resume_simulation`

        '''
        self._simulation_state = 'paused'



    def resume_simulation(self):
        '''
        Calling this method causes the simulation to be resumed

        .. seealso:: :func:`pause_simulation`

        '''
        self._simulation_state = 'running'
        self._last_time = self._last_update_time = None






    ######## Properties ########


    @property
    def update_frequency(self):
        '''
        Property that can be used to get/set the desired scene update frequency

        .. seealso::
            :func:`set_update_frequency`
            :func:`get_update_frequency`

        '''
        return self.get_update_frequency()


    @update_frequency.setter
    def update_frequency(self, freq):
        self.set_update_frequency(freq)


    update_freq = update_frequency


    @property
    def time_multiplier(self):
        '''
        Property that can be used to get/set the time multiplier

        .. seealso::
            :func:`set_time_multiplier`
            :func:`get_time_multiplier`

        '''
        return self.get_time_multiplier()


    @time_multiplier.setter
    def time_multiplier(self, multiplier):
        self.set_time_multiplier(multiplier)
