

######## Imports ########

from lib3d_mec_ginac import *
import warnings


######## Configuration ########

set_gravity_direction('up')
#set_atomization_state(False)
warnings.filterwarnings('ignore')


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


# Input vector
Fx2, Fz2 = new_input('Fx2', 0), new_input('Fz2', 0)
Fx3, Fz3 = new_input('Fx3', 0), new_input('Fz3', 0)
My2, My3 = new_input('My2', 0), new_input('My3', 0)
Fext2 = new_vector('Fext2', Fx2, 0,   Fz2, 'xyz')
Fext3 = new_vector('Fext3', Fx3, 0,   Fz3, 'xyz')
Mext2 = new_vector('Mext2', 0,   My2, 0,   'xyz')
Mext3 = new_vector('Mext3', 0,   My3, 0,   'xyz')


# Gravity center vectors
cg1x, cg1z = new_param("cg1x",0.2), new_param("cg1z",0.1)
cg2x, cg2z = new_param("cg2x",1.0), new_param("cg2z",0.1)
cg3x, cg3z = new_param("cg3x",0.6), new_param("cg3z",0.1)
new_vector("OArm1_GArm1",cg1x,0,cg1z,"BArm1")
new_vector("OArm2_GArm2",cg2x,0,cg2z,"BArm2")
new_vector("OArm3_GArm3",cg3x,0,cg3z,"BArm3")


######## Points ########

A = new_point('A',  'O', 'OA')
B = new_point('B',  'A', 'AB')
C = new_point('C',  'B', 'BC')
O2 = new_point('O2', 'O', 'OO2')


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

Arm1 = new_solid("Arm1", "O"  ,"BArm1" ,"m1","OArm1_GArm1","I_Arm1")
Arm2 = new_solid("Arm2", "A" , "BArm2" ,"m2","OArm2_GArm2","I_Arm2")
Arm3 = new_solid("Arm3", "B" , "BArm3" ,"m3","OArm3_GArm3","I_Arm3")


######## Force & Momentum ########

K = new_param('K', 50)
l2x = new_param('l2x', 1)
l3x, l3z = new_param('l3x', 0.5), new_param('l3z', 0.1)

OArm2_L2 = new_vector('OArm2_L2', l2x, 0, 0, 'BArm2')
OArm3_L3 = new_vector('OArm3_L3', l3x, 0, 0, 'BArm3')

OL2 = new_point('OL2', 'A', OArm2_L2)
OL3 = new_point('OL3', 'B', OArm3_L3)

OL2_OL3 = position_vector(OL2, OL3)
FK = K * OL2_OL3
MK = new_vector('MK_GroundPend1', 0, 0, 0, 'xyz')



######## Wrenches ########

# Gravity wrenches
Gravity_Arm1 = gravity_wrench('Arm1')
Gravity_Arm2 = gravity_wrench('Arm2')
Gravity_Arm3 = gravity_wrench('Arm3')

# Inertia wrenches
Inertia_Arm1 = inertia_wrench('Arm1')
Inertia_Arm2 = inertia_wrench('Arm2')
Inertia_Arm3 = inertia_wrench('Arm3')

# Constitutive wrenches
SpringA = new_wrench('SpringA', FK,   MK, OL2, Arm2, 'Constitutive')
SpringB = new_wrench('SpringR', -FK, -MK, OL3, Arm3, 'Constitutive')

# External wrenches
FMext2 = new_wrench('FMext2', Fext2, Mext2, A, Arm2, 'External')
FMext3 = new_wrench('FMext3', Fext3, Mext3, B, Arm3, 'External')

Sum_Wrenches_Arm1 = Inertia_Arm1 + Gravity_Arm1
Sum_Wrenches_Arm2 = Inertia_Arm2 + Gravity_Arm2 + SpringA + FMext2
Sum_Wrenches_Arm3 = Inertia_Arm3 + Gravity_Arm3 - SpringA + FMext3

Twist_Arm1, Twist_Arm2, Twist_Arm3 = twist('Arm1'), twist('Arm2'), twist('Arm3')




######## Matrices of symbols ########

q,   q_aux   = get_coords_matrix(),        get_aux_coords_matrix()
dq,  dq_aux  = get_velocities_matrix(),    get_aux_velocities_matrix()
ddq, ddq_aux = get_accelerations_matrix(), get_aux_accelerations_matrix()
epsilon      = get_joint_unknowns_matrix()


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

