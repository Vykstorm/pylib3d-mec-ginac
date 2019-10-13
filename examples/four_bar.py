

## Imports
from lib3d_mec_ginac import *
from math import pi, e
from tabulate import tabulate


# Set gravity value
set_value('g', 9.80665)


######## Solver parameters ########

# Integration step
delta_t =             .003
# Assembly init problem solver parameters
geom_eq_init_tol =    1e-10
geom_eq_init_relax =  .1
# Assembly problem solver parameters
geom_eq_tol =         delta_t**2 * 10**-3
geom_eq_relax =       .1
# Equilibrium problem solver parameters
dyn_eq_tol =          1.0e-10
dyn_eq_relax =        .1
# Perturbed dynamic state solver parameters
per_dyn_state_tol =   1e-12
# ...


######## Generalized coordinates, velocities and accelerations ########

theta1, dtheta1, ddtheta1 = new_coord('theta1', -pi/6, 0)
theta2, dtheta2, ddtheta2 = new_coord('theta2', -2*pi/6, 0)
theta3, dtheta3, ddtheta3 = new_coord('theta3', -3*pi/6, 0)


######## Geometric parameters ########

l1, l2 = new_param('l1', 0.4), new_param('l2', 2.0)
l3, l4 = new_param('l3', 1.2), new_param('l4', 1.6)


new_base('Barm1', 'xyz', [0, 1, 0], theta1)
new_base('Barm2', 'xyz', 0, 1, 0, theta2)
new_base('Barm3', 'xyz', rotation_tupla=[0, 1, 0], rotation_angle=theta3)


new_vector('O_A', l1, 0, 0, 'Barm1')
new_vector('A_B', l2, 0, 0, 'Barm2')
new_vector('B_C', [l3, 0, 0], 'Barm3')
new_vector('O_O2', values=[l4, 0, 0], base='xyz')


new_point('OA', 'O', 'O_A')
new_point('OB', 'OA', 'A_B')
new_point('OC', 'OB', 'B_C')
new_point('O2', 'O', 'O_O2')


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


new_frame('Fra_arm1', 'O',  'Barm1')
new_frame('Fra_arm2', 'OA', 'Barm2')
new_frame('Fra_arm3', 'OB', 'Barm3')
new_frame('Fra_ABS2', 'O2', 'xyz')



######## Solids ########

new_solid('arm1', 'O',  'Barm1', 'm1', 'OArm1_GArm1', 'Iarm1')
new_solid('arm2', 'OA', 'Barm2', 'm2', 'OArm2_GArm2', 'Iarm2')
new_solid('arm3', 'OB', 'Barm3', 'm3', 'OArm3_GArm3', 'Iarm3')





######## System introspection ########

print('#'*10 + ' Symbols ' + '#'*10)
print()
print(get_symbols())
print()

print('#'*10 + ' Bases ' + '#'*10)
print()
print(get_bases())
print()

print('#'*10 + ' Vectors ' + '#'*10)
print()
print(get_vectors())
print()

print('#'*10 + ' Points ' + '#'*10)
print()
print(get_points())
print()

print('#'*10 + ' Frames ' + '#'*10)
print()
print(get_frames())
print()
