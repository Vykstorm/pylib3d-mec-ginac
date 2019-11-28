'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Console
'''

from code import InteractiveConsole, compile_command
from functools import partial
from threading import Thread, RLock
import rlcompleter
import readline
import socket

import json
from queue import Queue
from types import SimpleNamespace



class MessageReader(Thread):
    '''
    This class can be used to read messages from the given socket
    '''
    def __init__(self, s):
        super().__init__()
        self.daemon = True
        self._socket = s
        self._callbacks = []
        self._lock = RLock()


    def read(self):
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
            payload = s.recv(payload_size).decode()
            # Decode the message
            message = SimpleNamespace(**json.loads(payload))
            return message
        except:
            raise ConnectionError('Failed to read message')



    def add_callback(self, callback):
        with self._lock:
            self._callbacks.append(callback)


    def run(self):
        while True:
            message = self.read()
            with self._lock:
                for callback in self._callbacks:
                    callback(message)





class MessageWriter:
    '''
    This class can be used to send messages from the given socket
    '''
    def __init__(self, s):
        self._socket = s

    def send(self, message):
        s = self._socket
        try:
            # Encode the message
            payload = json.dumps(message.__dict__).encode()
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
        self._reader = MessageReader(self._socket)
        self._writer = MessageWriter(self._socket)

        readline.parse_and_bind('tab: complete')

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

        writer.send(SimpleNamespace(source=source, filename=filename, symbol=symbol))

        '''
        if result == 'ok':
            output = readmsg()
            print(output)
        elif result == 'exit':
            exit(0)
        elif result == 'error':
            info = readmsg()
            print(info)
        else:
            raise ConnectionError
        '''

        return False




if __name__ == '__main__':
    client = ClientConsole()

    try:
        client.interact()
    except ConnectionError:
        raise ConnectionError('Failed to connect to the remote python console')
