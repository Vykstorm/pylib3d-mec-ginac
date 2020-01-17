

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



######## Dynamical parameters ########

m1, m2, m3 = new_param('m1', 1), new_param('m2', 1), new_param('m3', 1)


cg1x, cg1z = new_param('cg1x', 0.2), new_param('cg1z', 0.1)
cg2x, cg2z = new_param('cg2x', 1),   new_param('cg2z', 0.1)
cg3x, cg3z = new_param('cg3x', 0.6), new_param('cg3z', 0.1)


new_vector('OArm1_GArm1', cg1x, 0, cg1z, 'Barm1')
new_vector('OArm2_GArm2', cg2x, 0, cg2z, 'Barm2')
new_vector('OArm3_GArm3', cg3x, 0, cg3z, 'Barm3')


I1yy, I2yy, I3yy = [new_param(name, 1) for name in ('I1yy', 'I2yy', 'I3yy')]

I_Arm1 = new_tensor('Iarm1', base='Barm1')
I_Arm2 = new_tensor('Iarm2', base='Barm2')
I_Arm3 = new_tensor('Iarm3', base='Barm3')
I_Arm1[1, 1], I_Arm2[1, 1], I_Arm3[1, 1] = I1yy, I2yy, I3yy


######## Frames ########

new_frame('FArm1',    'O',  'Barm1')
new_frame('FArm2',    'A',  'Barm2')
new_frame('FArm3',    'B',  'Barm3')
new_frame('Fra_ABS2', 'O2', 'xyz')



######## Solids ########

new_solid('Arm1', 'O', 'Barm1', 'm1', 'OArm1_GArm1', 'Iarm1')
new_solid('Arm2', 'A', 'Barm2', 'm2', 'OArm2_GArm2', 'Iarm2')
new_solid('Arm3', 'B', 'Barm3', 'm3', 'OArm3_GArm3', 'Iarm3')



######## Joint unknowns ########

new_unknown('lambda1')
new_unknown('lambda2')



######## Inputs ########

Fx2, Fz2 = new_input('Fx2'), new_input('Fz2')
Fx3, Fz3 = new_input('Fx3'), new_input('Fz3')
My2, My3 = new_input('My2'), new_input('My3')

new_vector('Fext2', Fx2, 0,   Fz2, 'xyz')
new_vector('Fext3', Fx3, 0,   Fz3, 'xyz')
new_vector('Mext2', 0,   My2, 0,   'xyz')
new_vector('Mext3', 0,   My3, 0,   'xyz')



######## Force and momentum ########

K   = new_param('k',     50)
l2x = new_param('l2x',    1)
l3x = new_param('l3x',  0.5)
l3z = new_param('l3z',  0.1)

new_vector('OArm2_L2',  l2x, 0, 0,   'Barm2')
new_vector('OArm3_L3',  l3x, 0, l3z, 'Barm3')

new_point('OL2', 'A', 'OArm2_L2')
new_point('OL3', 'B', 'OArm3_L3')

OL2_OL3 = position_vector('OL2', 'OL3')
FK = K * OL2_OL3
MK = new_vector('MK_GroundPend1', 0, 0, 0, 'xyz')


######## Wrenches ########

# Gravity
Gravity_Arm1 = gravity_wrench('Arm1')
Gravity_Arm2 = gravity_wrench('Arm2')
Gravity_Arm3 = gravity_wrench('Arm3')

# Inertia
Inertia_Arm1 = inertia_wrench('Arm1')
Inertia_Arm2 = inertia_wrench('Arm2')
Inertia_Arm3 = inertia_wrench('Arm3')

# Constitutive
SpringA = new_wrench('SpringA', FK,   MK, 'OL2', 'Arm2', 'Constitutive')
SpringR = new_wrench('SpringR', -FK, -MK, 'OL3', 'Arm3', 'Constitutive')

# External
FMext2 = new_wrench('FMext2', 'Fext2', 'Mext2', 'A', 'Arm2', 'External')
FMext3 = new_wrench('FMext3', 'Fext3', 'Mext3', 'B', 'Arm3', 'External')

