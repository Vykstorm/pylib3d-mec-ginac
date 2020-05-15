'''
Author: Víctor Ruiz Gómez
Description: This is the CLI for the library
'''

from argparse import ArgumentParser

# Build CLI
parser = ArgumentParser(
    description='Command line interface for lib3d-mec-ginac library python extension'
)
parser.add_argument('file', type=str, nargs='?', help='Optional file to execute')
parser.add_argument('--atomization', '-a', choices=('on', 'off'), default=None, help='Enable or disable atomization')
parser.add_argument('--gravity', '-g', choices=('up', 'down'), default=None, help='Set gravity directon up/down')
parser.add_argument('--no-gui', default=False, action='store_true', help='Dont open the 3D viewer!')
parser.add_argument('--no-ide', default=False, action='store_true', help='If the 3D viewer is open, show it without file editor & console')


# Parse CLI args
args = parser.parse_args()

del parser, ArgumentParser


# Import all packages and functions that will be avaliable in the GUI shell
import numpy as np
import lib3d_mec_ginac
import lib3d_mec_ginac.gui
from lib3d_mec_ginac import *

# Process CLI arguments
if args.atomization is not None:
    set_atomization_state(args.atomization)
if args.gravity is not None:
    set_gravity_direction(args.gravity)
_no_gui = args.no_gui
_no_ide = args.no_ide
_filepath = args.file

del args



from copy import copy
_default_environment = copy(globals())
del copy



# This is a small hack to prevent the gui to be open before the script is executed
_open_viewer = open_viewer
def open_viewer(*args, **kwargs):
    pass
lib3d_mec_ginac.open_viewer = open_viewer

# Default environment ( global variables ) for the shell (IDE)
lib3d_mec_ginac.gui._default_environment = _default_environment
del _default_environment


# Execute file if specified
if _filepath is not None:
    try:
        import os.path

        if os.path.isdir(_filepath):
            _filepath = os.path.join(_filepath, '__main__.py')

        with open(_filepath, 'r') as file:
            # Change the working directory to the script`s folder
            os.chdir(os.path.dirname(_filepath))
            code = file.read()
            # Execute code in the script
            exec(code, globals())

        del code, file, os
    except FileNotFoundError:
        parser.error(f'File "{filepath}" not found')
del _filepath


# Open the 3D viewer

if not _no_gui:
    _open_viewer(gui=not _no_ide)
