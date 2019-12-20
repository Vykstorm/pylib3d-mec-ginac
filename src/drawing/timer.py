'''
Author: Víctor Ruiz Gómez.
Description: This file defines the classes Timer and OneShotTimer
'''


######## Import statements ########

from threading import Thread, Condition
from time import sleep, time, process_time
from collections.abc import Iterable, Mapping



######## class Timer ########

class Timer(Thread):
    '''
    Instances of this class can be used to trigger an arbitrary callback repeatedly
    over time
    '''

    def __init__(self, callback, interval=1, one_shot=False, args=(), kwargs={}):
        '''
        Create a new timer object that will invoke the given callback repeatedly.

        :param callback: Is the callback that should be executed by this timer periodically
        :param interval: The callback will be executed on each time interval (in seconds)
        :param one_shot: If True, the timer will invoke the callback only once. After that,
            it will be automatically destroyed.
        :param args: Additional positional arguments to be passed to the callback
        :param kwargs: Additional keyword arguments to be passed to the callback

        '''
        # Validate & parse input arguments
        if not callable(callback):
            raise TypeError('callback must be callable')

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



        # Initialize super instance and set the thread as daemon
        super().__init__()
        self.daemon = True

        # Initialize internal fields
        self._callback, self._interval = callback, interval
        self._one_shot = one_shot
        self._args, self._kwargs = args, kwargs
        self._state = 'inactive'
        self._lock = Condition()


    def run(self):
        callback, interval = self._callback, self._interval
        args, kwargs = self._args, self._kwargs
        cv = self._lock
        last_exec_time = 0


        while True:
            with cv:
                while True:
                    # Wait until the timer is not paused
                    while self._state == 'paused':
                        cv.wait()
                    # If the timer was killed, finish the execution
                    if self._state == 'death':
                        return
                    # Go to sleep before the next callback execution
                    cv.wait(timeout=max(self._interval-last_exec_time, 0))
                    if self._state == 'running':
                        # Break this loop if the timer is running
                        break

            # Trigger the callback
            t = process_time()
            callback(*args, **kwargs)
            last_exec_time = process_time() - t

            if self._one_shot:
                # Only trigger the callback once
                return



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
        with self._lock:
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
        with self._lock:
            return self._state in ('running', 'paused')



    def is_alive(self):
        '''is_alive() -> bool
        Returns True if this timer is not death (not started, running or paused).
        False otherwise.

        :rtype: bool

        '''
        with self._lock:
            return self._state != 'death'



    def is_death(self):
        '''is_death() -> bool
        Returns True if this timer is death. False otherwise.

        :rtype: bool

        '''
        with self._lock:
            return self._state == 'death'



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


    def start(self, resumed=True):
        '''start(resumed: bool)
        Start this timer.

        :param resumed: If True, the timer will be running after this method execution.
            Otherwise, it will be paused. By default is True

        '''
        with self._lock:
            if self._state != 'inactive':
                raise RuntimeError('Timer already started')
            self._state = 'running' if resumed else 'paused'
        super().start()



    def resume(self):
        '''resume()
        Resume this timer.

        :raises RuntimeError: If the timer was not paused

        '''
        with self._lock:
            if self._state != 'paused':
                raise RuntimeError('Timer is not paused')
            self._state = 'running'
            self._lock.notify()



    def pause(self):
        '''resume()
        Pause this timer.

        :raises RuntimeError: If the timer was not running

        '''
        with self._lock:
            if self._state != 'running':
                raise RuntimeError('Timer is not running')
            self._state = 'paused'
            self._lock.notify()



    def kill(self):
        '''kill()
        Kill this timer.

        :raises RuntimeError: If the timer was not running nor paused

        '''
        with self._lock:
            if self._state == 'inactive':
                raise RuntimeError('Timer was not started yet')
            self._state = 'death'
            self._lock.notify()
        #self.join()




    def set_time_interval(self, interval):
        '''set_time_interval(interval: numeric)
        Changes the time interval

        :param interval: Time interval (in seconds)

        '''
        try:
            interval = float(interval)
            if interval <= 0:
                raise TypeError
            with self._lock:
                self._interval = interval
        except TypeError:
            raise TypeError('interval must be a float or int value greater than zero')





######## class OneShotTimer ########

class OneShotTimer(Timer):
    '''
    Instances of this class can be used to trigger a callback after an specific
    amount of time elapsed.
    '''
    def __init__(self, callback, interval=1, *args, **kwargs):
        super().__init__(callback, interval, True, *args, **kwargs)





if __name__ == '__main__':
    bar = 0
    def foo():
        global bar
        bar += 1
        print(bar)

    timer = Timer(foo, interval=1)
    timer.start()
    sleep(2)
    timer.pause()
    sleep(2)
    timer.resume()
    sleep(2)
    timer.set_time_interval(0.5)
    sleep(2)
    timer.pause()
    sleep(1)
    timer.kill()

    def foo():
        print("Hello world")

    timer = OneShotTimer(foo, interval=2)
    timer.start()
    timer.join()