# Wrenches sums
Sum_Wrenches_Arm1 = Inertia_Arm1 + Gravity_Arm1
Sum_Wrenches_Arm2 = Inertia_Arm2 + Gravity_Arm2 + SpringA - FMext2
Sum_Wrenches_Arm3 = Inertia_Arm3 + Gravity_Arm3 - SpringA + FMext3


# Twists
Twist_Arm1, Twist_Arm2, Twist_Arm3 = twist('Arm1'), twist('Arm2'), twist('Arm3')



######## Matrices of symbols ########

q,   q_aux   = get_coords_matrix(),        get_aux_coords_matrix()
dq,  dq_aux  = get_velocities_matrix(),    get_aux_velocities_matrix()
ddq, ddq_aux = get_accelerations_matrix(), get_aux_accelerations_matrix()
epsilon      = get_unknowns_matrix()
param        = get_params_matrix()
input        = get_inputs_matrix()


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

# Beta
beta = -dPhi
beta = subs(beta, dq, 0)
beta = subs(beta, dq_aux, 0)

# Phi_q
Phi_q = jacobian(Phi.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_dq = jacobian(dPhi.transpose(), Matrix.block(2, 1, dq, dq_aux))


# Gamma
gamma = -ddPhi
gamma = subs(gamma, ddq, 0)
gamma = subs(gamma, ddq_aux, 0)


# Phi_init
Phi_init = Matrix([theta1 + pi / 2])
dPhi_init = Matrix([dtheta1 + pi / 2])



######## Dynamic equations ########

Dyn_eq_VP = Matrix(shape=[3, 1], values=[
    Sum_Wrenches_Arm1*diff(Twist_Arm1, dtheta1) + Sum_Wrenches_Arm2*diff(Twist_Arm2,dtheta1) + Sum_Wrenches_Arm3*diff(Twist_Arm3,dtheta1),
    Sum_Wrenches_Arm1*diff(Twist_Arm1, dtheta2) + Sum_Wrenches_Arm2*diff(Twist_Arm2,dtheta2) + Sum_Wrenches_Arm3*diff(Twist_Arm3,dtheta2),
    Sum_Wrenches_Arm1*diff(Twist_Arm1, dtheta3) + Sum_Wrenches_Arm2*diff(Twist_Arm2,dtheta3) + Sum_Wrenches_Arm3*diff(Twist_Arm3,dtheta3)
])


######## Output vector ########


Output = new_matrix('Output', shape=[1, 1])



######## Energy equations ########


Energy = new_matrix('Energy', shape=[1, 1])

Dyn_eq_VP_open = Dyn_eq_VP
Dyn_eq_VP_open = subs(Dyn_eq_VP_open, epsilon, 0)


Dyn_eq_L = Dyn_eq_VP
M_qq = jacobian(Dyn_eq_VP_open.transpose(), ddq, True)

delta_q = -Dyn_eq_VP_open
delta_q = subs(delta_q, ddq, 0)
delta_q = subs(delta_q, ddq_aux, 0)

Phi_init = Matrix.block(2, 1, Phi, Phi_init)
dPhi_init = Matrix.block(2, 1, dPhi, dPhi_init)


Phi_init_q = jacobian(Phi_init.transpose(), Matrix.block(2, 1, q, q_aux))
dPhi_init_dq = jacobian(dPhi_init.transpose(), Matrix.block(2, 1, dq, dq_aux))

beta_init = -dPhi_init
beta_init = subs(beta_init, dq, 0)
beta_init = subs(beta_init, ddq_aux, 0)

Extra_Dyn_Eq_eq = Matrix([dtheta1, ddtheta1]).transpose()
Dyn_Eq_eq_VP = Matrix.block(5, 1, Dyn_eq_L, ddPhi, dPhi, Phi, Extra_Dyn_Eq_eq)



######## Drawings ########

draw_point('O', color='cyan')
draw_point('A', color='red')
draw_point('B', color='green')
draw_point('C', color='blue')
draw_position_vector('O', 'A')
draw_position_vector('A', 'B')
draw_position_vector('B', 'C')
draw_position_vector('C', 'O')


camera = get_camera()
camera.position = 0.8, 4, 0.5
camera.focal_point = 0.8, 0, -0.2


start_kinematic_euler_simulation(Phi_init, Phi_init_q, dPhi_init, dPhi_init_dq, beta_init, Phi, Phi_q, dPhi_dq, beta)
