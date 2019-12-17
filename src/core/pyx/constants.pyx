'''
Author: Víctor Ruiz Gómez
Description: This module defines symbolic mathematical constants
'''




######## Math constants ########

# Symbolic constants
Pi = _expr_from_c(c_ex(c_sym_pi))
Euler = _expr_from_c(c_ex(c_sym_euler))
Tau = 2 * Pi

# Numeric constants
pi = math.pi
euler = math.e
tau = math.tau
