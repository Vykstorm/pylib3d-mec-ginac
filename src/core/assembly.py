'''
Author: Víctor Ruiz Gómez
Description: This script defines the class AssemblyProblemSolver
'''

######## Import statements ########

from numpy.linalg import norm, pinv



######## class AssemblyProblemSolver ########

class AssemblyProblemSolver:
    '''
    This class can be used to solve the "assembly problem" in order to adjust
    numeric values of the coordinates ( and its derivatives ) used to define a
    mechanical system.
    The method `init` solves the assembly problem initialization ( coordinate & velocity levels )
    On the other hand `step` solves the assembly problem step ( coordinate & velocity leveles)
    The second one is invoked after the numerical integration phase when performing a simulation.
    '''
    def __init__(self, system,
        Phi,        Phi_q,      beta,
        Phi_init,   Phi_init_q, beta_init,
        dPhi_dq, dPhi_init_dq,
        geom_eq_tol=.05 * 10**-3, geom_eq_relax=.1,
        geom_eq_init_tol=1e-10, geom_eq_init_relax=.1):
        '''
        Constructor.
        You must pass the symbolic matrices Phi, Phi_q, beta, Phi_init, Phi_init_q,
        beta_init, dPhi_dq and dPhi_init_dq either as positional or keyword arguments.

        geom_eq_tol and geom_eq_relax represents the geometric tolerance and relaxation parameters
        for the assembly problem solver.
        The same applies for geom_eq_init_tol and geom_eq_init_relax, but these are used on
        the initialization phase.
        '''
        self._system = system
        self.Phi, self.Phi_q, self.beta = Phi, Phi_q, beta
        self.Phi_init, self.Phi_init_q, self.beta_init = Phi_init, Phi_init_q, beta_init
        self.dPhi_dq, self.dPhi_init_dq = dPhi_dq, dPhi_init_dq
        self.geom_eq_tol, self.geom_eq_relax = geom_eq_tol, geom_eq_relax
        self.geom_eq_init_tol, self.geom_eq_init_relax = geom_eq_init_tol, geom_eq_init_relax



    def init(self, q_values, dq_values, ddq_values):
        '''
        This solves the assembly problem initialization ( coordinate & velocity levels )
        :param q_values: Numpy array representing the coordinate`s numeric values
        :param dq_values: Numpy array representing the velocities numeric values
        :param ddq_values: Numpy array representing the accelerations numeric values
        '''
        evaluate = self._system.evaluate
        Phi_init, Phi_init_q = self.Phi_init, self.Phi_init_q
        dPhi_init_dq, beta_init = self.dPhi_init_dq, self.beta_init
        geom_eq_init_tol, geom_eq_init_relax = self.geom_eq_init_tol, self.geom_eq_init_relax

        # Coordinate level
        Phi_init_num = evaluate(Phi_init)
        q_values -= geom_eq_init_relax * pinv( evaluate(Phi_init_q) ) @ Phi_init_num
        Phi_init_num = evaluate(Phi_init)

        while norm(Phi_init_num) > geom_eq_init_tol:
            q_values -= geom_eq_init_relax * (pinv( evaluate(Phi_init_q) ) @ Phi_init_num)
            Phi_init_num = evaluate(Phi_init)

        # Velocity level
        dPhi_init_dq_num = evaluate(dPhi_init_dq)
        dq_values += pinv(dPhi_init_dq_num) @ (evaluate(beta_init) - dPhi_init_dq_num @ dq_values)



    def step(self, q_values, dq_values, ddq_values, delta_t):
        '''
        This solves the assembly problem ( coordinate & velocity levels )
        :param q_values: Numpy array representing the coordinate`s numeric values
        :param dq_values: Numpy array representing the velocities numeric values
        :param ddq_values: Numpy array representing the accelerations numeric values
        :param float delta_t: This is the delta time used for this step
        '''
        evaluate = self._system.evaluate
        Phi, Phi_q = self.Phi, self.Phi_q
        dPhi_dq, beta = self.dPhi_dq, self.beta
        geom_eq_tol, geom_eq_relax = self.geom_eq_tol, self.geom_eq_relax

        # Coordinate level
        Phi_num = evaluate(Phi)
        q_values -= geom_eq_relax * pinv( evaluate(Phi_q) ) @ Phi_num
        Phi_num = evaluate(Phi)
        while norm(Phi_num) > geom_eq_tol:
            q_values -= geom_eq_relax *  pinv( evaluate(Phi_q) ) @ Phi_num
            Phi_num = evaluate(Phi)

        # Velocity level
        dPhi_dq_num = evaluate(dPhi_dq)
        dq_values += pinv(dPhi_dq_num) @ (evaluate(beta) - dPhi_dq_num @ dq_values)
