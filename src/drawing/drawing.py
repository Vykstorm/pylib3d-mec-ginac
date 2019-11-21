'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''


from lib3d_mec_ginac_ext import Matrix
from vtk import vtkProp, vtkMatrix4x4, vtkActor
import numpy as np
from math import radians
from itertools import chain
from operator import methodcaller
from .transform import Transform
from .object import VtkObjectWrapper
from .geometry import Geometry, Sphere, Cylinder, Cone
from .scene import Scene
from .color import Color




class Drawing3D(VtkObjectWrapper):
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    def __init__(self, geometry=None):
        if geometry is not None and not isinstance(geometry, Geometry):
            raise TypeError('geometry must be an instance of the class Geometry')

        actor = vtkActor()
        super().__init__(actor)

        # Initialize internal fields
        self._transform = Transform.identity()
        self._transform_evaluated = np.eye(4).astype(np.float64)
        self._geometry = geometry
        self._color = Color()

        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())

        # Set default properties for the actor
        actor.VisibilityOn()
        actor.GetProperty().SetColor(*self._color.rgb)
        actor.GetProperty().SetOpacity(self._color.a)


        # Add event handlers & child objects
        self.add_event_handler(self._on_object_entered, 'object_entered')
        self._color.add_event_handler(self._on_color_changed, 'changed')
        if geometry is not None:
            self.add_child(geometry)
        self.add_child(self._color)



    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if self == source:
            # This drawing was added to another drawing or to the viewers
            self._update()
        elif isinstance(source, Geometry):
            # A geometry object was attached to this drawing object
            with self:
                self.get_handler().SetMapper(source.get_handler())



    def _on_color_changed(self, *args, **kwargs):
        # Drawing object color changed
        actor = self.get_handler()
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
        Get the geometry associated to this drawing object if any. False otherwise
        :rtype: Geometry

        '''
        with self:
            return self._geometry



    def set_geometry(self, geometry):
        '''set_geometry(geometry: Geometry)
        Change the geometry associated to this drawing object
        '''
        with self:
            if self._geometry is not None:
                self.remove_child(self._geometry)
            self._geometry = geometry
            self.add_child(geometry)



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



    def add_transform(self, transform):
        '''
        Add a new transformation to this drawing object
        '''
        if not isinstance(transform, Transform):
            raise TypeError('Input argument must be a Transform instance')
        with self:
            self.set_transform(transform.concatenate(self._transform))



    def rotate(self, *args, **kwargs):
        '''rotate(...)
        Add a new rotation transformation to this drawing object
        '''
        self.add_transform(Transform.rotate(*args, **kwargs))



    def rotate_over_axis(self, *args, **kwargs):
        '''rotate_over_axis(...)
        Add a new rotation tranformation (over the given axis) to this drawing object
        '''
        self.add_transform(Transform.rotation_over_axis(*args, **kwargs))



    def xrotate(self, *args, **kwargs):
        '''xrotate(...)
        Add a new rotation tranformation (over the x axis) to this drawing object
        '''
        self.add_transform(Transform.xrotation(*args, **kwargs))



    def yrotate(self, *args, **kwargs):
        '''yrotate(...)
        Add a new rotation tranformation (over the y axis) to this drawing object
        '''
        self.add_transform(Transform.yrotation(*args, **kwargs))



    def zrotate(self, *args, **kwargs):
        '''zrotate(...)
        Add a new rotation tranformation (over the z axis) to this drawing object
        '''
        self.add_transform(Transform.zrotation(*args, **kwargs))



    def scale(self, *args, **kwargs):
        '''scale(...)
        Add a new scale transformation to this drawing object

        '''
        self.add_transform(Transform.scale(*args, **kwargs))



    def translate(self, *args, **kwargs):
        '''translate(...)
        Add a new translation transformation to this drawing object
        '''
        self.add_transform(Transform.translation(*args, **kwargs))



    def rotate_to_dir(self, *args, **kwargs):
        '''rotate_to_dir(...)
        Add a new rotation transformation (to vector direction) to this drawing object
        '''
        self.add_transform(Transform.rotation_from_dir(*args, **kwargs))







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
                matrix = self.get_parent()._transform_evaluated @ matrix

            self._transform_evaluated = matrix

            # Change the vtk user matrix of the actor associated to this drawing
            self.get_handler().GetUserMatrix().DeepCopy(tuple(map(float, matrix.flat)))



    def show(self):
        '''show()
        Toogle visibility on for this drawing object (and all child drawings)
        '''
        with self:
            actors = map(methodcaller('get_handler'), chain([self], self.get_predecessors(Drawing3D)))
            for actor in actors:
                actor.VisibilityOn()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object (and all child drawings)
        '''
        with self:
            actors = map(methodcaller('get_handler'), chain([self], self.get_predecessors(Drawing3D)))
            for actor in actors:
                actor.VisibilityOff()
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


    @property
    def geometry(self):
        return self.get_geometry()

    @geometry.setter
    def geometry(self, x):
        self.set_geometry(x)







