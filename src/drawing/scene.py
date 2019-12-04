'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Scene
'''

######## Import statements ########

# standard imports
from operator import methodcaller
from itertools import chain

# imports from other modules
from .object import Object
from .simulation import Simulation
from .scad import scad_to_stl
from .color import Color
from .transform import Transform
from lib3d_mec_ginac_ext import Vector3D, Point, Frame, Matrix, Solid

# vtk imports
from vtk import vtkRenderer




######## Helper variables ########


_render_modes = ['points', 'wireframe', 'solid']





######## class Scene ########

class Scene(Object):

    ######## Constructor ########

    def __init__(self, system):
        # Initialize super instance
        super().__init__()

        # Create vtk renderer
        renderer = vtkRenderer()

        # Set default camera position
        renderer.GetActiveCamera().SetPosition(7, 7, 7)

        # Set default background color
        renderer.SetBackground(1, 1, 1)
        renderer.SetBackgroundAlpha(1)

        # Create simulation
        simulation = Simulation(self, system)
        self.add_child(simulation)

        # Initialize internal fields
        self._renderer = renderer
        self._system = system
        self._simulation = simulation
        self._background_color = Color()
        self._render_mode = 'solid'


        # Listen for events
        self.add_child(self._background_color)
        self.add_event_handler(self._event_handler)
        self.add_event_handler(self._on_render_mode_changed, 'render_mode_changed')
        self._simulation.add_event_handler(self._on_simulation_step, 'simulation_step')
        self._background_color.add_event_handler(self._on_background_color_changed, 'changed')



    ######## Event handlers ########

    def _event_handler(self, event_type, source, *args, **kwargs):
        # This method is called when an event occurs
        if isinstance(source, Drawing3D):
            if event_type in ('object_entered', 'object_exit'):
                # A new drawing object entered or exit this 3d scene
                actors = map(methodcaller('get_handler'), chain([source], source.get_predecessors(Drawing3D)))
                if event_type == 'object_entered':
                    # Add all actors attached to the drawing object to the scene renderer
                    render_mode = self._render_mode
                    render_mode_id = _render_modes.index(render_mode)
                    for actor in actors:
                        actor.GetProperty().SetRepresentation(render_mode_id)
                        self._renderer.AddActor(actor)

                elif event_type == 'object_exit':
                    # Remove all actors attached to the drawing object to the scene renderer
                    for actor in actors:
                        self._renderer.RemoveActor(actor)

        elif isinstance(source, Drawing2D):
            # A new 2D drawing entered / exit the scene
            actor = source.get_handler()
            if event_type == 'object_entered':
                self._renderer.AddActor2D(actor)
            elif event_type == 'object_exit':
                self._renderer.RemoveActor2D(actor)



    def _on_render_mode_changed(self, *args, **kwargs):
        # This is called when the render mode changes
        render_mode = self._render_mode
        render_mode_id = _render_modes.index(render_mode)

        for drawing in self.get_3D_drawings():
            actors = map(methodcaller('get_handler'), chain([drawing], drawing.get_predecessors(Drawing3D)))
            for actor in actors:
                actor.GetProperty().SetRepresentation(render_mode_id)



    def _on_simulation_step(self, *args, **kwargs):
        # This method is called when the simulation executes the next step
        # Update drawings
        self._update()



    def _on_background_color_changed(self, *args, **kwargs):
        # This method is invoked when the background color of the scene is changed
        renderer = self._renderer
        renderer.SetBackground(*self._background_color.rgb)
        renderer.SetBackgroundAlpha(self._background_color.a)




    ######## Update ########


    def _update(self):
        # This method is called whenever the scene should be updated

        # Update drawings
        for drawing in self.get_drawings():
            drawing._update()






    ######## Getters ########


    def is_simulation_running(self):
        '''is_simulation_running() -> bool
        Returns True if the simulation is running. False otherwise.
        '''
        return self._simulation.is_running()



    def is_simulation_paused(self):
        '''is_simulation_paused() -> bool
        Returns True if the simulation is paused. False otherwise.
        '''
        return self._simulation.is_paused()



    def is_simulation_stopped(self):
        '''is_simulation_stopped() -> bool
        Returns True if the simulation is stopped. False otherwise.
        '''
        return self._simulation.is_stopped()



    def get_simulation_update_frequency(self):
        '''get_simulation_update_frequency() -> float
        Returns the current simulation update frequency (in number of updates per second)

        :rtype: float

        '''
        return self._simulation.get_update_frequency()



    def get_simulation_time_multiplier(self):
        '''get_simulation_time_multiplier() -> float
        Returns the current simulation time multiplier

        :rtype: float

        '''
        return self._simulation.get_time_multiplier()



    def get_drawings(self):
        '''get_drawings() -> List[Drawing]
        Get all the drawings previously created in the scene

        :rtype: List[Drawing]

        '''
        return self.get_children(kind=Drawing)


    def get_2D_drawings(self):
        '''get_2D_drawings() -> List[Drawing2D]
        Get all the 2D drawings previously created in the scene

        :rtype: List[Drawing2D]

        '''
        return self.get_children(kind=Drawing2D)


    def get_3D_drawings(self):
        '''get_3D_drawings() -> List[Drawing2D]
        Get all the 3D drawings previously created in the scene

        :rtype: List[Drawing3D]

        '''
        return self.get_children(kind=Drawing3D)



    def get_background_color(self):
        '''get_background_color() -> Color
        Get the background color of the scene

        :rtype: Color

        '''
        return self._background_color



    def get_render_mode(self):
        '''get_render_mode() -> str
        Get the current rendering mode.

        :return: 'wireframe', 'solid' or 'points'
        '''
        with self:
            return self._render_mode





    ######## Setters ########


    def set_simulation_update_frequency(self, frequency):
        '''set_simulation_update_frequency(frequency: numeric)
        Change the simulation update frequency.

        :param frequency: The new simulation update frequency (in number of updates per second)

        '''
        self._simulation.set_update_frequency(frequency)




    def set_simulation_time_multiplier(self, multiplier):
        '''set_simulation_time_multiplier(multiplier: numeric)
        Change the simulation time multiplier

        :param multiplier: The new simulation time multiplier

        '''
        self._simulation.set_time_multiplier(multiplier)



    def set_background_color(self, *args):
        '''set_background_color(...)
        Set the background color of the scene
        '''
        self._background_color.set(*args)



    def set_render_mode(self, mode):
        '''set_render_mode(mode: str)
        Change the rendering mode of the drawings.

        :param mode: The rendering mode. Possible values are 'solid', 'wireframe' or
            'points'

        '''
        if not isinstance(mode, str):
            raise TypeError('Input argument must be string')
        if mode not in _render_modes:
            raise TypeError(f'Invalid render mode. Possible values are: {", ".join(_render_modes)}')
        with self:
            self._render_mode = mode
            self.fire_event('render_mode_changed')





    ######## Simulation controls ########


    def start_simulation(self):
        '''start_simulation()
        Starts the simulation

        :raises RuntimeError: If the simulation already started

        '''
        self._simulation.start()



    def stop_simulation(self):
        '''stop_simulation()
        Stops the simulation

        :raises RuntimeError: If the simulation is already stopped

        '''
        self._simulation.stop()



    def resume_simulation(self):
        '''resume_simulation()
        Resumes the simulation

        :raises RuntimeError: If the simulation is not paused

        '''
        self._simulation.resume()



    def pause_simulation(self):
        '''pause_simulation()
        Pauses the simulation

        :raises RuntimeError: If the simulation is not running

        '''
        self._simulation.pause()




    ######## Add/Remove drawings ########


    def purge_drawings(self):
        '''purge_drawings()
        Remove all the drawing objects created previously
        '''
        with self:
            drawings = self.get_drawings()
            for drawing in drawings:
                self.remove_child(drawing)



    def add_drawing(self, drawing):
        '''add_drawing(drawing: Drawing)
        Add a new drawing object to the scene
        '''
        if not isinstance(drawing, Drawing):
            raise TypeError('Input argument must be a Drawing instance')
        self.add_child(drawing)




    def _apply_point_transform(self, drawing, point):
        system = self._system
        OC = system.position_vector(system.O, point)
        base = OC.get_base()
        R = system.rotation_matrix(system.xyz, base)
        T = R * OC
        drawing.add_transform(Transform.translation(T) & Transform.rotation(R))


    def _apply_vector_transform(self, drawing, vector):
        system = self._system
        # Put the vector into the xyz base
        vector = vector.in_base(system.xyz)

        shaft, tip = drawing.shaft, drawing.tip
        shaft_size = shaft.geometry.height
        tip_size = tip.geometry.height

        drawing.add_transform(Transform.rotation_from_dir(vector))
        m = vector.get_module()
        shaft.scale((m+shaft_size-1)/shaft_size, 1, 1)
        tip.translate(m-shaft_size-tip_size, 0, 0)





    def draw_point(self, point, *args, **kwargs):
        # Validate & parse point argument
        if not isinstance(point, (Point, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(point, str):
            point = self._system.get_point(point)

        # Create a point drawing
        drawing = PointDrawing(*args, **kwargs)

        # Setup drawing transformation
        self._apply_point_transform(drawing, point)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def draw_frame(self, frame, *args, **kwargs):
        # Validate & parse point argument
        if not isinstance(frame, (Frame, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(frame, str):
            frame = self._system.get_frame(frame)

        # Create a frame drawing
        drawing = FrameDrawing(*args, **kwargs)

        # Setup drawing transformation
        self._apply_point_transform(drawing, frame.get_point())

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def draw_vector(self, point, vector, *args, **kwargs):
        # Validate & parse point argument
        if not isinstance(vector, (Vector3D, str)):
            raise TypeError('vector argument must be a Vector3D or str instance')
        if not isinstance(point, (Point, str)):
            raise TypeError('point argument must be a Point or str instance')

        if isinstance(vector, str):
            vector = self._system.get_vector(vector)
        if isinstance(point, str):
            point = self._system.get_point(point)

        # Create a vector drawing
        drawing = VectorDrawing(*args, **kwargs)

        # Setup drawing transformation
        self._apply_vector_transform(drawing, vector)
        self._apply_point_transform(drawing, point)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing




    def draw_stl(self, filename, color=(1, 1, 0), scale=5):
        # Create STL geometry
        geometry = read_stl(filename)

        # Create the drawing object
        drawing = Drawing3D(geometry)
        drawing.set_color(color)

        # Setup drawing transformation
        drawing.scale(scale)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def draw_scad(self, filename, color=(1, 1, 0), scale=5, **kwargs):
        # Convert the scad file to a stl
        stl_filename = scad_to_stl(filename, **kwargs)
        return self.draw_stl(stl_filename, color, scale)




    def draw_solid(self, solid, *args, **kwargs):
        # Validate & parse point argument
        if not isinstance(solid, (Solid, str)):
            raise TypeError('solid argument must be a Vector3D or str instance')

        if isinstance(solid, str):
            solid = self._system.get_solid(solid)

        # Create the drawing
        drawing = self.draw_stl(solid.get_name() + '.stl', *args, **kwargs)

        # Setup drawing transformation
        self._apply_point_transform(drawing, solid.get_point())

        return drawing



    def draw_position_vector(self, a, b, *args, **kwargs):
        return self.draw_vector(a, self._system.position_vector(a, b), *args, **kwargs)


    def draw_velocity_vector(self, frame, point):
        return self.draw_vector(point, self._system.velocity_vector(frame, point))


    def draw_text(self, *args, **kwargs):
        drawing = TextDrawing(*args, **kwargs)
        self.add_drawing(drawing)
        return drawing



    @property
    def background_color(self):
        '''
        Property that can be used to set/get the background color of this scene

        .. seealso::
            :func:`set_background_color`, :func:`get_background_color`
        '''
        return self.get_background_color()


    @background_color.setter
    def background_color(self, args):
        self.set_background_color(*args)



    @property
    def render_mode(self):
        '''
        Property that can be used to set/get the render mode for the drawings of this
        scene.

        .. seealso::
            :func:`set_render_mode`, :func:`get_render_mode`

        '''
        return self.get_render_mode()

    @render_mode.setter
    def render_mode(self, mode):
        self.set_render_mode(mode)




# This imports are moved here to avoid circular dependencies
from .drawing import Drawing, Drawing2D, TextDrawing, Drawing3D, PointDrawing, VectorDrawing, FrameDrawing
from .geometry import Geometry, read_stl
