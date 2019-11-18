'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Geometry and all its subclasses
'''

from threading import RLock


class Geometry:
    def __init__(self, actor):
        self._actor = actor
        self._lock = RLock()
        


    def get_actor(self):
        pass
