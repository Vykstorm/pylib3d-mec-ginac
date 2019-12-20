'''
Author: Víctor Ruiz Gómez
Description: This script defines the class IntegrationMethod and its subclasses
'''


######## Import statements ########

from numpy.linalg import norm, pinv




######## class IntegrationMethod ########

class IntegrationMethod:
    '''
    This is the base class for all integration methods. They are used to met certain
    equation constraints in a system by adjusting the values of the symbols.

    .. seealso:: :class:``KinematicEulerIntegrator``

    '''
    ######## Constructor ########

    def __init__(self):
        self._funcs_cache = {}
        self._system = None


    ######## Operations ########

    def init(self):
        '''init()
        This method will be called to initialize the values of the symbols. This is invoked normally
        when the system simulation begins.
        '''
        pass

    def step(self, delta_t):
        '''step(delta_t: float)
        This is called to update the values of the symbols so that the equation constraints
            are still met. This usually happen at each time step.
        '''
        pass




    def _set_system(self, system):
        self._system = system
        self._funcs_cache.clear()




    ######## Helper methods ########

    def evaluate(self, matrix):
        if id(matrix) not in self._funcs_cache:
            self._funcs_cache[id(matrix)] = self._system.get_numeric_function(matrix)
        func = self._funcs_cache[id(matrix)]
        return func.evaluate()




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
    def __init__(self,
        Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init,
        Phi, Phi_q, dPhi_dq, beta,
        geom_eq_init_tol=1e-10,
        geom_eq_init_relax=.1,
        geom_eq_tol = 0.05 * 10**-3,
        geom_eq_relax = .1
        ):
        super().__init__()
        self.Phi_init = Phi_init
        self.Phi_init_q = Phi_init_q
        self.dPhi_init = dPhi_init
        self.dPhi_init_dq = dPhi_init_dq
        self.beta_init = beta_init
        self.Phi = Phi
        self.Phi_q = Phi_q
        self.dPhi_dq = dPhi_dq
        self.beta = beta
        self.geom_eq_init_tol = geom_eq_init_tol
        self.geom_eq_init_relax = geom_eq_init_relax
        self.geom_eq_tol = geom_eq_tol
        self.geom_eq_relax = geom_eq_relax



    def init(self):
        q_values, dq_values, ddq_values = self.q_values, self.dq_values, self.ddq_values
        Phi_init, Phi_init_q, dPhi_init_dq, beta_init = self.Phi_init, self.Phi_init_q, self.dPhi_init_dq, self.beta_init
        geom_eq_init_tol, geom_eq_init_relax = self.geom_eq_init_tol, self.geom_eq_init_relax

        evaluate = self.evaluate

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




    def step(self, delta_t=.05):
        q_values, dq_values, ddq_values = self.q_values, self.dq_values, self.ddq_values
        Phi, Phi_q, dPhi_dq, beta = self.Phi, self.Phi_q, self.dPhi_dq, self.beta
        geom_eq_tol, geom_eq_relax = self.geom_eq_tol, self.geom_eq_relax
        evaluate = self.evaluate

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
