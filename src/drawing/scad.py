'''
Author: Víctor Ruiz Gómez
Description: This file defines the function scad_to_stl function.
'''

# filepath & os utilities
from os import devnull
from os.path import dirname, join, exists, normpath
# regex
from re import sub, match
# subprocesses & multithreading
import subprocess
from subprocess import CalledProcessError
from threading import Thread
# other utilities
from itertools import repeat, chain
from operator import add
from functools import reduce
# local imports
from ..config import runtime_config
from .events import EventProducer
from ..utils.singleton import singleton

@singleton
class ScadToStlManager(EventProducer):
    def __init__(self):
        super().__init__()
        self._loading_stls = []
        self.add_event_handler(self._on_event)

    def _on_event(self, event_type, source, stl_filename, *args, **kwargs):
        if event_type in ("stl_model_loaded", "stl_model_loading_failed"):
            self._loading_stls.remove(stl_filename)


    def get_loading_stls(self):
        return self._loading_stls


    def scad_to_stl(self, scad_filename, stl_filename, **kwargs):
        # Check input arguments
        if not isinstance(scad_filename, str):
            raise TypeError('scad_filename must be a str object')
        if stl_filename is not None and not isinstance(stl_filename, str):
            raise TypeError('stl_filename must be a str object')

        if '.' not in scad_filename:
            scad_filename += '.scad'
        elif not scad_filename.endswith('.scad'):
            # Scad filename must end with .scad
            raise ValueError('scad filename must have .scad extension')
        if stl_filename is None:
            # stl filename not specified (use scad filename but replacing its extension)
            stl_filename = sub('.scad$', '.stl', scad_filename)

        else:
            if '.' not in stl_filename:
                stl_filename += '.stl'
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

        # Add the stl to the loading list
        self._loading_stls.append(stl_filename)

        manager = self
        class Worker(Thread):
            def __init__(self):
                super().__init__()
                self.daemon = True

            def run(self):
                with open(devnull) as stderr: # Supress stdout and stderr of subprocess
                    stdout = stderr
                    try:
                        result = subprocess.run(args, check=True, stderr=stderr, stdout=stdout)
                        manager.fire_event('stl_model_loaded', stl_filename)
                    except CalledProcessError as e:
                        manager.fire_event('stl_model_loading_failed', stl_filename)

        worker = Worker()
        worker.start()

        return stl_filename




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
    ScadToStlManager().scad_to_stl(scad_filename, stl_filename, **kwargs)



# Alias of function defined above
scad2stl = scad_to_stl
