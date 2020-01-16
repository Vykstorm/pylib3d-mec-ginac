'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Vector, Vector2
'''


######## Imports ########

from .vtkobjectwrapper import VtkObjectWrapper
from .vector import Vector3


######## class Camera ########

class Camera( VtkObjectWrapper ):
    def __init__(self, handler):
        super().__init__(handler)
        self._position = Vector3(7, 7, 7)
        self.add_child(self._position)

        # Update camera position
        self._update_position()

        # Add event handler
        self._position.add_event_handler(self._on_position_changed, 'changed')


    def _on_position_changed(self, *args, **kwargs):
        self._update_position()

    def _update_position(self):
        self.get_handler().SetPosition(*self._position)

    def set_position(self, *args):
        self._position.set(*args)

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, values):
        self.set_position(values)
