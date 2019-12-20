'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Simulation
'''

######## Import statements ########

# Standard imports
from time import process_time
from collections import deque
from collections.abc import Mapping, Iterable

# Imports from other modules
from .events import EventProducer
from .timer import Timer
from ..config import runtime_config
from ..core.integration import IntegrationMethod, KinematicEulerIntegrationMethod
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
        self._state = 'stopped'
        self._update_freq = runtime_config.SIMULATION_UPDATE_FREQUENCY
        self._time_multiplier = runtime_config.SIMULATION_TIME_MULTIPLIER
        self._timer = None
        self._elapsed_time, self._last_update_time = 0.0, None
        self._diff_times = deque(maxlen=10)
        self._integration_method = IntegrationMethod(system)



    ######## Simulation controls ########

    def start(self):
        with self:
            if self._state != 'stopped':
                raise RuntimeError('Simulation already started')
            self._state = 'running'
            self._timer = Timer(self._update, interval=1 / self._update_freq)
            self._timer.start(resumed=True)
            self.get_integration_method().init()
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




    ######## Getters ########

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


    def get_update_frequency(self):
        with self:
            return self._update_freq


    def get_time_multiplier(self):
        with self:
            return self._time_multiplier


    def get_real_update_frequency(self):
        with self:
            if not self._diff_times:
                return 0
            return len(self._diff_times) / sum(self._diff_times)


    def get_integration_method(self):
        '''get_integrator() -> IntegrationMethod
        Get the current integration method to adjust system's symbol values while
        the simulation is running
        '''
        return self._integration_method




    ######## Setters ########


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




    def set_integration_method(self, method, constraints, parameters):
        '''set_integrator(method: IntegrationMethod)
        Change integration method to adjust system's symbol values while the
        simulation is running
        '''
        if not issubclass(method, IntegrationMethod) and not isinstance(method, str):
            raise TypeError('Integration method must be a subclass of IntegrationMethod or a string')

        if isinstance(method, str):
            methods = {
                'kinematic_euler': KinematicEulerIntegrationMethod
            }
            if method not in methods:
                raise ValueError(f'Invalid integration method name ("{method}")')
            method = methods[method]


        system = self._system

        try:
            if not isinstance(constraints, Mapping):
                raise Exception
            for name, value in constraints.items():
                if not isinstance(name, str) or not isinstance(value, (Matrix, NumericFunction)):
                    raise Exception
            constraints = dict(zip(
                constraints.keys(),
                [value if isinstance(value, NumericFunction) else system.get_numeric_function(value) for value in constraints.values()]
            ))
        except Exception as e:
            raise TypeError('constraints must be a mapping like object where keys are constraint names and values are Matrix or NumericFunction instances')

        with self:
            self._integration_method = method(system, constraints, parameters)
            self.fire_event('integration_method_changed')



    def set_kinematic_euler_integration(self,
        Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init, Phi, Phi_q, dPhi_dq, beta,
        geom_eq_init_tol=1e-10, geom_eq_init_relax=.1,
        geom_eq_tol=.05 * 10**-3, geom_eq_relax=.1):
        '''start_kinematic_euler_simulation()
        This method will start a simulation on this system adjusting the values of
        symbols over time to met the equation constraints defined by the input matrices:
        Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init, Phi, Phi_q dPhi_dq, beta
        '''
        self.set_integration_method(KinematicEulerIntegrationMethod,
            constraints={
                'Phi_init': Phi_init,
                'Phi_init_q': Phi_init_q,
                'dPhi_init': dPhi_init,
                'dPhi_init_dq': dPhi_init_dq,
                'beta_init': beta_init,
                'Phi': Phi,
                'Phi_q': Phi_q,
                'dPhi_dq': dPhi_dq,
                'beta': beta
            },
            parameters={
                'geom_eq_init_tol': geom_eq_init_tol,
                'geom_eq_init_relax': geom_eq_init_relax,
                'geom_eq_tol': geom_eq_tol,
                'geom_eq_relax': geom_eq_relax
            })



    def _update(self):
        with self:
            if self._state == 'running':
                # Update elapsed time
                current_time = process_time()
                if self._last_update_time is None:
                    delta_t = 0
                    self._last_update_time = current_time
                else:
                    delta_t = current_time - self._last_update_time
                    self._elapsed_time += delta_t
                    self._diff_times.appendleft(delta_t)
                    self._last_update_time = current_time


            # Update time variable
            delta_t *= self._time_multiplier
            system = self._system
            system.get_time().value += delta_t

            if self._state == 'running':
                self.get_integration_method().step(delta_t)
                self.fire_event('simulation_step')
