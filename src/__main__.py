'''
Author: Víctor Ruiz Gómez
Description: This script allows the user to open a python prompt in parallel with
the lib3d-mec-ginac graphical interface.
'''


from argparse import ArgumentParser
from os.path import join, isdir, isfile, exists, normpath, dirname
from os import getcwd, chdir
from re import match
from copy import copy
import sys
from functools import partial
from lib3d_mec_ginac import *



if __name__ == '__main__':
    # The next code creates a command line interface (execute the script with the option -h for more info)
    parser = ArgumentParser(
        description=\
        'Open a python prompt with all the functions and methods of the ' +\
        'lib3d-mec-ginac library imported by default and the 3D viewer can be open asynchronously ' +\
        'calling to show_viewer()'
    )

    parser.add_argument('file', type=str, nargs='?', default=None,
        help='Optional python script to be executed after lib3d-mec-ginac library is imported. ' +\
        'This can also be a directory. In such case, a file with the name __main__.py  will be ' +\
        'searched inside the given folder. This can be set also to any predefined example of the library (e.g: "four_bar")' +\
        'The current working directory will be changed to the parent directory of the script indicated ' +\
        'before it is executed.')

    parser.add_argument('--show-viewer', action='store_true',
        help='Open 3D viewer after running the given script. By default is not open. You must invoke ' +\
            'show_viewer() to open it')

    ## Parse input arguments
    parsed_args = parser.parse_args()


    # Parse script file path
    script_path = parsed_args.file
    if script_path is not None:
        script_path = normpath(script_path)
        if not exists(script_path):
            if match('\w+', script_path):
                script_path = join(dirname(__file__), '..', 'examples', script_path)
            else:
                parser.error(f'File or directory "{script_path}" doesnt exist')

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

    # Execute the given script

    # Execute server command prompt in parallel
    server = ServerConsole(context=globals())
    server.start()

    # Execute VTK main loop
    get_viewer().main()
