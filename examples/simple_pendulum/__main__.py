
######## Imports ########

#from lib3d_mec_ginac import *
from src import *
import warnings


######## Configuration ########

set_gravity_direction('up')
set_atomization_state(False)
warnings.filterwarnings('ignore')



######## Geometric parameters ########

l = new_param('l', 2)              # Longitude of the pendulum
alpha0 = new_param('alpha0', 0.05) # Initial value must be << 1 radian
A = new_param('a', pi/3)           # Amplitude of the oscilation

# Gravity & time
g, t = get_param('g'), get_time()


######## Coordinates ########

alpha, dalpha, ddalpha = new_coord('alpha')


######## Geometry ########

Bbob = new_base('Bbob', 0, 0, 1, alpha)     # Base of the bob
v = new_vector('v', 0, -l, 0, Bbob)         # Vector from the origin to the bob
Bob = new_point('Bob', 'O', v)              # Position of the bob
FBob = new_frame('FBob', Bob, Bbob)         # Frame of the bob


######## Symbol matrices ########

q,   q_aux   = get_coords_matrix(),        get_aux_coords_matrix()
dq,  dq_aux  = get_velocities_matrix(),    get_aux_velocities_matrix()
ddq, ddq_aux = get_accelerations_matrix(), get_aux_accelerations_matrix()



######## Kinematic equations ########

# Phi
Phi = Matrix([
    # Simple armonic equation
    alpha - A * cos(sqrt(g / l) * t)
]).transpose()
dPhi = derivative(Phi)
ddPhi = derivative(dPhi)

# Phi_init
Phi_init = Matrix([
    alpha - alpha0,
    dalpha
]).transpose()
dPhi_init = derivative(Phi_init)


# Phi_q
Phi_q = jacobian(Phi.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_dq = jacobian(dPhi.transpose(), Matrix.block(2, 1, dq, dq_aux))

# Beta
beta = -dPhi
beta = subs(beta, dq, 0)
beta = subs(beta, dq_aux, 0)

# Phi_init_q
Phi_init_q = jacobian(Phi_init.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_init_dq = jacobian(dPhi_init.transpose(), Matrix.block(2, 1, dq, dq_aux))

# beta_init
beta_init = -dPhi_init
beta_init = subs(beta_init, dq, 0)
beta_init = subs(beta_init, ddq_aux, 0)



######## Drawings ########

draw_point('O')
draw_point(Bob, scale=2, color='gray')
draw_position_vector('O', Bob)
draw_frame(FBob)




######## Simulation & Viewer ########

# Setup integration method
set_integration_method('euler')

# Configure assembly problem constraints
assembly_problem(Phi, Phi_q, beta, Phi_init, Phi_init_q, beta_init, dPhi_dq, dPhi_init_dq)

# Choose what should be drawn in the simulation
toogle_drawings(points=True, vectors=True, frames=False, grid=False)

# Start simulation
start_simulation(delta_t=0.05)

open_viewer(gui=True)
