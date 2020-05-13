'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class Drawing
'''

######## Import statements ########


# Imports from other modules
from .vtkobjectwrapper import VtkObjectWrapper
from .color import Color




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


    def is_visible(self):
        '''is_visible() -> bool
        Returns True if this drawing is visible, False otherwise
        '''
        return self.get_handler().GetVisibility()



    def is_hidden(self):
        '''is_hidden() -> bool
        Returns True if this drawing is hidden, False otherwise
        '''
        return not self.is_visible()



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
        self.get_handler().VisibilityOn()
        # Fire 'visibility_changed' event
        self.fire_event('visibility_changed')



    def hide(self):
        '''hide()
        Toggle visibility off for this drawing object
        '''
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








# This import is added here to avoid circular dependencies
from .scene import Scene
