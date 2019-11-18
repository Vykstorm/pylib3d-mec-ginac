

from .timer import Timer
from time import time
from threading import RLock



class Simulation:
    '''
    This class is responsible of storing & update the simulation state (change the
    time symbol value periodically and integrate).
    Also it updates the scene (which recomputes the drawings affine transformations and
    redraws the vtk scene)
    '''

    def __init__(self, scene, system):

        # Initialize internal fields
        self._scene, self._system = scene, system
        self._state = 'stopped'
        self._time_multiplier = 1.0
        self._update_freq = 30
        self._timer = None
        self._elapsed_time, self._last_update_time = 0.0, None
        self._lock = RLock()


    def start(self):
        with self._lock:
            if self._state != 'stopped':
                raise RuntimeError('Simulation already started')
            self._state = 'running'
            self._timer = Timer(self._update, interval=1 / self._update_freq)
            self._timer.start(resumed=True)


    def resume(self):
        with self._lock:
            if self._state != 'paused':
                raise RuntimeError('Simulation is not paused')
            self._state = 'running'


    def pause(self):
        with self._lock:
            if self._state != 'running':
                raise RuntimeError('Simulation is not running')
            self._state = 'paused'


    def stop(self):
        with self._lock:
            if self._state == 'stopped':
                raise RuntimeError('Simulation has not started yet')
            self._state = 'stopped'
            self._timer.kill()
            self._timer = None
            self._elapsed_time = 0.0
            self._last_update_time = None
            self._update()


    def is_running(self):
        with self._lock:
            return self._state == 'running'


    def is_paused(self):
        with self._lock:
            return self._state == 'paused'


    def is_stopped(self):
        with self._lock:
            return self._state == 'stopped'


    def get_elapsed_time(self):
        with self._lock:
            return self._elapsed_time


    def get_time_multiplier(self):
        with self._lock:
            return self._time_multiplier


    def set_time_multiplier(self, multiplier):
        try:
            multiplier = float(multiplier)
            if multiplier <= 0:
                raise TypeError
        except TypeError:
            raise TypeError('Input argument must be a number greater than zero')
        with self._lock:
            self._time_multiplier = multiplier


    def get_update_frequency(self):
        with self._lock:
            return self._update_freq


    def set_update_frequency(self, frequency):
        try:
            frequency = float(frequency)
            if frequency <= 0:
                raise TypeError
        except TypeError:
            raise TypeError('Input argument must be a number greater than zero')
        with self._lock:
            self._update_freq = frequency
            if self._state != 'stopped':
                self._timer.set_time_interval(1 / self._update_freq)


    def _update(self):
        with self._lock:
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

        # Update scene (update drawings & redraw)
        self._scene._update()
