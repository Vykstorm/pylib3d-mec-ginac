'''
Author: Víctor Ruiz Gómez
Description: This script allows the user to open a python prompt in parallel with
the lib3d-mec-ginac graphical interface.
'''


from argparse import ArgumentParser
from os.path import join, isdir, isfile, exists, normpath, dirname, abspath
from os import getcwd, chdir
from re import match
from copy import copy
import sys
from functools import partial
import subprocess
import threading
from signal import signal, getsignal, SIGINT, SIGPIPE
from lib3d_mec_ginac import *




if __name__ == '__main__':
    # The next code creates a command line interface (execute the script with the option -h for more info)
    parser = ArgumentParser(
        description=\
        'Open a python prompt with all the functions and methods of the ' +\
        'lib3d-mec-ginac library imported by default and the 3D viewer can be open asynchronously ' +\
        'by calling to ``show_viewer()``'
    )

    parser.add_argument('file', type=str, nargs='?', default=None,
        help='Optional python script to be executed after lib3d-mec-ginac library is imported. ' +\
        'This can also be a directory. In such case, a file with the name __main__.py  will be ' +\
        'searched inside the given folder. ' +\
        'The current working directory will be changed to the parent directory of the script indicated ' +\
        'before it is executed. ')


    #parser.add_argument('--'
    #)

    parser.add_argument('--atomization', '-a', nargs=1, default=None, choices=['on', 'off', 'true', 'false', '0', '1'],
        help='Enable/Disable atomization ' +\
        '(by default is enabled only if ``ATOMIZATION`` variable setting in the setup.py was set to "on")')

    parser.add_argument('--gravity', '-g', nargs=1, default=None, choices=['up', 'down', '1', '0'],
        help='Set gravity direction up or down ' +\
        '(by default it is set by the variable ``GRAVITY_DIRECTION`` in the setup.py)')



    # Parse input arguments
    parsed_args = parser.parse_args()

    # Enable/Disable atomization
    if parsed_args.atomization is not None:
        atomization = parsed_args.atomization[0] in ('on', 'true', '1')
        set_atomization_state(atomization)

    # Set gravity direction
    if parsed_args.gravity is not None:
        gravity_direction = parsed_args.gravity[0]
        if gravity_direction in ('0', '1'):
            gravity_direction = int(gravity_direction)
        set_gravity_direction(gravity_direction)


    # Parse script file path
    script_path = parsed_args.file
    if script_path is not None:
        script_path = normpath(script_path)
        if isdir(script_path):
            script_path = join(script_path, '__main__.py')
            if not isfile(script_path):
                parser.error(f'File "{script_path}" not found')
        else:
            if not script_path.endswith('.py'):
                parser.error(f'Script must be a file with .py extension')

        # Read script file source
        with open(script_path, 'r') as file:
            script = file.read()

        # Change current working directory
        chdir(dirname(script_path))

    else:
        script = None


    # Execute server command prompt in parallel
    viewer = get_viewer()
    server = ServerConsole(context=globals(), host='localhost', port=15010)
    server.start()

    # Execute the given script
    if script is not None:
        server.exec(script, mode='exec')


    # Execute client python prompt in a different process
    prompt = subprocess.Popen([sys.executable, join(dirname(__file__), 'utils', 'console.py'), f'localhost:15010'])


    # This is used to prevent a bug when subprocess reads from stdin and a keyboard
    # interrupt is made
    def sigint_callback(*args, **kwargs):
        if prompt.poll() is not None:
            exit(0)
    signal(SIGINT, sigint_callback)

    # Execute VTK main loop
    viewer.main(open=True)
