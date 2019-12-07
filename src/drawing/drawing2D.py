'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class Drawing2D
'''

######## Imports ########

# Standard imports
from functools import partial, partialmethod

# Imports from other modules
from .drawing import Drawing
from .vector import Vector2

# VTK imports
from vtk import vtkTextActor, vtkCoordinate
from vtk import VTK_TEXT_LEFT, VTK_TEXT_CENTERED, VTK_TEXT_RIGHT, VTK_TEXT_TOP, VTK_TEXT_BOTTOM
from vtk import VTK_ARIAL, VTK_COURIER, VTK_TIMES





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


    def _get_absolute_screen_coords(self, scene):
        assert isinstance(scene, Scene)
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
            scene = self.get_ancestor(Scene)
            if scene is None:
                return
            handler.SetPosition(*self._position._get_absolute_screen_coords(scene))



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










######## class TextDrawing ########

class TextDrawing(Drawing2D):
    '''
    This represents a text which is shown at the screen in 2D
    '''

    ######## Constructor ########

    def __init__(self, text='', position=(0, 0), color=(0, 0, 0),
        font_size=20, font_family='courier', bold=False, italic=False):
        actor = vtkTextActor()
        super().__init__(actor, position)

        # Set default actor properties
        self._color.set(color)
        actor.SetInput(text)
        text_prop = actor.GetTextProperty()
        text_prop.SetJustificationToLeft()
        text_prop.SetVerticalJustificationToBottom()
        text_prop.SetFontFamilyToCourier()

        self.set_font_size(font_size)
        self.set_font_family(font_family)
        self.set_bold(bold)
        self.set_italic(italic)



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


    def get_horizontal_justification(self):
        '''get_horizontal_justification() -> str
        Get the current horizontal justification of the text

        :return: 'left', 'center' or 'right'

        '''
        with self:
            return {VTK_TEXT_LEFT: 'left', VTK_TEXT_CENTERED: 'center', VTK_TEXT_RIGHT: 'right'}.get(self.get_handler().GetTextProperty().GetJustification())



    def get_vertical_justification(self):
        '''get_vertical_justification() -> str
        Get the current vertical justification of the text

        :return: 'bottom', 'center', 'top'
        '''
        with self:
            return {VTK_TEXT_BOTTOM: 'bottom', VTK_TEXT_CENTERED: 'center', VTK_TEXT_TOP: 'top'}.get(self.get_handler().GetTextProperty().GetVerticalJustification())





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


    def set_horizontal_justification(self, mode):
        if not isinstance(mode, str):
            raise TypeError('Input argument must be string')
        if mode not in ('left', 'center', 'right'):
            raise ValueError('horizontal justification must be "left", "center" or "right"')
        with self:
            self.get_handler().GetTextProperty().SetJustification({'left': VTK_TEXT_LEFT, 'center': VTK_TEXT_CENTERED, 'right': VTK_TEXT_RIGHT}.get(mode))
            self.fire_event('horizontal_justification_changed')


    set_horizontal_justification_to_left = partialmethod(set_horizontal_justification, 'left')
    set_horizontal_justification_to_center = partialmethod(set_horizontal_justification, 'center')
    set_horizontal_justification_to_right = partialmethod(set_horizontal_justification, 'right')



    def set_vertical_justification(self, mode):
        if not isinstance(mode, str):
            raise TypeError('Input argument must be string')
        if mode not in ('bottom', 'center', 'top'):
            raise ValueError('vertical justification must be "left", "center" or "right"')
        with self:
            self.get_handler().GetTextProperty().SetVerticalJustification({'bottom': VTK_TEXT_BOTTOM, 'center': VTK_TEXT_CENTERED, 'top': VTK_TEXT_TOP}.get(mode))
            self.fire_event('vertical_justification_changed')


    set_vertical_justification_to_bottom = partialmethod(set_vertical_justification, 'bottom')
    set_vertical_justification_to_center = partialmethod(set_vertical_justification, 'center')
    set_vertical_justification_to_top = partialmethod(set_vertical_justification, 'top')





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
    def horizontal_justification(self):
        '''
        Property that can be used to set/get the horizontal justification of the displayed text of
        this drawing.

        .. seealso:: :func::`get_horizontal_justification` :func:`set_horizontal_justification`
        '''
        return self.get_horizontal_justification()

    @horizontal_justification.setter
    def horizontal_justification(self, value):
        self.set_horizontal_justification(value)



    @property
    def vertical_justification(self):
        '''
        Property that can be used to set/get the horizontal justification of the displayed text of
        this drawing.

        .. seealso:: :func::`get_vertical_justification` :func:`set_vertical_justification`
        '''
        return self.get_vertical_justification()

    @vertical_justification.setter
    def vertical_justification(self, value):
        self.set_vertical_justification(value)




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
