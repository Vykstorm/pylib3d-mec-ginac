'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Simulation
'''

######## Import statements ########

# Standard imports
from time import time_ns
from collections import deque
from collections.abc import Mapping, Iterable
from functools import partial

# Imports from other modules
from ..utils.events import EventProducer
from .timer import Timer
from ..config import runtime_config
from ..core.integration import NumericIntegration
from ..core.assembly import AssemblyProblemSolver
from lib3d_mec_ginac_ext import Matrix, NumericFunction



######## class Simulation ########

class Simulation(EventProducer):
    '''
    This class is responsible of storing & update the simulation state (change the
    time symbol value periodically and perform temporal integration).
    Also it updates the scene (which recomputes the drawings affine transformations and
    redraws the vtk scene)
    '''

    ######## Constructor ########

    def __init__(self, scene, system):
        super().__init__()

        # Initialize internal fields
        self._scene, self._system = scene, system
        self._delta_t = 1 / 30
        self._timer = None
        self._elapsed_time, self._last_update_time = 0.0, None
        self._looped, self._time_limit = False, None
        self._diff_times = deque(maxlen=10)
        self._assembly_problem_init = lambda *args, **kwargs: None
        self._assembly_problem_step = lambda *args, **kwargs: None
        self.set_integration_method('euler')

        self._timer = Timer()
        self.add_event_handler(self._on_timer_tick, 'tick')
        self.add_child(self._timer)



    ######## Simulation controls ########

    def start(self, delta_t=None, time_limit=None, looped=None):
        if delta_t is not None:
            self.set_delta_time(delta_t)
        if time_limit is not None:
            self.set_time_limit(time_limit)
        if looped is not None:
            self.set_looped(looped)

        if not self.is_stopped():
            raise RuntimeError('Simulation already started')

        self._timer.set_time_interval(self._delta_t)
        self._timer.start(resumed=True)

        self._system.save_state()
        self._assembly_problem_init()
        self._system.get_time().value = 0

        self.fire_event('simulation_started')



    def resume(self):
        if not self.is_paused():
            raise RuntimeError('Simulation is not paused')

        self._last_update_time = None
        self._timer.resume()
        self.fire_event('simulation_resumed')



    def pause(self):
        if not self.is_running():
            raise RuntimeError('Simulation is not running')

        self._timer.pause()
        self.fire_event('simulation_paused')



    def stop(self):
        if self.is_stopped():
            raise RuntimeError('Simulation has not started yet')

        self._elapsed_time = 0.0
        self._last_update_time = None
        self._system.restore_previous_state()

        self._timer.stop()
        self.fire_event('simulation_stopped')




    ######## Getters ########

    def is_running(self):
        return self._timer.is_running()


    def is_paused(self):
        return self._timer.is_paused()


    def is_stopped(self):
        return self._timer.is_stopped()


    def get_elapsed_time(self):
        return self._elapsed_time


    def get_update_frequency(self):
        return 1 / self._delta_t


    def get_real_update_frequency(self):
        if not self._diff_times:
            return 0
        try:
            return len(self._diff_times) / sum(self._diff_times)
        except ZeroDivisionError:
            return 0


    def get_delta_time(self):
        return self._delta_t


    def is_looped(self):
        return self._looped


    def get_time_limit(self):
        return self._time_limit


    def get_integration_method(self):
        '''get_integrator() -> Callable
        Get the current integration method to adjust system's symbol values while
        the simulation is running
        '''
        return self._integration_method


    def get_integration_method_name(self):
        '''get_integration_method_name() -> str
        Get the current integration method`s name to adjust system's symbol values
        while the simulation is running
        '''
        method = self.get_integration_method()
        if isinstance(method, partial):
            return method.func.__name__
        return method.__name__




    ######## Setters ########


    def set_looped(self, looped=True):
        '''set_looped(looped: bool)
        If the argument is set to True, repeat the simulation indefinitely (only if time duration
        is set). By default is set to True
        If set to False, stop the simulation automatically when reaching the time limit (if any, otherwise
        it runs indefinitely)
        '''
        if not isinstance(looped, bool):
            raise Type('Input argument must be bool')

        self._looped = looped
        self.fire_event('looped_mode_changed')



    def set_time_limit(self, limit):
        '''set_time_limit(limit: numeric | None)
        Set the simulation time limit
        '''
        if limit is not None:
            try:
                limit = float(limit)
                if limit <= 0:
                    raise TypeError
            except:
                raise TypeError('Input argument must be a number greater than zero or None')

        self._time_limit = limit
        self.fire_event('time_limit_changed')



    def set_delta_time(self, delta_t):
        '''set_delta_time(delta_t: numeric | None)
        Change the simulation integration time (Amount of time to integrate with on each
        simulation step). If a number is specified, it will
        have a fixed numeric value. If set to None ( by default ) it is updated on each
        simulation step ( calculated as the time elapsed between two simulaton updates )
        '''
        if delta_t is not None:
            try:
                delta_t = float(delta_t)
                if delta_t <= 0:
                    raise TypeError
            except:
                raise TypeError('Input argument must be a number greater than zero or None')

        self._delta_t = delta_t
        self._timer.set_time_interval(delta_t)
        self.fire_event('delta_time_changed')



    def set_integration_method(self, method):
        '''set_integrator(method: IntegrationMethod)
        Change integration method to adjust system's symbol values while the
        simulation is running
        :param method: Must be a callable for a custom integration method or
            the name of a predefined integrator like 'euler', 'rk4'
        '''
        if not isinstance(method, str) and not callable(method):
            raise TypeError('Integration method must be a callable or a string')

        if isinstance(method, str):
            method = NumericIntegration.get_method(method)

        system = self._system
        q_values   = system.get_coords_values()
        dq_values  = system.get_velocities_values()
        ddq_values = system.get_accelerations_values()

        self._integration_method = partial(method, q_values, dq_values, ddq_values)
        self.fire_event('integration_method_changed')



    def assembly_problem(self, *args, **kwargs):
        '''assembly_problem(...)
        Setup assembly problem constraints and parameters

        You must pass first the next constraints as positional arguments:
        Phi, Phi_q, beta, Phi_init, Phi_init_q, beta_init, dPhi_dq, dPhi_init_dq

        and then you can specify additional parameters (this is optional):
        geom_eq_tol, geom_eq_relax, geom_eq_init_tol, geom_eq_init_relax
        '''
        solver = AssemblyProblemSolver(self._system, *args, **kwargs)
        system = self._system
        q_values   = system.get_coords_values()
        dq_values  = system.get_velocities_values()
        ddq_values = system.get_accelerations_values()
        self._assembly_problem_init = partial(solver.init, q_values, dq_values, ddq_values)
        self._assembly_problem_step = partial(solver.step, q_values, dq_values, ddq_values)



    ######## Event handlers ########

    def _on_timer_tick(self, *args, **kwargs):
        self._update()
        return True



    def _update(self, delta_t=None):
        if delta_t is None:
            # Compute real delta time
            current_time = time_ns()
            if self._last_update_time is None:
                delta_t = 0
                self._last_update_time = current_time
            else:
                delta_t = (current_time - self._last_update_time) / 1e9
                self._last_update_time = current_time
        self._diff_times.appendleft(delta_t)

        # Update elapsed time
        self._elapsed_time += delta_t

        # Update time
        t = self._system.get_time()
        t.value += delta_t

        if self._delta_t is not None:
            # Use the user delta_t to perform the numerical integration and solve
            # the assembly problem
            delta_t = self._delta_t

        self._integration_method(delta_t)
        self._assembly_problem_step(delta_t)
        self.fire_event('simulation_step')

        t_limit = self._time_limit
        if t_limit is not None and t.value >= t_limit:
            if self._looped:
                delta_t = t.value - t_limit
                t.value -= t_limit
                self._system.restore_previous_state()
                self._assembly_problem_init()
                self._integration_method(delta_t)
                self.fire_event('simulation_step')
            else:
                self.stop()
