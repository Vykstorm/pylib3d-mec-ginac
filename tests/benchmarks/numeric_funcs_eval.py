'''
Author: Víctor Ruiz Gómez
Description: Benchmark to evaluate the performance of numeric functions evaluation.
'''


from lib3d_mec_ginac import *
import timeit
from tabulate import tabulate
from itertools import count
from operator import methodcaller


# Define a dummy matrix where to extract the numeric function to be evaluated.
a, b, c, d = new_param('a', 1), new_param('b', 2), new_param('c', 3), new_param('d', 4)
v = new_vector('v', a, b, c)
m = v.skew * v.skew * v.skew * v.skew * v.skew * v.module
func = get_numeric_function(m, c_optimized=False)
func_optimized = get_numeric_function(m, c_optimized=True)



# Print atomization state on/off and python debug mode
print(f"Atomization is {'enabled' if get_atomization_state() == 1 else 'disabled'}")
print(f"Python debug mode is {'enabled' if __debug__ else 'disabled'}")
print()

# Start benchmark & print time metrics
print("Starting benchmark...")
n = 10000
result = min(timeit.repeat(lambda: func.evaluate(), repeat=10, number=n)) / n
print("Average evaluation time (unoptimized): {:5f} milliseconds".format(result*1000))
result = min(timeit.repeat(lambda: func_optimized.evaluate(), repeat=10, number=n)) / n
print("Average evaluation time (optimized): {:5f} milliseconds".format(result*1000))
