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
m = v.skew * v.skew * v.skew * v.module
func = m.get_numeric_function()


# Print numeric function atoms & output info
print("Numeric function atoms: ")
atoms = func.atoms
print( tabulate(zip(atoms.keys(), atoms.values()), tablefmt='simple', headers=()) )

print("Numeric function output: ")
outputs = func.outputs
print('[')
for row in outputs:
    print(f'\t[ {", ".join(map(methodcaller("ljust", 20), row))} ]')
print(']')


# Print atomization state on/off and python debug mode
print(f"Atomization is {'enabled' if get_atomization_state() == 1 else 'disabled'}")
print(f"Python debug mode is {'enabled' if __debug__ else 'disabled'}")
print()

# Start benchmark & print time metrics
print("Starting benchmark...")
n = 50000
result = min(timeit.repeat(lambda: evaluate(func), repeat=10, number=n)) / n
print("Average evaluation time: {:5f} milliseconds".format(result*1000))
