'''
Author: Víctor Ruiz Gómez.
Description: This file defines the classes Timer and OneShotTimer
'''


######## Import statements ########

from time import time
from .events import EventProducer
from collections.abc import Iterable, Mapping



######## class Timer ########

class Timer(EventProducer):
    '''
    Instances of this class can be used to create objects that generate ticks
    periodically over time.
    '''

    ######## Constructor ########

    def __init__(self, interval=1, one_shot=False, args=(), kwargs={}):
        '''
        Create a new timer object that will invoke the given callback repeatedly.

        :param interval: This object will generate a 'tick' event on each time interval (in seconds)
        :param one_shot: If True, the timer will invoke the callback only once. After that,
            it will be automatically destroyed.
        :param args: Additional positional arguments to be passed when the 'tick' event is raised
        :param kwargs: Additional keyword arguments to be passed when the 'tick' event is raised

        '''
        # Validate & parse input arguments
        try:
            interval = float(interval)
            if interval <= 0:
                raise TypeError
        except TypeError:
            raise TypeError('interval must be a float or int value greater than zero')

        if not isinstance(one_shot, bool):
            raise TypeError('one_shot must be a bool value')

        if not isinstance(args, Iterable):
            raise TypeError('args must be an iterable object')
        args = tuple(args)

        if not isinstance(kwargs, Mapping):
            raise TypeError('kwargs must be a mapping object')
        kwargs = dict(kwargs)



        # Initialize super instance
        super().__init__()

        # Initialize internal fields
        self._interval, self._one_shot = interval, one_shot
        self._args, self._kwargs = args, kwargs
        self._state = 'stopped'
        self._elapsed_time, self._last_time = 0.0, None




    ######## Getters ########


    def get_callback(self):
        '''get_callback() -> Callable
        Get the callback that will be triggered by this timer repeatedly.

        :rtype: Callable

        '''
        return self._callback



    def get_time_interval(self):
        '''get_time_interval() -> float
        Get the time interval in seconds

        :rtype: float

        '''
        return self._interval



    def is_one_shot(self):
        '''is_one_shot() -> bool
        Returns True if this timer is one shot. False otherwise.

        :rtype: bool

        '''
        return self._one_shot



    def is_active(self):
        '''is_active() -> bool
        Returns True if this timer is running or paused. False otherwise.

        :rtype: bool

        '''
        return not self.is_stopped()



    def is_stopped(self):
        '''is_stopped() -> bool
        Returns True if this time is stopped. False Otherwise

        :rtype: bool

        '''
        return self._state == 'stopped'



    def is_running(self):
        '''is_running() -> bool
        Returns True if this timer is running. False otherwise.

        :rtype: bool

        '''
        with self._lock:
            return self._state == 'running'



    def is_paused(self):
        '''is_paused() -> bool
        Returns True if this timer is paused. False otherwise.

        :rtype: bool

        '''
        with self._lock:
            return self._state == 'paused'




    ######## Setters ########


    def set_time_interval(self, interval):
        '''set_time_interval(interval: numeric)
        Changes the time interval

        :param interval: Time interval (in seconds)

        '''
        try:
            interval = float(interval)
            if interval <= 0:
                raise TypeError
            self._interval = interval
        except TypeError:
            raise TypeError('interval must be a float or int value greater than zero')






    ######## Controls ########


    def start(self, resumed=True):
        '''start(resumed: bool)
        Start this timer.

        :param resumed: If True, the timer will be running after this method execution.
            Otherwise, it will be paused. By default is True

        '''
        if self._state != 'stopped':
            raise RuntimeError('Timer already started')

        self._state = 'running' if resumed else 'paused'



    def resume(self):
        '''resume()
        Resume this timer.

        :raises RuntimeError: If the timer was not paused

        '''
        if self._state != 'paused':
            raise RuntimeError('Timer is not paused')
        self._state = 'running'
        self._last_time = None



    def pause(self):
        '''resume()
        Pause this timer.

        :raises RuntimeError: If the timer was not running

        '''
        if self._state != 'running':
            raise RuntimeError('Timer is not running')
        self._state = 'paused'


    def stop(self):
        '''stop()
        Stop this timer.

        :raises RuntimeError: If the timer was not active (running or paused)
        '''
        if self._state == 'stopped':
            raise RuntimeError('Timer is already stopped')
        self._state = 'stopped'
        self._last_time, self._elapsed_time = None, 0.0



    def _update(self):
        # This is called internally to update the state of the timer
        if self._state != 'running':
            return
        current_time = time()
        if self._last_time is None:
            self._last_time = current_time
        else:
            diff_time = current_time - self._last_time
            interval = self._interval
            self._last_time = current_time
            self._elapsed_time += diff_time
            while self._elapsed_time >= interval:
                self._elapsed_time -= interval
                self.fire_event('tick', *self._args, **self._kwargs)
                if self._one_shot:
                    self.stop()
                    break






######## class OneShotTimer ########

class OneShotTimer(Timer):
    '''
    Instances of this class can be used to trigger a callback after an specific
    amount of time elapsed.
    '''
    def __init__(self, interval=1, *args, **kwargs):
        super().__init__(interval, True, *args, **kwargs)




def main():
    from time import sleep

    timer = OneShotTimer(args=(1, 2, 3), kwargs={'a':4})
    timer.add_event_handler(lambda *args, **kwargs: print(args, kwargs))
    timer.start()

    timer._update()
    sleep(0.5)
    timer._update()
    timer.pause()
    sleep(0.6)
    timer.resume()
    timer._update()
    sleep(0.6)
    timer._update()
