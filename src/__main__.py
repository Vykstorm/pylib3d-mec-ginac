'''
Author: Víctor Ruiz Gómez
Description: This script allows the user to open a python prompt in parallel with
the lib3d-mec-ginac graphical interface.
'''



######## Imports ########

# CL
from argparse import ArgumentParser

# Filepaths & working directory handling
from os.path import join, isdir, isfile, exists, normpath, dirname, abspath
from os import getcwd, chdir

# Multithreading
from threading import RLock, Thread

# Subprocesses & signals
import subprocess
from signal import signal, getsignal, SIGINT, SIGPIPE

# other
import sys
from io import StringIO
import traceback

# From other modules
from lib3d_mec_ginac import *






class AutoCompleteRequestManager(Thread):
    def __init__(self, conn, context):
        super().__init__()
        self.daemon = True
        self._conn = conn
        self._context = context


    def run(self):
        conn = self._conn
        try:
            while True:
                # Wait for the next autocomplete request
                request = conn.readmsg('autocomplete')

                # Genereate autocomplete output using the completer function
                results = autocomplete(request.text, self._context)

                # Send back a response
                conn.writemsg('autocomplete-response', dict(results=results))

        except ConnectionError:
            pass




######## class Controller ########

class Controller(Server):
    def __init__(self, address):
        super().__init__(address)
        self._viewer = get_viewer()
        self._context = globals()
        self._lock = RLock()
        self.start()


    def handle_connection(self, conn):
        # Handle autocomplete requests asynchronously
        AutoCompleteRequestManager(conn, self._context).start()

        try:
            with conn:
                # Start reading messages
                while True:
                    # Wait for source code execution request message
                    message = conn.readmsg('exec')
                    try:
                        # Execute the code received
                        output = self.exec(**message.__dict__)
                        # Return a response to the client (with the execution output)
                        conn.writemsg('exec-response', dict(code='ok', output=output))
                    except SystemExit:
                        # The result of the execution is a system exit
                        conn.writemsg('exec-response', dict(code='exit'))
                        break
        except ConnectionError:
            pass



    def exec(self, source, filename='<input>', mode='single'):
        with self._lock:
            context = self._context

            # Compile the given source code
            code = compile(source, filename, mode)
            # Redirect stdout to a temporal buffer
            prev_stdout, output = sys.stdout, StringIO()
            sys.stdout = output
            try:
                # Execute the code
                exec(code, context)
            except SystemExit:
                raise SystemExit
            except:
                # If a exception was generated, print the exception traceback
                traceback.print_exc(file=sys.stdout)
            finally:
                # Retore stdout
                sys.stdout = prev_stdout
            # Return output temporal buffer contents
            return output.getvalue()


    def main(self):
        self._viewer.main(open=True)










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


    parser.add_argument('--no-console', action='store_true',
        help='If specified, dont create the python prompt')

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


    address = 'localhost:15010'
    controller = Controller(address=address)

    # Execute the script given by the user
    if script is not None:
        controller.exec(script, mode='exec')


    if not parsed_args.no_console:
        # Execute client python prompt in a different process
        prompt = subprocess.Popen([
            sys.executable,
            '-c',
            ';'.join([
                'from lib3d_mec_ginac.ui.console import ConsoleClient',
                f'ConsoleClient("{address}").interact()'
            ])
        ])

        # This is used to prevent a bug when subprocess reads from stdin and a keyboard
        # interrupt is made
        def sigint_callback(*args, **kwargs):
            if prompt.poll() is not None:
                exit(0)
        signal(SIGINT, sigint_callback)

    # Execute VTK main loop
    controller.main()
