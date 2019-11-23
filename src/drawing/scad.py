'''
Author: Víctor Ruiz Gómez
Description: This file defines the function scad_to_stl function.
'''


import json
from os import devnull
from os.path import dirname, join, exists, normpath
from re import sub
from types import SimpleNamespace
import subprocess
from subprocess import CalledProcessError
from itertools import repeat, chain
from operator import add
from functools import reduce
from ..config import runtime_config




def scad_to_stl(scad_filename, stl_filename=None, **kwargs):
    '''
    Converts the input .scad file to the a .stl file using the openscad command
    line utility (A subprocess is created to call it)

    The next example shows how to create a stl file (``Arm.stl``) using
    ``Arm.scad`` model (It can be found in the four_bar example).
    We set the variables ``n_facets=20`` and ``r_rod=10`` to generate the geometry.

            :Example:

            >>> scad_to_stl('Arm.scad', n_facets=20, r_rod=10)
            'Arm.stl'


    :param scad_filename: Input scad filename (Must have .scad extension)
    :param stl_filename: Output stl filename (Must have .stl extension). By default it is the same as the
        input scad filename but replacing the extension to .stl
    :param kwargs: Additional parameters to be passed to openscad (with -D option).

    :return: The name of the stl file.

    :raise ValueError: If the input scad filename dont have .scad extension or the output
        stl filename dont have .stl extension
    :raise FileNotFoundError: If the scad file doesnt exist
    :raise RuntimeError: If the conversion couldnt be done


    '''
    # Check input arguments
    if not isinstance(scad_filename, str):
        raise TypeError('scad_filename must be a str object')
    if stl_filename is not None and not isinstance(stl_filename, str):
        raise TypeError('stl_filename must be a str object')

    # Scad filename must end with .scad and stl filename with .stl
    if not scad_filename.endswith('.scad'):
        raise ValueError('scad filename must have .scad extension')
    if stl_filename is None:
        # stl filename not specified (use scad filename but replacing its extension)
        stl_filename = sub('.scad$', '.stl', scad_filename)

    elif not stl_filename.endswith('.stl'):
        raise ValueError('stl filename must have .stl extension')

    # Check that input scad file exists
    if not exists(scad_filename):
        raise FileNotFoundError(f'File "{scad_filename}" doesnt exist')

    stl_filename, scad_filename = normpath(stl_filename), normpath(scad_filename)


    # Parse additional key-value options
    var_options = reduce(add, zip(repeat('-D'), map('='.join, zip(kwargs.keys(), map(str, kwargs.values())))), ())

    # Spawn subprocess to call openscad command line
    program = runtime_config.OPENSCADCMD
    options = ['-o', stl_filename, scad_filename]
    args = list(chain([program], var_options, options))

    with open(devnull) as stderr: # Supress stdout and stderr of subprocess
        stdout = stderr
        try:
            result = subprocess.run(args, check=True, stderr=stderr, stdout=stdout)
        except CalledProcessError as e:
            raise RuntimeError(f'Couldnt convert scad to stl file')

    return stl_filename



# Alias of function defined above
scad2stl = scad_to_stl
