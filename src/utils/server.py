
from threading import Thread
from code import InteractiveConsole
import socket
import sys
from contextlib import contextmanager
from io import StringIO
from functools import partial


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



def _exec(source, filename, symbol, context):
    code = compile(source, filename, symbol)

    prev_stdout = sys.stdout
    sys.stdout = StringIO()
    try:
        exec(code, context)
        return sys.stdout.getvalue()
    finally:
        sys.stdout = prev_stdout





class ServerConsole(Thread):
    def __init__(self, context, address='localhost', host=15010):
        Thread.__init__(self)
        self.daemon = True
        self._address, self._host = address, host
        self._context = context


    def run(self):
        context = self._context
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self._address, self._host))
        s.listen(1)
        client, adress_info = s.accept()

        sendmsg, readmsg = partial(_sendmsg, client), partial(_readmsg, client)

        try:
            while True:
                source = readmsg()
                filename = readmsg()
                symbol = readmsg()

                try:
                    output = _exec(source, filename, symbol, context)
                    sendmsg('ok')
                    sendmsg(output)

                except SystemExit:
                    sendmsg('exit')
                except Exception as e:
                    sendmsg('error')
                    sendmsg(str(e))


        finally:
            client.close()
            s.close()



if __name__ == '__main__':
    server = ServerConsole(context=globals())
    server.run()
