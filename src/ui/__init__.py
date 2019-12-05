'''
Author: Víctor Ruiz Gómez
Description: Public API for the submodule ui
'''


# The next variable will contain all public API methods & classes
__all__ = [
    'Client', 'ConsoleClient', 'JupyterClient'
]

# Import all the class & functions of the public API
from .client import Client
from .console import ConsoleClient
from .jupyter import JupyterClient