class PointDrawing(Drawing3D):
    def __init__(self, radius=0.06, resolution=15, color=(1, 1, 1)):
        super().__init__(
            Sphere(radius=radius, resolution=resolution)
        )
        self.set_color(color)



class VectorDrawing(Drawing3D):
    def __init__(self,
        shaft_radius=0.03, tip_radius=0.1, origin_radius=0.04,
        shaft_resolution=10, tip_resolution=15, origin_resolution=15,
        shaft_color=(1, 1, 1), tip_color=(1, 1, 0), origin_color=(1, 1, 1)):
        super().__init__()

        shaft_size = 0.8
        tip_size = 1 - shaft_size
        shaft = Drawing3D(
            Cylinder(
                radius=shaft_radius, resolution=shaft_resolution, height=shaft_size,
                center=(0, shaft_size/2, 0)
            )
        )
        tip = Drawing3D(
            Cone(
                radius=tip_radius, resolution=tip_resolution, height=tip_size,
                direction=(0, 1, 0), center=(0, shaft_size+tip_size/2, 0)
            )
        )
        origin = PointDrawing(radius=origin_radius, resolution=origin_resolution, color=origin_color)

        # Setup drawings properties
        shaft.set_color(shaft_color)
        tip.set_color(tip_color)

        # Add child drawings
        self.add_child(shaft)
        self.add_child(tip)
        self.add_child(origin)

        # Setup transformations
        shaft.zrotate(radians(-90))
        tip.zrotate(radians(-90))

        # Initialize internal fields
        self.shaft, self.tip = shaft, tip





class FrameDrawing(Drawing3D):
    def __init__(self,
        axis_shaft_radius=0.03, axis_tip_radius=0.1, origin_radius=0.06,
        axis_shaft_resolution=10, axis_tip_resolution=15, origin_resolution=15,
        axis_shaft_color=(1, 1, 1), axis_tip_colors=((1, 0, 0), (0, 1, 0), (0, 0, 1)), origin_color=(1, 1, 1)):

        try:
            axis_tip_colors = tuple(axis_tip_colors)
            if len(axis_tip_colors) != 3:
                raise TypeError
        except TypeError:
            raise TypeError('axis_tip_colors must be a list of three colors')


        super().__init__()

        # Create x, y and z axis
        def create_axis(tip_color):
            return VectorDrawing(
                shaft_radius=axis_shaft_radius, tip_radius=axis_tip_radius,
                shaft_resolution=axis_shaft_resolution, tip_resolution=axis_tip_resolution,
                shaft_color=axis_shaft_color, tip_color=tip_color
            )

        x_axis, y_axis, z_axis = map(create_axis, axis_tip_colors)

        # Create origin
        origin = PointDrawing(
            radius=origin_radius, resolution=origin_resolution, color=origin_color
        )


        # Setup transformations
        y_axis.zrotate(radians(90))
        z_axis.yrotate(radians(-90))

        # Add child drawings
        self.add_child(x_axis)
        self.add_child(y_axis)
        self.add_child(z_axis)
        self.add_child(origin)

        # Initialize internal fields
        self.x_axis, self.y_axis, self.z_axis = x_axis, y_axis, z_axis
        self.origin = origin
