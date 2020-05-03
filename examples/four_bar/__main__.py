

######## Imports ########
#from lib3d_mec_ginac import *
from src import *

######## Generalized coordinates, velocities and accelerations ########

theta1, dtheta1, ddtheta1 = new_coord('theta1', -pi/6, 0)
theta2, dtheta2, ddtheta2 = new_coord('theta2', -2*pi/6, 0)
theta3, dtheta3, ddtheta3 = new_coord('theta3', -3*pi/6, 0)


######## Kinematical parameters ########

l1, l2 = new_param('l1', 0.4), new_param('l2', 2.0)
l3, l4 = new_param('l3', 1.2), new_param('l4', 1.6)


######## Dynamical parameters ########

m1, m2, m3 = new_param('m1', 1), new_param('m2', 1), new_param('m3', 1)



######## Bases ########

new_base('BArm1', 'xyz', [0, 1, 0], theta1)
new_base('BArm2', 'BArm1', 0, 1, 0, theta2)
new_base('BArm3', 'BArm2', rotation_tupla=[0, 1, 0], rotation_angle=theta3)


######## Vectors ########

new_vector('OA', l1, 0, 0, 'BArm1')
new_vector('AB', l2, 0, 0, 'BArm2')
new_vector('BC', [l3, 0, 0], 'BArm3')
new_vector('OO2', values=[l4, 0, 0], base='xyz')


# Gravity center vectors
cg1x, cg1z = new_param("cg1x",0.2), new_param("cg1z",0.1)
cg2x, cg2z = new_param("cg2x",1.0), new_param("cg2z",0.1)
cg3x, cg3z = new_param("cg3x",0.6), new_param("cg3z",0.1)
new_vector("OArm1_GArm1",cg1x,0,cg1z,"BArm1")
new_vector("OArm2_GArm2",cg2x,0,cg2z,"BArm2")
new_vector("OArm3_GArm3",cg3x,0,cg3z,"BArm3")


######## Points ########

new_point('A',  'O', 'OA')
new_point('B',  'A', 'AB')
new_point('C',  'B', 'BC')
new_point('O2', 'O', 'OO2')


######## Frames ########

new_frame('FArm1',    'O',  'BArm1')
new_frame('FArm2',    'A',  'BArm2')
new_frame('FArm3',    'B',  'BArm3')
new_frame('Fra_ABS2', 'O2', 'xyz')


######## Inertia tensors ########

I1yy, I2yy, I3yy = new_param("I1yy",1), new_param("I2yy",1), new_param("I3yy",1)
I_Arm1 = new_tensor('I_Arm1', base='BArm1')
I_Arm2 = new_tensor('I_Arm2', base='BArm2')
I_Arm3 = new_tensor('I_Arm3', base='BArm3')
I_Arm1[1, 1], I_Arm2[1, 1], I_Arm3[1, 1] = I1yy, I2yy, I3yy



######## Solids ########

new_solid("Arm1", "O"  ,"BArm1" ,"m1","OArm1_GArm1","I_Arm1")
new_solid("Arm2", "A" , "BArm2" ,"m2","OArm2_GArm2","I_Arm2")
new_solid("Arm3", "B" , "BArm3" ,"m3","OArm3_GArm3","I_Arm3")



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
dPhi_init = Matrix.block(2, 1, dPhi, Matrix([dtheta1 + pi / 3]))


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


# Load STL objects
scad2stl('Arm','Arm1', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l1);
scad2stl('Arm','Arm2', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l2);
scad2stl('Arm','Arm3', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l3);
scad2stl('Slider', r_in=0.05*l1, r_out=0.1*l1, height=0.1)


# Draw STL objects
arms = [draw_solid(f'Arm{i}', scale=1) for i in range(1, 4)]
sliders = [draw_stl('Slider.stl', scale=1, color=(0.6, 0.6, 0)) for i in range(0, 3)]

for slider, arm in zip(sliders, arms):
    slider.transform = arm.transform & Transform.xrotation(pi/2) & Transform.translation(0, 0, 0.1)


# Change camera position & focal point
camera = get_camera()
camera.position = 0.8, 4, 0.5
camera.focal_point = 0.8, 0, -0.2

# Setup what object are being shown in the viewer
toogle_drawings(solids=True, vectors=False, points=False, frames=False, others=True)


######## Simulation ########

set_integration_method('euler')
assembly_problem(Phi, Phi_q, beta, Phi_init, Phi_init_q, beta_init, dPhi_dq, dPhi_init_dq)
start_simulation(delta_t=0.01)
