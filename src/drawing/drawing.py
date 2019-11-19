'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4, vtkActor
import numpy as np
from threading import RLock
from .transform import Transform
from .object import Object
from .geometry import Geometry


class Drawing3D(Object):
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    def __init__(self, geometry):
        super().__init__()

        # Initialize internal fields
        self._transform = Transform.identity()
        self._transform_evaluated = np.eye(4).astype(np.float64)
        self._system = None
        self._geometry = geometry

        self.add_event_handler(self._on_object_entered, 'object_entered')
        self.add_child(self._geometry)



    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if self == source or isinstance(source, Geometry):
            self._update()



    def get_geometry(self):
        '''get_geometry() -> Geometry
        Get the geomtry associated to this drawing object
        :rtype: vtkProp

        '''
        with self.lock:
            return self._geometry



    def set_geometry(self, geometry):
        '''set_geometry(geometry: Geometry)
        Change the geometry associated to this drawing object
        '''
        with self.lock:
            self.remove_child(self._geometry)
            self._geometry = geometry
            self.add_child(geometry)



    def get_transform(self):
        '''get_transform() -> Transform
        Get the transformation of the drawing object
        '''
        with self.lock:
            return self._transform



    def set_transform(self, transform):
        '''set_transform(transform: Transform)
        Set the transformation of this drawing object

        :type transform: Transform

        '''
        if not isinstance(transform, Transform):
            raise TypeError('Input argument must be a Transform object')
        with self.lock:
            # Change drawing transformation
            self._transform = transform
            # Update drawing
            self._update()
            # Fire 'transform_changed' event
            self.fire_event('transform_changed')



    def clear_transform(self):
        '''clear_transform()
        Clear the transformation of this drawing object
        '''
        self.set_transform(Transform.identity())



    def rotate(self, *args, **kwargs):
        '''rotate(...)
        Add a new rotation transformation to this drawing object
        '''
        with self.lock:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.rotate(*args, **kwargs)))



    def scale(self, *args, **kwargs):
        '''scale(...)
        Add a new scale transformation to this drawing object

        '''
        with self.lock:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.scale(*args, **kwargs)))



    def translate(self, *args, **kwargs):
        '''translate(...)
        Add a new translation transformation to this drawing object
        '''
        with self.lock:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.translation(*args, **kwargs)))



    def rotate_to_dir(self, *args, **kwargs):
        '''rotate_to_dir(...)
        Add a new rotation transformation (to vector direction) to this drawing object
        '''
        with self.lock:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.rotation_from_dir(*args, **kwargs)))



    def _update(self):
        with self.lock:
            # Update this drawing transformation matrix
            self._update_transform()
            # Update child drawings
            self._update_subdrawings()



    def _update_subdrawings(self):
        with self.lock:
            for child in self.get_children(kind=Drawing3D):
                child._update()



    def _update_transform(self):
        # Update transformation
        with self.lock:
            if self._system is None:
                return

            # Compute transformation numerically for this drawing
            matrix = self._transform.evaluate(self._system)

            # Concatenate transformation of the parent drawing if any
            if self.has_parent() and isinstance(self.get_parent(), Drawing3D):
                matrix = self.get_parent()._transformation_evaluated @ matrix

            self._transform_evaluated = matrix
            self._geometry.get_actor().GetUserMatrix().DeepCopy(tuple(map(float, matrix.flat)))



    def show(self):
        '''show()
        Toogle visibility on for this drawing object
        '''
        with self.lock:
            # Toggle visibility on
            self._geometry.get_actor().VisibilityOn()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')




    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
        with self.lock:
            # Toggle visibility off
            self._geometry.get_actor().VisibilityOff()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')



    @property
    def transform(self):
        '''
        Property that can be used to get/set the transformation of this drawing object

        :rtype: Transform

        '''
        return self.get_transform()


    @transform.setter
    def transform(self, x):
        self.set_transform(x)
