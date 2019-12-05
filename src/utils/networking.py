'''
Author: Víctor Ruiz Gómez
Description: This file defines the classes Socket, ServerSocket, ClientSocket,
SocketMessageReader and SocketMessageWriter
'''


######## Import statements ########

# multithreading & networking
import socket
from socket import socket as create_socket
from threading import Thread, RLock, Condition
from collections import deque

# message codification
import json
from types import SimpleNamespace


# other
from abc import ABC, abstractmethod
from collections.abc import Mapping




######## Helper methods ########

def _parse_address(address):
    if not isinstance(address, str):
        raise TypeError('address must be a string')
    try:
        tokens = address.split(':')
        if len(tokens) != 2:
            raise Exception
        host, port = tokens
        port = int(port)
        return host, port
    except:
        raise ValueError('Invalid address')




######## class Socket ########

class Socket:
    def __init__(self, conn):
        self._conn = conn
        self._reader, self._writer = SocketMessageReader(conn), SocketMessageWriter(conn)
        self._reader.start()


    def readmsg(self, kind):
        return self._reader.readmsg(kind)


    def writemsg(self, kind, message):
        self._writer.writemsg(kind, message)


    def close(self):
        self._conn.close()


    def __enter__(self):
        return self


    def __exit__(self, exc_type, exc_value, tb):
        self.close()



    @classmethod
    def connect_to(cls, address):
        conn = create_socket()
        conn.connect(_parse_address(address))
        return cls(conn)




######## class ServerSocket ########


class Server(ABC, Thread):
    def __init__(self, address, backlog=5):
        if not isinstance(backlog, int) or backlog <= 0:
            raise TypeError('backlog must be an integer greater or equal than zero')

        Thread.__init__(self)
        ABC.__init__(self)
        self.daemon = True
        self._address, self._backlog = _parse_address(address), backlog


    def run(self):
        conn = create_socket()
        conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        conn.bind(self._address)
        conn.listen(self._backlog)

        while True:
            client_conn = Socket(conn.accept()[0])
            th = Thread(target=self.handle_connection, args=(client_conn,))
            th.start()


    @abstractmethod
    def handle_connection(self, conn):
        pass




######## class SocketMessageReader ########


class SocketMessageReader(Thread):
    def __init__(self, conn):
        super().__init__()
        self.daemon = True
        self._conn = conn
        self._queues = {}
        self._closed = False
        self._cv = Condition(lock=RLock())


    def run(self):
        try:
            while True:
                # Wait for a message
                kind, message = self._read()
                with self._cv:
                    if kind not in self._queues:
                        self._queues[kind] = deque()
                    # Store the message in the queue
                    self._queues[kind].append(message)
                    self._cv.notify_all()
        except:
            # Underline socket was closed manually just to clean up
            pass
        finally:
            with self._cv:
                self._closed = True
                self._cv.notify_all()



    def _read(self):
        s = self._conn
        buffer = bytearray()
        try:
            # Read the header (read char by char until '\n' is encountered)
            while True:
                c = s.recv(1)
                if not c:
                    raise Exception
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
        except:
            raise ConnectionError



    def readmsg(self, kind):
        if not isinstance(kind, str):
            raise TypeError('Input argument must be str')

        cv = self._cv
        try:
            with cv:
                # Wait for any message of the given type
                while not self._closed and kind not in self._queues:
                    cv.wait()
                if self._closed:
                    raise Exception
                queue = self._queues[kind]
                while not self._closed and not queue:
                    cv.wait()
                if self._closed:
                    raise Exception
                # Consume one message of the given type from the queue
                return queue.popleft()
        except:
            raise ConnectionError('Failed to read message')







######## class SocketMessageWriter ########


class SocketMessageWriter:
    def __init__(self, conn):
        self._conn = conn
        self._lock = RLock()  # Only one thread can write to the socket at a time


    def writemsg(self, kind, message):
        # Validate & parse input arguments
        if not isinstance(kind, str):
            raise TypeError('kind must be a str instance')
        if not isinstance(message, (Mapping, SimpleNamespace)):
            raise TypeError('message must be a mapping or simple namespace object')

        if isinstance(message, SimpleNamespace):
            message = message.__dict__
        elif not isinstance(message, dict):
            message = dict(message)

        s = self._conn
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
        except Exception as e:
            print(e)
            raise ConnectionError('Failed to write message')
