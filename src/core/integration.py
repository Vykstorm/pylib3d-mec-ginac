'''
Author: Víctor Ruiz Gómez
Description: This script defines the class IntegrationMethod and its subclasses
'''


######## Import statements ########

from numpy.linalg import norm, pinv
from functools import partial
from lib3d_mec_ginac_ext import evaluate



######## class IntegrationMethod ########

class IntegrationMethod:
    '''
    This is the base class for all integration methods. They are used to met certain
    equation constraints in a system by adjusting the values of the symbols.

    .. seealso:: :class:``KinematicEulerIntegrator``

    '''
    ######## Constructor ########

    def __init__(self, system, constraints={}, parameters={}):
        self._system = system
        self._constraints, self._parameters = constraints, parameters
        args = [
            system.get_coords_values(), system.get_velocities_values(), system.get_accelerations_values(),
            system.get_params_values(), constraints, parameters
        ]
        self.init, self.step = partial(self.init, *args), partial(self.step, *args)


    ######## Operations ########

    def init(self, q_values, dq_values, ddq_values, p_values, constraints, parameters):
        '''init()
        This method will be called to initialize the values of the symbols. This is invoked normally
        when the system simulation begins.
        '''
        pass

    def step(self, q_values, dq_values, ddq_values, p_values, constraints, parameters, delta_t):
        '''step(delta_t: float)
        This is called to update the values of the symbols so that the equation constraints
            are still met. This usually happen at each time step.
        '''
        pass




    ######## Properties ########

    @property
    def q_values(self):
        return self._system.get_coords_values()

    @property
    def dq_values(self):
        return self._system.get_velocities_values()

    @property
    def ddq_values(self):
        return self._system.get_accelerations_values()

    @property
    def p_values(self):
        return self._system.get_params_values()

    @property
    def time(self):
        return self._system.get_time().get_value()

    t = time






######## class KinematicEulerIntegrationMethod ########

class KinematicEulerIntegrationMethod(IntegrationMethod):
    '''
    This class implements the euler improved integration.
    * It has the next equation constraints which must be supplied in the constructor:
        Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init, Phi, Phi_q_ dPhi_dq, beta
    * It also has the next parameters:
        geom_eq_init_tol, geom_eq_init_relax, geom_eq_tol, geom_eq_relax
    '''

    def init(self, q_values, dq_values, ddq_values, p_values, constraints, parameters):
        Phi_init, Phi_init_q, dPhi_init_dq, beta_init = map(constraints.__getitem__, ('Phi_init', 'Phi_init_q', 'dPhi_init_dq', 'beta_init'))
        geom_eq_init_tol, geom_eq_init_relax = map(parameters.__getitem__, ('geom_eq_init_tol', 'geom_eq_init_relax'))


        # Assembly problem (Coordinate level)
        Phi_init_num = evaluate(Phi_init)
        q_values -= geom_eq_init_relax * pinv( evaluate(Phi_init_q) ) @ Phi_init_num
        Phi_init_num = evaluate(Phi_init)

        # Assembly problem (Velocity level)
        while norm(Phi_init_num) > geom_eq_init_tol:
            q_values -= geom_eq_init_relax * (pinv( evaluate(Phi_init_q) ) @ Phi_init_num)
            Phi_init_num = evaluate(Phi_init)

        dPhi_init_dq_num = evaluate(dPhi_init_dq)
        dq_values += pinv(dPhi_init_dq_num) @ (evaluate(beta_init) - dPhi_init_dq_num @ dq_values)




    def step(self, q_values, dq_values, ddq_values, p_values, constraints, parameters, delta_t):
        Phi, Phi_q, dPhi_dq, beta = map(constraints.__getitem__, ('Phi', 'Phi_q', 'dPhi_dq', 'beta'))
        geom_eq_tol, geom_eq_relax = map(parameters.__getitem__, ('geom_eq_tol', 'geom_eq_relax'))

        # Euler improved integration
        q_values += delta_t * (dq_values + 0.5 * delta_t * ddq_values)
        dq_values += delta_t * ddq_values

        # Assembly problem (Coordinate level)
        Phi_num = evaluate(Phi)
        q_values -= geom_eq_relax * pinv( evaluate(Phi_q) ) @ Phi_num
        Phi_num = evaluate(Phi)
        while norm(Phi_num) > geom_eq_tol:
            q_values -= geom_eq_relax *  pinv( evaluate(Phi_q) ) @ Phi_num
            Phi_num = evaluate(Phi)

        # Assembly problem (velocity level)
        dPhi_dq_num = evaluate(dPhi_dq)
        dq_values += pinv(dPhi_dq_num) @ (evaluate(beta) - dPhi_dq_num @ dq_values)
