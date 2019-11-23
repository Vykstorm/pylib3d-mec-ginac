

from .object import Object
from .timer import Timer
from time import time
from ..config import runtime_config



class Simulation(Object):
    '''
    This class is responsible of storing & update the simulation state (change the
    time symbol value periodically and integrate).
    Also it updates the scene (which recomputes the drawings affine transformations and
    redraws the vtk scene)
    '''

    def __init__(self, scene, system):
        super().__init__()

        # Initialize internal fields
        self._scene, self._system = scene, system
        self._state = 'stopped'
        self._time_multiplier = runtime_config.SIMULATION_TIME_MULTIPLIER
        self._update_freq = runtime_config.SIMULATION_UPDATE_FREQUENCY
        self._timer = None
        self._elapsed_time, self._last_update_time = 0.0, None



    def start(self):
        with self:
            if self._state != 'stopped':
                raise RuntimeError('Simulation already started')
            self._state = 'running'
            self._timer = Timer(self._update, interval=1 / self._update_freq)
            self._timer.start(resumed=True)

            self.fire_event('simulation_started')



    def resume(self):
        with self:
            if self._state != 'paused':
                raise RuntimeError('Simulation is not paused')
            self._state = 'running'

            self.fire_event('simulation_resumed')



    def pause(self):
        with self:
            if self._state != 'running':
                raise RuntimeError('Simulation is not running')
            self._state = 'paused'

            self.fire_event('simulation_paused')



    def stop(self):
        with self:
            if self._state == 'stopped':
                raise RuntimeError('Simulation has not started yet')
            self._state = 'stopped'
            self._timer.kill()
            self._timer = None
            self._elapsed_time = 0.0
            self._last_update_time = None
            self._update()

            self.fire_event('simulation_stopped')



    def is_running(self):
        with self:
            return self._state == 'running'


    def is_paused(self):
        with self:
            return self._state == 'paused'


    def is_stopped(self):
        with self:
            return self._state == 'stopped'


    def get_elapsed_time(self):
        with self:
            return self._elapsed_time


    def get_time_multiplier(self):
        with self:
            return self._time_multiplier


    def set_time_multiplier(self, multiplier):
        try:
            multiplier = float(multiplier)
            if multiplier <= 0:
                raise TypeError
        except TypeError:
            raise TypeError('Input argument must be a number greater than zero')
        with self:
            self._time_multiplier = multiplier

            self.fire_event('time_multiplier_changed')



    def get_update_frequency(self):
        with self:
            return self._update_freq


    def set_update_frequency(self, frequency):
        try:
            frequency = float(frequency)
            if frequency <= 0:
                raise TypeError
        except TypeError:
            raise TypeError('Input argument must be a number greater than zero')
        with self:
            self._update_freq = frequency
            if self._state != 'stopped':
                self._timer.set_time_interval(1 / self._update_freq)

            self.fire_event('update_frequency_changed')



    def _update(self):
        with self:
            if self._state == 'running':
                # Update elapsed time
                current_time = time()
                if self._last_update_time is None:
                    self._last_update_time = current_time
                else:
                    self._elapsed_time += current_time - self._last_update_time
                    self._last_update_time = current_time


            # Update time variable
            elapsed_time = self._elapsed_time * self._time_multiplier
            system = self._system
            t = system.get_time()
            t.set_value(elapsed_time)

            # Intergrate
            # TODO

            if self._state == 'running':
                self.fire_event('simulation_step')
