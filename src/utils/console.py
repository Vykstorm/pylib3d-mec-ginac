'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Console
'''

from threading import Thread, RLock, Condition
import rlcompleter
import readline
from code import InteractiveConsole, compile_command

import socket
import json
from queue import Queue
from types import SimpleNamespace
from contextlib import contextmanager
from io import StringIO
from functools import partial
import sys
import traceback



class MessageReader(Thread):
    '''
    This class can be used to read messages from the given socket
    '''
    def __init__(self, s):
        super().__init__()
        self.daemon = True
        self._socket = s
        self._queues = {}
        self._cv = Condition(lock=RLock())


    def _read(self):
        s = self._socket
        buffer = bytearray()
        try:
            # Read the header
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
            print(e)
            raise ConnectionError('Failed to read message')



    def run(self):
        while True:
            kind, message = self._read()
            with self._cv:
                if kind not in self._queues:
                    self._queues[kind] = Queue()
                self._cv.notify_all()
            self._queues[kind].put(message)


    def read(self, kind):
        cv = self._cv
        with cv:
            while kind not in self._queues:
                cv.wait()
            queue = self._queues[kind]
        return queue.get()




class AutoCompleteMessageReader(Thread):
    '''
    This class is used to receive text autocomplete requests from the client prompt
    and send back the response (using readling completer)
    '''
    def __init__(self, reader, writer):
        super().__init__()
        self.daemon = True
        self._reader, self._writer = reader, writer


    def run(self):
        reader, writer = self._reader, self._writer
        completer = readline.get_completer()

        while True:
            request = reader.read('autocomplete')
            text = request.text
            results, i = [], 0
            while True:
                result = completer(text, i)
                if not isinstance(result, str):
                    break
                results.append(result)
                i += 1

            writer.send('autocomplete-response', SimpleNamespace(results=results))






class MessageWriter:
    '''
    This class can be used to send messages from the given socket
    '''
    def __init__(self, s):
        self._socket = s
        self._lock = RLock()

    def send(self, kind, message):
        s = self._socket
        try:
            with self._lock:
                # Encode the message
                payload = json.dumps({
                    'data': message.__dict__,
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








class ClientConsole(InteractiveConsole):
    '''
    This class is a python prompt where code is executed remotely in a server.
    The communication with the server is done via sockets. It also supports
    autocomplete.
    '''
    def __init__(self, address='localhost', host=15010):
        super().__init__(locals=None, filename='<console>')
        self._address, self._host = address, host
        self._socket = None
        self._reader, self._writer = None, None



    def interact(self, *args, **kwargs):
        # Connect to the remote console
        s = socket.socket()
        s.connect((self._address, self._host))
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
                self._writer.send('autocomplete', SimpleNamespace(text=text))
                response = self._reader.read('autocomplete-response')
                results = response.results
                completer_cache[text] = results
            results = completer_cache[text]
            return results[state]


        readline.set_completer(completer)


        # Start user interaction
        super().interact(*args, **kwargs)




    def runsource(self, source, filename='<input>', symbol='single'):
        # Check for syntax errors in the source code
        try:
            result = compile_command(source, filename, symbol)
        except (SyntaxError, OverflowError):
            self.showsyntaxerror()
            return False

        if result is None:
            return True

        if not source:
            return False


        # Send the source code, filename and symbol to the server
        reader, writer = self._reader, self._writer

        writer.send('exec', SimpleNamespace(source=source, filename=filename, symbol=symbol))
        response = reader.read('exec-response')
        response_code = response.code
        if response_code in ('ok', 'error'):
            print(response.output, end='', flush=True)
        elif response_code == 'exit':
            exit(0)
        else:
            raise ConnectionError

        return False





class ServerConsole(Thread):
    '''
    This class is used as the backend to execute python commands sent by the client
    promt.
    '''
    def __init__(self, context, address='localhost', host=15010):
        super().__init__()
        self.daemon = True
        self._address, self._host = address, host
        self._context = context


    def run(self):
        # Create the server socket
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self._address, self._host))
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
                # Wait for a execute source code request message
                message = reader.read('exec')
                try:
                    # Execute the code received
                    output = self._exec(message.source, message.filename, message.symbol)
                    # Return a response to the client (with the execution output)
                    writer.send('exec-response', SimpleNamespace(code='ok', output=output))
                except SystemExit:
                    # The result of the execution is a halt requestsw
                    writer.send('exec-response', SimpleNamespace(code='exit'))

        finally:
            # Close the connection with the client and the server socket
            client.close()
            s.close()



    def _exec(self, source, filename, symbol):
        # Execute the given source code
        context = self._context
        code = compile(source, filename, symbol)

        prev_stdout, output = sys.stdout, StringIO()
        sys.stdout = output
        try:
            exec(code, context)
        except SystemExit:
            raise SystemExit
        except:
            traceback.print_exc(file=sys.stdout)
        finally:
            sys.stdout = prev_stdout
        return output.getvalue()








if __name__ == '__main__':
    client = ClientConsole()

    try:
        client.interact()
    except ConnectionError:
        raise ConnectionError('Failed to connect to the remote python console')
