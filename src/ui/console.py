'''
Author: Víctor Ruiz Gómez
Description: This file defines the class ConsoleClient
'''



######## Imports ########


# Standard imports
import rlcompleter
import readline
from code import InteractiveConsole, compile_command

# From other modules
from .client import Client





######## class ConsoleClient ########

class ConsoleClient(Client, InteractiveConsole):
    def __init__(self, address):
        Client.__init__(self, address)
        InteractiveConsole.__init__(self, locals=None, filename='<console>')



    def interact(self, *args, **kwargs):
        # Enable text autocomplete
        readline.parse_and_bind('tab: complete')

        # Change text autocompleter
        completer_cache = {}
        def completer(text, state):
            if text not in completer_cache:
                # Clear cache
                completer_cache.clear()
                # Send an autocomplete text request
                results = self.autocomplete(text)
                # Store the results in the cache
                completer_cache[text] = results
            # Return autocomplete result for the given state
            results = completer_cache[text]
            return results[state]

        readline.set_completer(completer)

        InteractiveConsole.interact(self, *args, **kwargs)



    def runsource(self, source, filename='<input>', symbol='single'):
        # This method is invoked whenever the user tries to execute any source
        # code in the prompt

        # Check for syntax errors locally
        try:
            result = compile_command(source, filename, symbol)
        except (SyntaxError, OverflowError):
            # Syntax error (show it in stderr)
            self.showsyntaxerror()
            return False

        if result is None:
            # Source code is correct but incomplete
            return True

        if not source:
            # Source code is an empty string
            return False

        response = self.exec(source, filename, symbol)
        response_code = response.code
        if response_code in ('ok', 'error'):
            # The execution in the server was okay or raised an exception (not a SystemExit)
            print(response.output, end='', flush=True)
        elif response_code == 'exit':
            # Server raised SystemExit exception
            exit(0)
        else:
            # Invalid response
            raise ConnectionError

        # Code was correct, complete and executed
        return False







if __name__ == '__main__':
    '''
    When executing this file as a script a client console prompt is run.
    You can indicate the address and port of the remote server.
    '''
    # Validate & parse CLI arguments
    parser = ArgumentParser(description='This script runs a python prompt where the code is executed '+\
        'remotely on the given server (it support text autocompletion)')

    parser.add_argument('address', type=str, default='localhost:15010', nargs='?',
        help='Server address (localhost:15010 by default)')

    parsed_args = parser.parse_args()


    # Create client console
    client = ConsoleClient()

    try:
        # Start user interaction
        client.interact()
    except ConnectionError:
        raise ConnectionError('Failed to connect to the remote python console')
