'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4, vtkActor
import numpy as np
from threading import RLock
from vtk import vtkSphereSource, vtkPolyDataMapper, vtkActor

from .transform import Transform
from .object import Object


class Drawing3D(Object):
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    def __init__(self, viewer, system, actor=None):
        super().__init__()

        # Validate & parse input arguments
        if actor is None:
            source = vtkSphereSource()
            mapper = vtkPolyDataMapper()
            mapper.SetInputConnection(source.GetOutputPort())
            actor = vtkActor()
            actor.SetMapper(mapper)



        # Initialize internal fields
        self._transform = Transform.identity()
        self._transform_evaluated = np.eye(4).astype(np.float64)
        self._viewer, self._system = viewer, system
        self._actor = None
        self._set_actor(actor)



    def get_actor(self):
        '''get_actor() -> vtkProp
        Get the vtk actor associated to this drawing object

        :rtype: vtkProp

        '''
        with self.lock:
            return self._actor



    def _set_actor(self, actor):
        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())
        # Set default properties for the actor
        actor.VisibilityOn()

        with self.lock:
            self._actor = actor



    def set_actor(self, actor):
        '''set_actor(actor: vtkProp)
        Change the vtk actor attached to this drawing object
        '''
        with self.lock:
            self._viewer.remove_actor(self._actor)
            self._set_actor(actor)
            # Update this drawing
            self._update()

        # Redraw
        self._viewer._redraw()




    def add_child(self, child):
        '''add_child(child: Drawing3D)
        Add a new child drawing object
        '''
        super().add_child(child)

        # Update child drawing
        child._update()

        # Redraw
        self._viewer._redraw()



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

        # Redraw
        self._viewer._redraw()


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
            self._transform = self._transform.concatenate(Transform.rotate(*args, **kwargs))
            # Update drawing
            self._update()
        # Redraw
        self._viewer._redraw()


    def scale(self, *args, **kwargs):
        '''scale(...)
        Add a new scale transformation to this drawing object

        '''
        with self.lock:
            # Change drawing transformation
            self._transform = self._transform.concatenate(Transform.scale(*args, **kwargs))
            # Update drawing
            self._update()
        # Redraw
        self._viewer._redraw()


    def translate(self, *args, **kwargs):
        '''translate(...)
        Add a new translation transformation to this drawing object
        '''
        with self.lock:
            # Change drawing transformation
            self._transform = self._transform.concatenate(Transform.translation(*args, **kwargs))
            # Update drawing
            self._update()
        # Redraw
        self._viewer._redraw()


    def rotate_to_dir(self, *args, **kwargs):
        '''rotate_to_dir(...)
        Add a new rotation transformation (to vector direction) to this drawing object
        '''
        with self.lock:
            # Change drawing transformation
            self._transform = self._transform.concatenate(Transform.rotation_from_dir(*args, **kwargs))
            # Update drawing
            self._update()
        # Redraw
        self._viewer._redraw()




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
            # Compute affine transformation numerically for this drawing
            matrix = self._transform.evaluate(self._system)

            # Concatenate transformation of the parent drawing if any
            if self.has_parent() and isinstance(self.get_parent(), Drawing3D):
                matrix = self.get_parent()._transformation_evaluated @ matrix

            self._transform_evaluated = matrix
            self._actor.GetUserMatrix().DeepCopy(tuple(map(float, matrix.flat)))



    def show(self):
        '''show()
        Toogle visibility on for this drawing object
        '''
        # Toggle visibility on
        with self.lock:
            self._actor.VisibilityOn()

        # Redraw scene
        self._viewer._redraw()



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
        # Toggle visibility off
        with self.lock:
            self._actor.VisibilityOff()

        # Redraw scene
        self._viewer._redraw()



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
