'''
Author: Víctor Ruiz Gómez
Description: This file defines the class JupyterClient
'''


######## Imports ########

# Standard imports
from code import compile_command
import traceback
from io import StringIO
from re import sub

# IPython
import ipykernel.kernelbase

# From other modules
from .client import Client





######## class JupyterClient ########


class JupyterClient(ipykernel.kernelbase.Kernel, Client):
    '''
    This is a custom kernel for jupyter which allows the execution of notebooks
    while the lib3d mec ginac 3D viewer is open.
    '''

    ######## Kernel info ########

    implementation = 'lib3d-mec-ginac'
    implementation_version = '1.0.0'
    language = 'python'
    language_version = '3.7'
    language_info = {
        'name': 'python',
        'mimetype': 'text/x-python',
        'file_extension': '.py',
    }
    banner = "IPython kernel which you can use to execute a notebook asynchronously with the lib3d-mec-ginac library 3D viewer"




    ######## Constructor ########

    def __init__(self, *args, **kwargs):
        ipykernel.kernelbase.Kernel.__init__(self, *args, **kwargs)
        Client.__init__(self, address='localhost:15010')



    def do_execute(self, source, silent, store_history=True, user_expressions=None,
        allow_stdin=False):
        # This is invoked when the given source code must be executed

        # Remove line breaks at the beginning and at the end
        source = source.lstrip('\n').rstrip('\n')

        # Replace line breaks between source code lines with ';'
        source = sub('\n+', ';', source)


        # Response template
        result = {
            'execution_count': self.execution_count,
            'payload': [],
            'user_expressions': {},
            'status': 'ok'
        }
        # This variable will store the output to stdout
        output = None

        try:
            # Compile the source code. Check for syntax errors (we dont want to
            # send invalid code to the server)
            compile(source, '<input>', 'single')

            # Send a code execution request to the server
            response = Client.exec(self, source, mode='single')
            response_code = response.code

            # If the execution went ok
            if response_code == 'ok':
                if not silent:
                    output = response.output

            elif response_code == 'exit':
                # A SystemExit exception was raised in the server while executing the code
                raise SystemExit


        except (SyntaxError, OverflowError, ValueError) as e:
            # Error compilling the code (print the error traceback)
            buffer = StringIO()
            traceback.print_exc(file=buffer)
            output = buffer.getvalue()

        except SystemExit:
            output = 'Connection with the server closed'

        except (BrokenPipeError, ConnectionError, OSError) as e:
            output = 'Connection with the server was closed. Restart the kernel'


        if output is not None:
            # Send the output
            stream_content = {'name': 'stdout', 'text': output}
            self.send_response(self.iopub_socket, 'stream', stream_content)



        # Return the execution result
        return result



    def do_is_complete(self, source):
        # This is invoked when a source code completness test must be performed
        response = {}
        try:
            code = compile_command(source, '<input>', 'single')
            if code is None:
                # Code is incomplete
                response['status'] = 'incomplete'
                #response['indent'] = 1
            else:
                # Code is ready to be executed
                response['status'] = 'complete'
        except (SyntaxError, ValueError, OverflowError):
            # Code is invalid
            response['status'] = 'invalid'
        return response
