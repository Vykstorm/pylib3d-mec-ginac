'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Client
'''




######## Imports ########


# From other modules
from ..utils.networking import Socket




######## class Client ########

class Client:
    def __init__(self, address):
        super().__init__()
        self._conn = Socket.connect_to(address)



    def autocomplete(self, text):
        conn = self._conn
        # Send autocomplete request to the server
        conn.writemsg('autocomplete', dict(text=text))
        # Read the response
        response = conn.readmsg('autocomplete-response')
        return response.results



    def exec(self, source, filename='<input>', mode='single'):
        conn = self._conn
        # Send the source code, filename and symbol to the server
        conn.writemsg('exec', dict(source=source, filename=filename, mode=mode))
        # Read the response
        return conn.readmsg('exec-response')