# gamma
gamma = -ddPhi
gamma = subs(gamma, ddq, 0)
gamma = subs(gamma, ddq_aux, 0)



######## Dynamic equations ########


# Dyn_eq_VP
Dyn_eq_VP = Matrix([
    Sum_Wrenches_Arm1 * diff(Twist_Arm1, to_symbol(dq[k, 0])) + \
    Sum_Wrenches_Arm2 * diff(Twist_Arm2, to_symbol(dq[k, 0])) + \
    Sum_Wrenches_Arm3 * diff(Twist_Arm3, to_symbol(dq[k, 0]))   \
    for k in range(0, 3)
], shape=[3, 1])

# Dyn_eq_VP_open
Dyn_eq_VP_open = Dyn_eq_VP
Dyn_eq_VP_open = subs(Dyn_eq_VP_open, epsilon, 0)

# M_qq
M_qq = jacobian(Dyn_eq_VP_open.transpose(), ddq, 1)

# delta_q
delta_q = -Dyn_eq_VP_open
delta_q = subs(delta_q, ddq, 0)
delta_q = subs(delta_q, ddq_aux, 0)



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
scad2stl('Arm','Arm1', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l1)
scad2stl('Arm','Arm2', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l2)
scad2stl('Arm','Arm3', rod_r=0.05*l1, r_in=0.1*l1, d=0.2*l1, l=l3)
scad2stl('Slider', 'Slider1', r_in=0.05*l1, r_out=0.1*l1, height=0.1)
scad2stl('Slider', 'Slider2', r_in=0.05*l1, r_out=0.1*l1, height=0.25)


# Draw arms
arms_drawings = [draw_solid(f'Arm{i}', scale=1) for i in range(1,4)]
arms_drawings[0].transform &= Transform.translation(0, 0.35*l1, 0)

# Draw sliders
sliders_drawings = [
    draw_stl('Slider1.stl', color=(0.6, 0.6, 0)),
    draw_stl('Slider2.stl', color=(0.6, 0.6, 0)),
    draw_stl('Slider1.stl', color=(0.6, 0.6, 0))
]
xrot = Transform.xrotation(pi/2)
sliders_drawings[0].transform = arms_drawings[0].transform & xrot & Transform.translation(0, 0, 0.1)
sliders_drawings[1].transform = arms_drawings[1].transform & xrot & Transform.translation(0, 0, -0.05)
sliders_drawings[2].transform = arms_drawings[2].transform & xrot & Transform.translation(0, 0, 0.1)


# Change camera position & focal point
camera = get_camera()
camera.position = 0.8, 4, 0.5
camera.focal_point = 0.8, 0, -0.2



######## MATLAB export ########

export_numeric_init_func_MATLAB()
export_numeric_func_MATLAB(Phi, 'Phi_', 'Phi_out')
export_numeric_func_MATLAB(Phi_q, 'Phi_q_', 'Phi_q_out')
export_numeric_func_MATLAB(dPhi_dq, 'dPhi_dq_', 'dPhi_dq_out')
export_numeric_func_MATLAB(beta, 'beta_', 'beta_out')
export_numeric_func_MATLAB(gamma, 'gamma_', 'gamma_out')
export_numeric_func_MATLAB(Phi_init, 'Phi_init_', 'Phi_init_out')
export_numeric_func_MATLAB(Phi_init_q, 'Phi_init_q_', 'Phi_init_q_out')
export_numeric_func_MATLAB(dPhi_init_dq, 'dPhi_init_dq_', 'dPhi_init_dq_out')
export_numeric_func_MATLAB(beta_init, 'beta_init_', 'beta_init_out')
export_numeric_func_MATLAB(M_qq, 'M_qq_', 'M_qq_out')
export_numeric_func_MATLAB(delta_q, 'delta_q_', 'delta_q_out')



######## Simulation & Viewer ########

# Setup integration method
set_integration_method('euler')

# Configure assembly problem constraints
assembly_problem(Phi, Phi_q, beta, Phi_init, Phi_init_q, beta_init, dPhi_dq, dPhi_init_dq)

# Setup what objects are being shown in the viewer
toogle_drawings(solids=True, vectors=False, points=False, frames=False, grid=False, others=True)

# Start the simulation
start_simulation(delta_t=0.05)

# Finally open the viewer to watch the simulation
open_viewer()
