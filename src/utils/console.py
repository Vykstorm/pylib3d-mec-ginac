'''
Author: Víctor Ruiz Gómez
Description: This file defines the classes ClientConsole and ServerConsole
'''

######## Import statements ########

# text autocomplete & interactive console utilities
import rlcompleter
import readline
from code import InteractiveConsole, compile_command

# multithreading & networking
from threading import Thread, RLock, Condition
from queue import Queue
import socket

# messages codification
import json
from types import SimpleNamespace

# other
from collections.abc import Mapping
from io import StringIO
from functools import partial
import sys
import traceback





######## class MessageReader ########

class MessageReader(Thread):
    '''
    This class can be used to read messages from the given socket (the program
    at the other extreme of the socket will be using the class MessageWriter to send
    messages)

    .. seealso:: :class:`MessageWriter`

    This class also inherits from Thread. It is executed asynchronously in another thread
    reading messages from the given socket indefinitely until the program finishes (it is
    a daemon thread).
    When a message is received, it is stored internally and classified by type (messages
    of the same kind are stored in a single queue).
    Other thread may consume the messages read by calling the method ``read``

    .. seealso: :func:`read`


    '''
    def __init__(self, s):
        # Initialize thread super instance
        super().__init__()
        # Set thread as daemon
        self.daemon = True
        # Initialize internal fields
        self._socket = s
        self._queues = {}
        self._cv = Condition(lock=RLock())


    def _read(self):
        s = self._socket
        buffer = bytearray()
        try:
            # Read the header (read char by char until '\n' is encountered)
            while True:
                c = s.recv(1)
                if c == b'\n':
                    break
                buffer.extend(c)
            header = buffer.decode()
            # Compute payload size
            payload_size = int(header)
            # Read the payload
            payload = json.loads(s.recv(payload_size).decode())
            # Decode the message
            kind, data = payload['kind'], SimpleNamespace(**payload['data'])
            return kind, data
        except Exception as e:
            raise ConnectionError('Failed to read message')



    def run(self):
        while True:
            # Wait for a message
            kind, message = self._read()
            with self._cv:
                if kind not in self._queues:
                    self._queues[kind] = Queue()
                self._cv.notify_all()
            # Store the message in the queue
            self._queues[kind].put(message)



    def read(self, kind):
        '''read(kind: str) -> SimpleNamespace
        Read the next message of the given type (The calling will be blocked until
        a message of that type is received)

        :rtype: SimpleNamespace

        '''
        if not isinstance(kind, str):
            raise TypeError('Input argument must be str')

        cv = self._cv
        with cv:
            # Wait for any message of the given type
            while kind not in self._queues:
                cv.wait()
            queue = self._queues[kind]
        # Consume one message of the given type from the queue
        return queue.get()






######## class AutoCompleteMessageReader ########

class AutoCompleteMessageReader(Thread):
    '''
    This class is used to receive text autocomplete requests from the client prompt
    and send back a response via sockets.
    The other program at the other extreme of the socket will use the class MessageWriter
    to send a message with the method ``write`` like this:

        :Example:

        >>> writer.send('autocomplete', SimpleNamespace(text='f'))


    A possible autocompletion output for the text 'f' would be:

        :Example:

        >>> f
        filter(     finally:    float(      for         format(     from        frozenset(

    When this instance receives the autocomplete request, the response received by
    the client (using the method ``read`` with the class ``MessageReader``) will be something like:

        :Example:

        >>> message = reader.read('autocomplete-response')
        >>> message
        SimpleNamespace(results=[ 'filter(', 'finally:', 'float(', 'for', 'format(', 'from', 'frozenset(' ])

    This class inherits from Thread; It creates a thread that waits indefinitely for new
    autocomplete requests and send back the responses.


    '''
    def __init__(self, reader, writer):
        '''
        Initialize this instance.

        :param reader: Must be an instance of the class MessageReader. It will
            be used to read the autocomplete requests.
        :param writer: Must be an instance of the class MessageWriter. It will
            be used to write the autocomplete responses.
        '''
        if not isinstance(reader, MessageReader):
            raise TypeError('reader must be an instance of the class MessageReader')
        if not isinstance(writer, MessageWriter):
            raise TypeError('writer must be an instance of the class MessageWriter')

        # Initialize Thread super instance
        super().__init__()
        # Set thread as daemon
        self.daemon = True
        # Initialize internal fields
        self._reader, self._writer = reader, writer



    def run(self):
        reader, writer = self._reader, self._writer

        # Get read line completer
        completer = readline.get_completer()

        while True:
            # Wait for the next autocomplete request
            request = reader.read('autocomplete')
            # Genereate autocomplete output using the completer function
            text = request.text
            results, i = [], 0
            while True:
                result = completer(text, i)
                if not isinstance(result, str):
                    break
                results.append(result)
                i += 1
            # Send back a response
            writer.send('autocomplete-response', SimpleNamespace(results=results))








######## class MessageWriter ########

