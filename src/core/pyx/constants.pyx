'''
Author: Víctor Ruiz Gómez
Description: This module defines symbolic mathematical constants
'''




######## Math constants ########

pi = _expr_from_c(c_ex(c_sym_pi))
catalan = _expr_from_c(c_ex(c_sym_catalan))
euler = _expr_from_c(c_ex(c_sym_euler))
tau = 2 * pi
