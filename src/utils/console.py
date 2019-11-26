'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Console
'''

from code import InteractiveConsole, compile_command
from functools import partial
from threading import Thread
import rlcompleter
import readline
import socket



def _sendmsg(s, msg):
    s.send((str(len(msg)) + '\n').encode())
    s.send(msg.encode())


def _readmsg(s):
    buffer = bytearray()
    while True:
        c = s.recv(1)
        if c == b'\n':
            break
        buffer.extend(c)
    msg_len = int(buffer.decode())
    return s.recv(msg_len).decode()





class ClientConsole(InteractiveConsole):
    def __init__(self, address='localhost', host=15010):
        super().__init__(locals=None, filename='<console>')
        self._address, self._host = address, host
        self._socket = None


    def interact(self, *args, **kwargs):
        # Connect to the remote console
        s = socket.socket()
        s.connect((self._address, self._host))
        self._socket = s

        readline.parse_and_bind('tab: complete')

        super().interact(*args, **kwargs)



    def runsource(self, source, filename='<input>', symbol='single'):
        try:
            result = compile_command(source, filename, symbol)
        except (SyntaxError, OverflowError):
            self.showsyntaxerror()
            return False

        if result is None:
            return True

        if not source:
            return False


        # TODO
        s = self._socket
        sendmsg, readmsg = partial(_sendmsg, s), partial(_readmsg, s)

        sendmsg(source)
        sendmsg(filename)
        sendmsg(symbol)
        result = readmsg()
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

        return False



if __name__ == '__main__':
    client = ClientConsole()

    try:
        client.interact()
    except ConnectionError:
        raise ConnectionError('Failed to connect to the remote python console')
