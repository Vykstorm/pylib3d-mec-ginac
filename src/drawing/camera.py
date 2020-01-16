'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Vector, Vector2
'''


######## Imports ########

from .vtkobjectwrapper import VtkObjectWrapper
from .vector import Vector3


######## class Camera ########

class Camera( VtkObjectWrapper ):

    ######## Constructor ########

    def __init__(self, handler):
        super().__init__(handler)
        self._position = Vector3(7, 7, 7)
        self._focal_point = Vector3(0, 0, 0)
        self.add_child(self._position)
        self.add_child(self._focal_point)


        # Update camera position
        self._update()

        # Add event handler
        self._position.add_event_handler(self._on_position_changed, 'changed')
        self._focal_point.add_event_handler(self._on_focal_point_changed, 'changed')


    ######## Event handlers ########

    def _on_position_changed(self, *args, **kwargs):
        self._update_position()

    def _on_focal_point_changed(self, *args, **kwargs):
        self._update_focal_point()

    def _update_position(self):
        self.get_handler().SetPosition(*self._position)

    def _update_focal_point(self):
        self.get_handler().SetFocalPoint(*self._focal_point)

    def _update(self):
        self._update_position()
        self._update_focal_point()



    ######## Getters ########

    def get_position(self):
        return self._position

    def get_focal_point(self):
        return self._focal_point



    ######## Setters ########

    def set_position(self, *args):
        self._position.set(*args)

    def set_focal_point(self, *args):
        self._focal_point.set(*args)




    ######## Properties ########

    @property
    def position(self):
        return self.get_position()

    @position.setter
    def position(self, values):
        self.set_position(values)

    @property
    def focal_point(self):
        return self.get_focal_point()

    @focal_point.setter
    def focal_point(self, values):
        self.set_focal_point(values)
