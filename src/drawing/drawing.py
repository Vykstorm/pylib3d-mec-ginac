'''
Author: Víctor Ruiz Gómez
Description:
This script implements the class Drawing3D
'''

######## Import statements ########


# Standard imports
from math import radians
from itertools import chain
from operator import methodcaller
from functools import partial, partialmethod

# Imports from other modules
from lib3d_mec_ginac_ext import Matrix
from .transform import Transform
from .vtkobjectwrapper import VtkObjectWrapper
from .geometry import Geometry, Sphere, Cylinder, Cone
from .color import Color
from .vector import Vector2


# Third party libraries
from vtk import vtkProp, vtkMatrix4x4, vtkActor, vtkTextActor
from vtk import vtkCoordinate
from vtk import VTK_TEXT_LEFT, VTK_TEXT_CENTERED, VTK_TEXT_RIGHT, VTK_ARIAL, VTK_COURIER, VTK_TIMES
import numpy as np



######## class Drawing ########

class Drawing(VtkObjectWrapper):
    '''
    Represents any kind of renderable entity
    '''

    ######## Constructor ########


    def __init__(self, actor):
        # Initialize super instance
        super().__init__(actor)

        # Initialize internal fields
        self._color = Color()

        # Set default properties for the actor
        actor.VisibilityOn() # Turn on drawing visibility
        self._update_color() # Initialize color

        # Add event handlers
        self.add_child(self._color)
        self._color.add_event_handler(self._on_color_changed, 'changed')
        self.add_event_handler(self._on_object_entered, 'object_entered')




    ######## Event handlers ########


    def _on_color_changed(self, *args, **kwargs):
        # This method is invoked when drawing color changed
        self._update_color()


    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if source == self:
            # This drawing is added to the scene or another
            # drawing as a child object
            self._update()





    ######## Updating ########


    def _update_color(self):
        # This method updates the color of the underline vtk actor
        actor = self.get_handler()
        actor.GetProperty().SetColor(*self._color.rgb)
        actor.GetProperty().SetOpacity(self._color.a)


    def _update_subdrawings(self):
        # This method is invoked to update subdrawings
        with self:
            for child in self.get_children(kind=Drawing):
                child._update()


    def _update(self):
        # Method called to update this drawing
        self._update_subdrawings()



    ######## Getters ########


    def get_color(self):
        '''get_color() -> Color
        Get the color of this drawing object
        :rtype: Color

        '''
        return self._color


    def get_scene(self):
        '''get_scene() -> Scene
        Get the scene attached to this drawing object if any. None otherwise
        '''
        return self.get_ancestor(Scene)




    ######## Setters ########


    def set_color(self, *args):
        '''set_color(...)
        Change the color of this drawing object
        '''
        self._color.set(*args)



    def show(self):
        '''show()
        Toogle visibility on for this drawing object
        '''
        with self:
            self.get_handler().VisibilityOn()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
        with self:
            self.get_handler().VisibilityOff()
            # Fire 'visibility_changed' event
            self.fire_event('visibility_changed')




    ######## Properties ########


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
        self.set_color(args)











######## class ScreenPoint ########

