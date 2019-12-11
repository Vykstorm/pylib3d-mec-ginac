'''
Author: Víctor Ruiz Gómez
Description:
This file defines the classes Drawing3D, PointDrawing, VectorDrawing, FrameDrawing
'''

######## Imports ########

# Standard imports
from math import radians
from operator import methodcaller

# Imports from other modules
from .drawing import Drawing
from lib3d_mec_ginac_ext import Matrix
from .transform import Transform
from .geometry import Geometry, Sphere, Cylinder, Cone
from .color import Color

# Imports from third party libraries
from vtk import vtkMatrix4x4, vtkActor
import numpy as np





######## class Drawing3D ########

class Drawing3D(Drawing):
    '''
    An instance of this class represents any 3D renderable entity.
    '''

    ######## Constructor ########

    def __init__(self, geometry=None):
        if geometry is not None and not isinstance(geometry, Geometry):
            raise TypeError('geometry must be an instance of the class Geometry')

        actor = vtkActor()

        self._selected = False
        self._selected_color = Color('red')

        super().__init__(actor)

        # Initialize internal fields
        self._transform = Transform.identity()
        self._transform_evaluated = np.eye(4).astype(np.float64)
        self._geometry = geometry

        # Set default actor properties
        actor.GetProperty().SetColor(*self._color.rgb)
        actor.GetProperty().SetOpacity(self._color.a)

        # Initialize vtk actor user matrix
        actor.SetUserMatrix(vtkMatrix4x4())

        # Add event handlers
        if geometry is not None:
            self.add_child(geometry)
        self.add_event_handler(self._on_selected, 'selected')
        self.add_event_handler(self._on_unselected, 'unselected')
        self._selected_color.add_event_handler(self._on_color_changed, 'changed')



    ######## Event handlers ########


    def _on_object_entered(self, event_type, source, *args, **kwargs):
        super()._on_object_entered(event_type, source, *args, **kwargs)
        if isinstance(source, Geometry):
            # A geometry object was attached to this drawing object
            self.get_handler().SetMapper(source.get_handler())


    def _on_selected(self, event_type, source, *args, **kwargs):
        self._update_color(highlighted=True)
        for drawing in self.get_predecessors(Drawing3D):
            drawing._update_color(highlighted=True)


    def _on_unselected(self, event_type, source, *args, **kwargs):
        self._update_color(highlighted=False)
        for drawing in self.get_predecessors(Drawing3D):
            drawing._update_color(highlighted=False)


    ######## Updating ########


    def _update(self):
        with self:
            # Update this drawing transformation matrix
            self._update_transform()
            super()._update()


    def _update_color(self, highlighted=False):
        # This method updates the color of the underline vtk actor
        if highlighted:
            color = self._color.lerp(self._selected_color, 0.3)
        else:
            color = self._color
        actor = self.get_handler()
        actor.GetProperty().SetColor(*color.rgb)
        actor.GetProperty().SetOpacity(color.a)


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







    ######## Getters ########


    def get_geometry(self):
        '''get_geometry() -> Geometry
        Get the geometry associated to this drawing object if any. False otherwise
        :rtype: Geometry

        '''
        with self:
            return self._geometry


    def get_transform(self):
        '''get_transform() -> Transform
        Get the transformation of the drawing object

        :rtype: Transform

        '''
        with self:
            return self._transform


    def is_selected(self):
        '''is_selected() -> bool
        Is this drawing selected

        :rtype: bool
        '''
        with self:
            return self._selected


    def get_selected_color(self):
        '''get_selected_color() -> Color
        Get the color which is used to paint the drawing when it is selected

        :rtype: Color
        '''
        return self._selected_color



    ######## Setters ########


    def set_geometry(self, geometry):
        '''set_geometry(geometry: Geometry)
        Change the geometry associated to this drawing object
        '''
        with self:
            if self._geometry is not None:
                self.remove_child(self._geometry)
            self._geometry = geometry
            self.add_child(geometry)


    def set_selected_color(self, *args):
        '''set_selected_color(...)
        Change the color of the drawing when it is selected
        '''
        self._selected_color.set(*args)



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
        self.add_transform(Transform.rotation(*args, **kwargs))



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



    def show(self):
        '''show()
        Toogle visibility on for this drawing object (and all child drawings)
        '''
        with self:
            for actor in map(methodcaller('get_handler'), self.get_predecessors(Drawing3D)):
                actor.VisibilityOn()
            super().show()


    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object (and all child drawings)
        '''
        with self:
            for actor in map(methodcaller('get_handler'), self.get_predecessors(Drawing3D)):
                actor.VisibilityOff()
            super().show()


    def select(self):
        '''select()
        Select this drawing
        '''
        with self:
            if not self._selected:
                self._selected = True
                self.fire_event('selected')



    def unselect(self):
        '''unselect()
        Unselect this drawing
        '''
        with self:
            if self._selected:
                self._selected = False
                self.fire_event('unselected')


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
    def geometry(self):
        return self.get_geometry()

    @geometry.setter
    def geometry(self, x):
        self.set_geometry(x)


    @property
    def selected_color(self):
        return self.get_selected_color()

    @selected_color.setter
    def selected_color(self, args):
        self.set_selected_color(args)






######## class PointDrawing ########


class PointDrawing(Drawing3D):
    '''
    This represents a drawing which can be used to render points in the 3D scene.
    The geometry of this drawing is a sphere.
    '''


    ######## Constructor ########

    def __init__(self, point, radius=0.06, resolution=15, color=(1, 1, 1)):
        super().__init__(
            Sphere(radius=radius, resolution=resolution)
        )
        self.set_color(color)
        self._point = point



    ######## Getters ########


    def get_point(self):
        '''get_point() -> Point
        Get the point of this drawing

        :rtype: Point

        '''
        return self._point



    ######## Properties ########


    @property
    def point(self):
        '''
        Only read property that returns the point attached to this drawing

        :rtype: Point

        .. seealso::
            :func:`get_point`

        '''
        return self.get_point()










######## class VectorDrawing ########

class VectorDrawing(Drawing3D):
    '''
    This represents a drawing which can be used to render vectors in the 3D scene.
    It has three subdrawings: The origin of the vector (with a sphere as geometry), the
    shaft (rendered with a cylinder) and the tip (with a cone shape)
    '''

    ######## Constructor ########

    def __init__(self, vector,
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
        origin = PointDrawing(None, radius=origin_radius, resolution=origin_resolution, color=origin_color)

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
        self._shaft, self._tip, self._origin = shaft, tip, origin
        self._vector = vector


    ######## Getters ########


    def get_shaft(self):
        '''get_shaft() -> Cylinder
        Get the shaft geometry of the vector

        :rtype: Cylinder

        '''
        return self._shaft


    def get_tip(self):
        '''get_tip() -> Cone
        Get the tip geometry of the vector

        :rtype: Cylinder

        '''
        return self._tip


    def get_origin(self):
        '''get_origin() -> Sphere
        Get the origin geometry of the vector

        :rtype: Sphere

        '''
        return self._origin


    def get_vector(self):
        '''get_vector() -> Vector3D
        Get the vector associated to this drawing

        :rtype: Vector3D

        '''
        return self._vector




    ######## Properties ########


    @property
    def shaft(self):
        '''
        Read only property that returns the shaft geometry of this vector.

        .. seealso::
            :func:`get_shaft`
        '''
        return self.get_shaft()


    @property
    def tip(self):
        '''
        Read only property that returns the tip geometry of this vector.

        .. seealso::
            :func:`get_tip`
        '''
        return self.get_tip()


    @property
    def vector(self):
        '''
        Read only property that returns the vector associated to this drawing

        .. seealso::
            :func:`get_vector`
        '''
        return self.get_vector()









######## class PositionVectorDrawing ########

class PositionVectorDrawing(VectorDrawing):

    ######## Constructor ########

    def __init__(self, vector, start, end, **kwargs):
        super().__init__(vector, **kwargs)
        self._start, self._end = start, end


    ######## Getters ########


    def get_start_point(self):
        '''get_start_point() -> Point
        Get the start point of the position vector attached to this drawing

        :rtype: Point

        '''
        return self._start


    def get_end_point(self):
        '''get_end_point() -> Point
        Get the end point of the position vector attached to this drawing

        :rtype: Point

        '''
        return self._end



    ######## Properties ########


    @property
    def start_point(self):
        '''
        Read only property that returns the start point of the position vector attached to this drawing

        :rtype: Point

        .. seealso:: :func:`get_start_point`

        '''
        return self.get_start_point()


    @property
    def end_point(self):
        '''
        Read only property that returns the end point of the position vector attached to this drawing.

        :rtype: Point

        .. seealso:: :func:`get_end_point`

        '''
        return self.get_end_point()






######## class VelocityVectorDrawing ########


class VelocityVectorDrawing(VectorDrawing):

    ######## Constructor ########

    def __init__(self, vector, frame, point, **kwargs):
        super().__init__(vector, **kwargs)
        self._frame, self._point = frame, point



    ######## Getters ########

    def get_point(self):
        '''get_point() -> Point
        Get the point of the velocity vector attached to this drawing.

        :rtype: Point

        '''
        return self._point


    def get_frame(self):
        '''get_frame() -> Frame
        Get the frame of the velocity vector attached to this drawing.

        :rtype: Frame

        '''
        return self._frame




    ######## Properties ########


    @property
    def point(self):
        '''
        Read only property that returns the point of the velocity vector attached to this drawing.

        :rtype: Point

        .. seealso:: :func:`get_point`

        '''
        return self.get_point()


    @property
    def frame(self):
        '''
        Read only property that returns the frame of the velocity vector attached to this drawing.

        :rtype: Frame

        .. seealso:: :func:`get_frame`

        '''
        return self.get_frame()







######## class FrameDrawing ########

class FrameDrawing(Drawing3D):
    '''
    This represents a drawing which can be used to draw frames in a 3D scene.
    It consists of 3 different vectors pointing at each axis in the 3D space.

    .. seealso:: VectorDrawing

    '''

    ######## Constructor ########

    def __init__(self, frame,
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
            return VectorDrawing(None,
                shaft_radius=axis_shaft_radius, tip_radius=axis_tip_radius,
                shaft_resolution=axis_shaft_resolution, tip_resolution=axis_tip_resolution,
                shaft_color=axis_shaft_color, tip_color=tip_color
            )

        x_axis, y_axis, z_axis = map(create_axis, axis_tip_colors)

        # Create origin
        origin = PointDrawing(None,
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
        self._x_axis, self._y_axis, self._z_axis = x_axis, y_axis, z_axis
        self._origin = origin
        self._frame = frame



    ######## Getters ########


    def get_frame(self):
        '''get_frame() -> Frame
        Get the frame attached to this drawing

        :rtype: Frame

        '''
        return self._frame




    ######## Properties ########

    @property
    def frame(self):
        '''
        Read only property that returns the frame attached to this drawings

        :rtype: Frame

        '''
        return self.get_frame()






######## class SolidDrawing ########


class SolidDrawing(Drawing3D):

    ######## Constructor ########

    def __init__(self, solid):
        super().__init__()
        self._solid = solid


    ######## Getters ########

    def get_solid(self):
        '''get_solid() -> Solid
        Get the solid attached to this drawing

        :rtype: Solid

        '''
        return self._solid


    ######## Properties ########


    @property
    def solid(self):
        '''
        Read only property that returns the solid attached to this drawing

        :rtype: Solid

        .. seealso:: :func:`get_solid`

        '''
        return self._solid
