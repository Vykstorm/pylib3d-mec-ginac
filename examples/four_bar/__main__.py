

######## Imports ########
from lib3d_mec_ginac import *



######## Generalized coordinates, velocities and accelerations ########

theta1, dtheta1, ddtheta1 = new_coord('theta1', -pi/6, 0)
theta2, dtheta2, ddtheta2 = new_coord('theta2', -2*pi/6, 0)
theta3, dtheta3, ddtheta3 = new_coord('theta3', -3*pi/6, 0)


######## Kinematical parameters ########

l1, l2 = new_param('l1', 0.4), new_param('l2', 2.0)
l3, l4 = new_param('l3', 1.2), new_param('l4', 1.6)


######## Bases ########

new_base('Barm1', 'xyz', [0, 1, 0], theta1)
new_base('Barm2', 'Barm1', 0, 1, 0, theta2)
new_base('Barm3', 'Barm2', rotation_tupla=[0, 1, 0], rotation_angle=theta3)


######## Vectors ########

new_vector('OA', l1, 0, 0, 'Barm1')
new_vector('AB', l2, 0, 0, 'Barm2')
new_vector('BC', [l3, 0, 0], 'Barm3')
new_vector('OO2', values=[l4, 0, 0], base='xyz')


######## Points ########

new_point('A',  'O', 'OA')
new_point('B',  'A', 'AB')
new_point('C',  'B', 'BC')
new_point('O2', 'O', 'OO2')


######## Frames ########

new_frame('FArm1',    'O',  'Barm1')
new_frame('FArm2',    'A',  'Barm2')
new_frame('FArm3',    'B',  'Barm3')
new_frame('Fra_ABS2', 'O2', 'xyz')


######## Matrices of symbols ########

q,   q_aux   = get_coords_matrix(),        get_aux_coords_matrix()
dq,  dq_aux  = get_velocities_matrix(),    get_aux_velocities_matrix()
ddq, ddq_aux = get_accelerations_matrix(), get_aux_accelerations_matrix()


######## Kinematic equations ########

O2C = position_vector('O2', 'C')
e_x = new_vector('e_x', 1, 0, 0, 'xyz')
e_z = new_vector('e_z', 0, 0, 1, 'xyz')

# Phi
Phi = Matrix(shape=[2, 1])
Phi[0] = O2C * e_x
Phi[1] = O2C * e_z
dPhi = derivative(Phi)
ddPhi = derivative(dPhi)

# Phi_q
Phi_q = jacobian(Phi.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_dq = jacobian(dPhi.transpose(), Matrix.block(2, 1, dq, dq_aux))

# Beta
beta = -dPhi
beta = subs(beta, dq, 0)
beta = subs(beta, dq_aux, 0)

# Phi_init
Phi_init = Matrix.block(2, 1, Phi, Matrix([theta1 + pi / 2]))
dPhi_init = Matrix.block(2, 1, dPhi, Matrix([dtheta1 + pi / 2]))

# Phi_init_q
Phi_init_q = jacobian(Phi_init.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_init_dq = jacobian(dPhi_init.transpose(), Matrix.block(2, 1, dq, dq_aux))

# beta_init
beta_init = -dPhi_init
beta_init = subs(beta_init, dq, 0)
beta_init = subs(beta_init, ddq_aux, 0)



######## Drawings ########

# Draw the pivot points
draw_point('O', color='cyan')
draw_point('A', color='red')
draw_point('B', color='green')
draw_point('C', color='blue')

# Draw the vectors connecting the pivots
draw_position_vector('O', 'A')
draw_position_vector('A', 'B')
draw_position_vector('B', 'C')
draw_position_vector('C', 'O')

# Change camera position & focal point
camera = get_camera()
camera.position = 0.8, 4, 0.5
camera.focal_point = 0.8, 0, -0.2




######## Simulation ########


# Start simulation
start_kinematic_euler_simulation(Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init, Phi, Phi_q, dPhi_dq, beta)