class ScreenPoint(Vector2):
    '''
    This represents a point in the screen. Coordinates are normalized (Starting from
    0, 0 to represent the bottom-left corner of the screen and 1, 1 for the top right)

    You can also define a coordinate relative to any of the corners of the screen using
    the method ``set_relative_to``

    .. seealso:: :func:`set_relative_to`

    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._x_coord_screen_ref, self._y_coord_screen_ref = 'left', 'bottom'
        coord = vtkCoordinate()
        coord.SetCoordinateSystemToNormalizedDisplay()
        self._coord = coord


    def _get_absolute_screen_coords(self):
        scene = self.get_ancestor(Scene)
        if scene is None:
            return
        renderer = scene._renderer

        with self:
            x, y = self._values
            x_ref, y_ref = self._x_coord_screen_ref, self._y_coord_screen_ref
            coord = self._coord
            if x_ref != 'left':
                x += 0.5 if x_ref == 'center' else 1
            if y_ref != 'bottom':
                y += 0.5 if y_ref == 'center' else 1

            coord.SetValue(x, y)
            return coord.GetComputedDisplayValue(renderer)



    def set_relative_to(self, s):
        if not isinstance(s, str):
            raise TypeError('Input argument must be a string')
        try:
            tokens =  s.lower().replace('_', '-').split('-')
            if len(tokens) != 2 and (len(tokens) != 1 or tokens[0] != 'center'):
                raise ValueError
            if len(tokens) == 2:
                y, x = tokens
                if x not in ('left', 'center', 'right'):
                    raise ValueError
                if y not in ('bottom', 'center', 'top'):
                    raise ValueError
            else:
                y, x = 'center', 'center'
        except ValueError:
            raise ValueError(f'Invalid argument value: "{s}"')

        with self:
            self._x_coord_screen_ref, self._y_coord_screen_ref = x, y







######## class Drawing2D ########

class Drawing2D(Drawing):
    '''
    An instance of this class represents any 2D renderable entity.
    '''


    ######## Constructor ########

    def __init__(self, actor, position=(0, 0)):
        super().__init__(actor)

        # Initialize internal fields
        self._position = ScreenPoint(position)
        self.add_child(self._position)

        # Add event handlers
        self._position.add_event_handler(self._on_position_changed, 'changed')
        self._position.add_event_handler(self._on_position_changed, 'object_entered')



    ######## Event handlers ########


    def _on_position_changed(self, *args, **kwargs):
        # This is invoked when any of the coordinates of the drawing`s position is changed
        self._update_position()



    ######## Updating ########


    def _update(self):
        # This is called when this drawing must be updated
        self._update_position()
        super()._update()


    def _update_position(self):
        # This is called when the position of this 2D drawing must be updated on VTK
        with self:
            handler = self.get_handler()
            handler.SetPosition(*self._position._get_absolute_screen_coords())



    ######## Getters ########


    def get_position(self):
        '''get_position() -> Vector2
        Get the current position of this 2D drawing

        :rtype: Vector2

        '''
        return self._position



    ######## Setters ########


    def set_position(self, *args):
        '''set_position(...)
        Change the position of this 2D drawing
        '''
        return self._position.set(*args)



    def set_position_relative_to(self, *args, **kwargs):
        '''position_relative_to(x: str, y: str)
        Set the position of this 2D drawing relative to the left, center or right side
        of the viewport for the x coordinate, and to the top, center or bottom for the
        y coordinate.

        The next example shows how to draw text in the middle of the screen:

            :Example:

            >>> drawing = TextDrawing('Hello world!', position=[0, 0])
            >>> drawing.position_relative_to('center')

        The example above shows how to display text at the bottom right side of the screen:

            :Example:

            >>> drawing = TextDrawing('Hello world!', position=[-0.2, 0])
            >>> drawing.position_relative_to('bottom-right')
        '''
        self._position.set_relative_to(*args, **kwargs)


    set_position_relative_to_center = partialmethod(set_position_relative_to, 'center')
    set_position_relative_to_top_left = partialmethod(set_position_relative_to, 'top-left')
    set_position_relative_to_top_right = partialmethod(set_position_relative_to, 'top-right')
    set_position_relative_to_bottom_left = partialmethod(set_position_relative_to, 'bottom-left')
    set_position_relative_to_bottom_right = partialmethod(set_position_relative_to, 'bottom-right')




    ######## Properties ########


    @property
    def position(self):
        return self.get_position()

    @position.setter
    def position(self, args):
        self.set_position(*args)







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

    def __init__(self, radius=0.06, resolution=15, color=(1, 1, 1)):
        super().__init__(
            Sphere(radius=radius, resolution=resolution)
        )
        self.set_color(color)






######## class VectorDrawing ########

class VectorDrawing(Drawing3D):
    '''
    This represents a drawing which can be used to render vectors in the 3D scene.
    It has three subdrawings: The origin of the vector (with a sphere as geometry), the
    shaft (rendered with a cylinder) and the tip (with a cone shape)
    '''

    ######## Constructor ########

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





######## class FrameDrawing ########

class FrameDrawing(Drawing3D):
    '''
    This represents a drawing which can be used to draw frames in a 3D scene.
    It consists of 3 different vectors pointing at each axis in the 3D space.

    .. seealso:: VectorDrawing

    '''
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






######## class TextDrawing ########

class TextDrawing(Drawing2D):
    '''
    This represents a text which is shown at the screen in 2D
    '''

    ######## Constructor ########

    def __init__(self, text='', position=(0, 0), color=(0, 0, 0), font_size=20):
        actor = vtkTextActor()
        super().__init__(actor, position)

        # Set default actor properties
        self._color.set(color)
        actor.SetInput(text)
        text_prop = actor.GetTextProperty()
        text_prop.SetFontSize(font_size)
        text_prop.SetJustificationToLeft()
        text_prop.SetFontFamilyToCourier()



    ######## Updating ########

    def _update_color(self):
        # This method updates the color of the underline vtk actor
        actor = self.get_handler()
        actor.GetTextProperty().SetColor(*self._color.rgb)
        actor.GetTextProperty().SetOpacity(self._color.a)



    ######## Getters ########


    def get_font_size(self):
        '''get_font_size() -> int
        Get the font size for this text drawing

        :rtype: int

        '''
        with self:
            return self.get_handler().GetTextProperty().GetFontSize()


    def get_text(self):
        '''get_text() -> str
        Get the displayed text of this drawing

        :rtype: str

        '''
        with self:
            return self.get_handler().GetInput()


    def get_horizontal_alignment(self):
        '''get_horizontal_alignment() -> str
        Get the current horizontal alignment of the text

        :return: 'left', 'center' or 'right'

        '''
        with self:
            return {VTK_TEXT_LEFT: 'left', VTK_TEXT_CENTERED: 'center', VTK_TEXT_RIGHT: 'right'}.get(self.get_handler().GetTextProperty().GetJustification())


    def get_font_family(self):
        '''get_font_family() -> str
        Get the current font family for the displayed text

        :return: 'arial', 'courier' or 'times'

        '''
        with self:
            return {VTK_ARIAL: 'arial', VTK_COURIER: 'courier', VTK_TIMES: 'times'}.get(self.get_handler().GetTextProperty().GetFontFamily())





    ######## Setters ########


    def set_font_size(self, value):
        '''set_font_size(value: int)
        Change the font size of this text drawing

        :type value: int

        '''
        if not isinstance(value, int) or value <= 0:
            raise TypeError('font size must be an integer greater than zero')

        actor = self.get_handler()
        with self:
            actor.GetTextProperty().SetFontSize(value)
            self.fire_event('font_size_changed')




    def set_text(self, text):
        '''set_text(text: str)
        Change the displayed text of this drawing
        '''
        if not isinstance(text, str):
            raise TypeError('Text must be a string')
        with self:
            self.get_handler().SetInput(text)
            self.fire_event('text_changed')



    def set_italic(self, enabled):
        if not isinstance(enabled, bool):
            raise TypeError('Input argument must be bool')
        with self:
            self.get_handler().GetTextProperty().SetItalic(enabled)
            self.fire_event('italic_changed')



    def set_bold(self, enabled):
        if not isinstance(enabled, bool):
            raise TypeError('Input argument must be bool')
        with self:
            self.get_handler().GetTextProperty().SetBold(enabled)
            self.fire_event('bold_changed')


    italic_on = partialmethod(set_italic, True)
    italic_off = partialmethod(set_italic, False)
    bold_on = partialmethod(set_bold, True)
    bold_off = partialmethod(set_bold, False)


    def set_horizontal_alignment(self, mode):
        if not isinstance(mode, str):
            raise TypeError('Input argument must be string')
        if mode not in ('left', 'center', 'right'):
            raise ValueError('alignment must be "left", "center" or "right"')
        with self:
            self.get_handler().GetTextProperty().SetJustification({'left': VTK_TEXT_LEFT, 'center': VTK_TEXT_CENTERED, 'right': VTK_TEXT_RIGHT}.get(mode))
            self.fire_event('horizontal_alignment_changed')


    def set_font_family(self, family):
        if not isinstance(family, str):
            raise TypeError('Input argument must be string')
        if family not in ('arial', 'courier', 'times'):
            raise ValueError('font family must be "arial", "courier" or "times"')
        with self:
            self.get_handler().GetTextProperty().SetFontFamily({'arial': VTK_ARIAL, 'courier': VTK_COURIER, 'times': VTK_TIMES}.get(family))
            self.fire_event('font_family_changed')




    ######## Properties ########

    @property
    def font_size(self):
        '''
        Property that can be used to set/get the font size of this text drawing

        .. seealso:: :func:`set_font_size`, :func:`get_font_size`

        '''
        return self.get_font_size()


    @font_size.setter
    def font_size(self, value):
        self.set_font_size(value)



    @property
    def text(self):
        '''
        Property that can be used to set/get the displayed text of this drawing

        .. seealso:: :func:`set_text`, :func:`get_text`

        '''
        return self.get_text()

    @text.setter
    def text(self, value):
        self.set_text(value)


    @property
    def horizontal_alignment(self):
        '''
        Property that can be used to set/get the horizontal alignment of the displayed text of
        this drawing.

        .. seealso:: :func::`get_horizontal_alignment` :func:`set_horizontal_alignment`
        '''
        return self.get_horizontal_alignment()

    @horizontal_alignment.setter
    def horizontal_alignment(self, value):
        self.set_horizontal_alignment(value)



    @property
    def font_family(self):
        '''
        Property that can be sued to set/get the fony family for the displayed text.


        .. seealso:: :func:`get_font_family`, :func:`set_font_family`

        '''
        return self.get_font_family()

    @font_family.setter
    def font_family(self, value):
        self.set_font_family(value)




# This import is added here to avoid circular dependencies
from .scene import Scene
