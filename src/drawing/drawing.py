'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4, vtkActor
import numpy as np
from .transform import Transform
from .object import Object
from .geometry import Geometry, Sphere
from .scene import Scene
from .color import Color


class Drawing3D(Object):
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    def __init__(self, geometry=None):
        if geometry is not None and not isinstance(geometry, Geometry):
            raise TypeError('geometry must be an instance of the class Geometry')
        if geometry is None:
            geometry = Sphere()

        super().__init__()

        actor = vtkActor()

        # Initialize internal fields
        self._transform = Transform.identity()
        self._transform_evaluated = np.eye(4).astype(np.float64)
        self._geometry = geometry
        self._actor = actor
        self._color = Color()

        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())

        # Set default properties for the actor
        actor.VisibilityOn()
        actor.GetProperty().SetColor(*self._color.rgb)
        actor.GetProperty().SetOpacity(self._color.a)


        # Add event handlers & child objects
        self.add_event_handler(self._on_object_entered, 'object_entered')
        self._color.add_event_handler(self._on_color_changed, 'color_changed')
        self.add_child(self._geometry)
        self.add_child(self._color)



    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if self == source:
            self._update()
        elif isinstance(source, Geometry):
            with self:
                self._actor.SetMapper(source.get_mapper())


    def _on_color_changed(self, *args, **kwargs):
        actor = self._actor
        with self:
            actor.GetProperty().SetColor(*self._color.rgb)
            actor.GetProperty().SetOpacity(self._color.a)


    def get_scene(self):
        '''get_scene() -> Scene
        Get the scene attached to this drawing object if any. None otherwise
        '''
        return self.get_ancestor(Scene)



    def get_geometry(self):
        '''get_geometry() -> Geometry
        Get the geometry associated to this drawing object
        :rtype: vtkProp

        '''
        with self:
            return self._geometry



    def set_geometry(self, geometry):
        '''set_geometry(geometry: Geometry)
        Change the geometry associated to this drawing object
        '''
        with self:
            self.remove_child(self._geometry)
            self._geometry = geometry
            self.add_child(geometry)


    def get_actor(self):
        '''get_actor() -> vtkActor
        Get the VTK actor associated to this drawing object
        :rtype: vtkActor

        '''
        return self._actor



    def get_transform(self):
        '''get_transform() -> Transform
        Get the transformation of the drawing object
        '''
        with self:
            return self._transform



    def set_transform(self, transform):
        '''set_transform(transform: Transform)
        Set the transformation of this drawing object

        :type transform: Transform

        '''
        if not isinstance(transform, Transform):
            raise TypeError('Input argument must be a Transform object')
        with self:
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
        with self:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.rotate(*args, **kwargs)))



    def scale(self, *args, **kwargs):
        '''scale(...)
        Add a new scale transformation to this drawing object

        '''
        with self:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.scale(*args, **kwargs)))



    def translate(self, *args, **kwargs):
        '''translate(...)
        Add a new translation transformation to this drawing object
        '''
        with self:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.translation(*args, **kwargs)))



    def rotate_to_dir(self, *args, **kwargs):
        '''rotate_to_dir(...)
        Add a new rotation transformation (to vector direction) to this drawing object
        '''
        with self:
            # Change drawing transformation
            self.set_transform(self._transform.concatenate(Transform.rotation_from_dir(*args, **kwargs)))






    def _update(self):
        with self:
            # Update this drawing transformation matrix
            self._update_transform()
            # Update child drawings
            self._update_subdrawings()



    def _update_subdrawings(self):
        with self:
            for child in self.get_children(kind=Drawing3D):
                child._update()



    def _update_transform(self):
        # Update transformation
        with self:
            scene = self.get_scene()
            if scene is None:
                # This drawing object is not attached to any scene yet
                return

            # Compute transformation numerically for this drawing
            matrix = self._transform.evaluate(scene._system)

            # Concatenate transformation of the parent drawing if any
            if self.has_parent() and isinstance(self.get_parent(), Drawing3D):
                matrix = self.get_parent()._transformation_evaluated @ matrix

            self._transform_evaluated = matrix

            # Change the vtk user matrix of the actor associated to this drawing
            self._actor.GetUserMatrix().DeepCopy(tuple(map(float, matrix.flat)))



    def show(self):
        '''show()
        Toogle visibility on for this drawing object
        '''
        with self:
            # Toggle visibility on
            self._actor.VisibilityOn()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
        with self:
            # Toggle visibility off
            self._actor.VisibilityOff()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')




    def get_color(self):
        '''get_color() -> Color
        Get the color of this drawing object
        :rtype: Color

        '''
        return self._color


    def set_color(self, *args):
        '''set_color(...)
        Change the color of this drawing object
        '''
        self._color.set(*args)




    @property
    def transform(self):
        '''
        Property that can be used to get/set the transformation of this drawing object

        :rtype: Transform

        .. seealso:: :func:`get_transform` :func:`set_transform`

        '''
        return self.get_transform()


    @transform.setter
    def transform(self, x):
        self.set_transform(x)


    @property
    def color(self):
        '''
        Property that can be used to get/set the color of this drawing object

        :rtype: Color

        .. seealso:: :func:`get_color` :func:`set_color`
        '''
        return self.get_color()

    @color.setter
    def color(self, args):
        self.set_color(*args)