class MessageWriter:
    '''
    This class can be used to send messages to the given socket. To do that,
    the method ``send`` must be called:

        :Example:

        >>> writer = MessageWriter(my_socket)
        >>> writer.send('execute', SimpleNamespace(code='foo = 20 + 30'))

    Messages sent the writer are simple namespaces or dictionaries.
    They are encoded as JSON text and then to bytes in order to be written to
    the socket.

    '''
    def __init__(self, s):
        self._socket = s
        self._lock = RLock() # Only one thread can use the socket at a time



    def send(self, kind, message):
        '''send(kind: str, message: SimpleNamespace | Dict)
        Send the given message to the socket attached to this instance.

        :param kind: Type of message
        :param message: The message to sent (a dictionary or simple namespace object
            with JSON compatible values)

        '''
        # Validate & parse input arguments
        if not isinstance(kind, str):
            raise TypeError('kind must be a str instance')
        if not isinstance(message, (Mapping, SimpleNamespace)):
            raise TypeError('message must be a mapping or simple namespace object')

        if isinstance(message, SimpleNamespace):
            message = message.__dict__
        elif not isinstance(message, dict):
            message = dict(message)


        s = self._socket
        try:
            # Only 1 write at a time!
            with self._lock:
                # Encode the message
                payload = json.dumps({
                    'data': message,
                    'kind': kind
                }).encode()
                # Send the header
                payload_size = len(payload)
                header = (str(payload_size) + '\n').encode()
                s.send(header)
                # Send the payload
                s.send(payload)
        except:
            raise ConnectionError('Failed to write message')








######## class ClientConsole ########

class ClientConsole(InteractiveConsole):
    '''
    This class is a python prompt where code is executed remotely in a server.
    The communication with the server is done via sockets. It also supports
    text autocompletion (syntax error checking is peformed locally before commands
    are sent to the remote console)
    '''
    def __init__(self, address='localhost', port=15010):
        '''
        Initialize this instance

        :param address: Server address
        :param host: Server port

        '''
        # Initialize InteractiveConsole super instance
        super().__init__(locals=None, filename='<console>')
        # Initialize fields
        self._address, self._port = address, port
        self._socket = None
        self._reader, self._writer = None, None



    def interact(self, *args, **kwargs):
        '''
        This method is overriden from the InteractiveConsole class.
        Must be executed on the main thread
        '''

        # Connect to the remote console
        s = socket.socket()
        s.connect((self._address, self._port))
        self._socket = s

        # Create socket reader & writer
        self._reader = MessageReader(self._socket)
        self._writer = MessageWriter(self._socket)
        self._reader.start()

        # Enable text autocomplete
        readline.parse_and_bind('tab: complete')

        # Change text autocompleter
        completer_cache = {}
        def completer(text, state):
            if text not in completer_cache:
                # Clear cache
                completer_cache.clear()
                # Send autocomplete request to the server
                self._writer.send('autocomplete', SimpleNamespace(text=text))
                # Read the response
                response = self._reader.read('autocomplete-response')
                # Store the results in the cache
                results = response.results
                completer_cache[text] = results
            # Return autocomplete result for the given state
            results = completer_cache[text]
            return results[state]

        readline.set_completer(completer)


        # Start user interaction
        super().interact(*args, **kwargs)





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

        reader, writer = self._reader, self._writer

        # Send the source code, filename and symbol to the server
        writer.send('exec', SimpleNamespace(source=source, filename=filename, symbol=symbol))
        # Read the response
        response = reader.read('exec-response')
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






######## class ServerConsole ########

class ServerConsole(Thread):
    '''
    This class is used as the backend to execute python commands sent by the client
    prompt (using the class ClientConsole).

    .. seealso:: :class:`ClientConsole`

    This class inherits from Thread; Its executed in an alternative thread waiting for
    code execution requests from the client. The code received is compiled and executed.
    The output to stdout generated by the code is sent back as a response to the client.

    '''
    def __init__(self, context, address='localhost', port=15010):
        # Initialize thread supert instance
        super().__init__()
        # Set thread as daemon
        self.daemon = True
        # Initialize internal fields
        self._address, self._port = address, port
        self._context = context


    def run(self):
        # Create the server socket
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind the address & port to the socket
        s.bind((self._address, self._port))
        s.listen(1)
        # Accept just one client
        client, adress_info = s.accept()

        # Create socket reader & writer
        reader, writer = MessageReader(client), MessageWriter(client)
        reader.start()

        # Create autocompleter manager
        autocompleter = AutoCompleteMessageReader(reader, writer)
        autocompleter.start()

        try:
            # Start reading messages
            while True:
                # Wait for source code execution request message
                message = reader.read('exec')
                try:
                    # Execute the code received
                    output = self._exec(message.source, message.filename, message.symbol)
                    # Return a response to the client (with the execution output)
                    writer.send('exec-response', SimpleNamespace(code='ok', output=output))
                except SystemExit:
                    # The result of the execution is a system exit
                    writer.send('exec-response', SimpleNamespace(code='exit'))
                    # TODO

        finally:
            # Close the connection with the client and the server socket
            client.close()
            s.close()



    def _exec(self, source, filename, symbol):
        context = self._context
        # Compile the given source code
        code = compile(source, filename, symbol)

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





if __name__ == '__main__':
    client = ClientConsole()

    try:
        client.interact()
    except ConnectionError:
        raise ConnectionError('Failed to connect to the remote python console')
