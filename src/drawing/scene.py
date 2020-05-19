'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Scene
'''

######## Import statements ########

# standard imports
from operator import methodcaller, eq, add, itemgetter
from functools import partial
from itertools import chain, starmap
import tempfile
from math import floor
from time import sleep
import sys

# imports from other modules
from ..utils.events import EventProducer
from .simulation import Simulation
from .color import Color
from .transform import Transform
from .vector import Vector2
from .camera import Camera
from lib3d_mec_ginac_ext import Vector3D, Point, Frame, Matrix, Solid

# vtk imports
from vtk import vtkRenderer, vtkRenderWindow, vtkWindowToImageFilter, vtkPNGWriter
from vtk import vtkOggTheoraWriter

# IPython imports
try:
    import IPython
    _is_ipython_avaliable = True
    _is_notebook_environment = False
    try:
        if IPython.get_ipython().__class__.__name__ == 'ZMQInteractiveShell':
            _is_notebook_environment = True
    except NameError:
        pass
except ImportError:
    # No problem if IPython is not avaliable
    _is_ipython_avaliable = False


# third party imports
from tabulate import tabulate




######## Helper variables ########


_render_modes = ['points', 'wireframe', 'solid']





######## class Scene ########

class Scene(EventProducer):

    ######## Constructor ########

    def __init__(self, system):
        # Initialize super instance
        super().__init__()

        self.add_child(system)

        # Create vtk renderer
        renderer = vtkRenderer()

        # Create simulation
        simulation = Simulation(self, system)
        self.add_child(simulation)

        # Initialize internal fields
        self._renderer = renderer
        self._system = system
        self._simulation = simulation
        self._background_color = Color('white')
        self._render_mode = 'solid'
        self._camera = Camera(renderer.GetActiveCamera())
        self._drawings_default_visibility = {}

        self.add_child(self._camera)

        # Initialize background color
        self.add_child(self._background_color)
        self._update_background_color()

        # Listen for simulation events
        self.add_event_handler(self._on_render_mode_changed, 'render_mode_changed')
        self._simulation.add_event_handler(self._on_simulation_step, 'simulation_step')
        self._simulation.add_event_handler(self._on_simulation_started, 'simulation_started')
        self._simulation.add_event_handler(self._on_simulation_stopped, 'simulation_stopped')
        self._simulation.add_event_handler(self._on_simulation_resumed, 'simulation_resumed')
        self._simulation.add_event_handler(self._on_simulation_paused, 'simulation_paused')

        # Listen for manual changes on the symbols values
        self.add_event_handler(self._on_symbol_value_changed, 'symbol_value_changed')

        # Refresh background color when changed
        self._background_color.add_event_handler(self._on_background_color_changed, 'changed')
        self.add_event_handler(self._on_object_entered, 'object_entered')
        self.add_event_handler(self._on_object_exit, 'object_exit')

        # Listen for drawing select events
        self.add_event_handler(self._on_drawing_selected, 'selected')
        self.add_event_handler(self._on_drawing_unselected, 'unselected')


        # Add simulation info text display
        display = TextDrawing('', position=(0.01, -0.02), font_size=15, color='black', italic=False)
        display.set_position_relative_to_top_left()
        display.vertical_justification = 'top'
        self._simulation_display_info = display
        self.add_drawing(display)

        # Add drawings info text display
        display = TextDrawing('', position=(-0.01, -0.02), font_size=15, color='black', italic=False)
        display.set_position_relative_to_top_right()
        display.vertical_justification = 'top'
        display.horizontal_justification = 'right'

        self._drawings_display_info = display
        self.add_drawing(display)

        self._grid = GridDrawing()
        self.add_drawing(self._grid)



    ######## Event handlers ########


    def _on_object_entered(self, event_type, source, *args, **kwargs):
        if isinstance(source, Drawing3D):
            # A new 3D drawing object entered or exit the scene
            actors = map(methodcaller('get_handler'), chain([source], source.get_predecessors(Drawing3D)))
            # Add all actors attached to the drawing object to the scene renderer
            render_mode = self._render_mode
            render_mode_id = _render_modes.index(render_mode)
            for actor in actors:
                actor.GetProperty().SetRepresentation(render_mode_id)
                self._renderer.AddActor(actor)

        elif isinstance(source, Drawing2D):
            # A new 2D drawing entered the scene
            self._renderer.AddActor2D(source.get_handler())

        elif isinstance(source, GridDrawing):
            # A grid was added to the scene
            self._renderer.AddActor(source.get_handler())




    def _on_object_exit(self, event_type, source, *args, **kwargs):
        if isinstance(source, Drawing3D):
            # A 3D drawing object exit the scene
            actors = map(methodcaller('get_handler'), chain([source], source.get_predecessors(Drawing3D)))
            # Remove all actors attached to the drawing object to the scene renderer
            for actor in actors:
                self._renderer.RemoveActor(actor)

        elif isinstance(source, Drawing2D):
            # A 2D drawing object exit the scene
            self._renderer.RemoveActor2D(source.get_handler())

        elif isinstance(source, GridDrawing):
            # A grid was removed from the scene
            self._renderer.RemoveActor(source.get_handler())


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
        self._update_simulation_display_info()


    def _on_simulation_started(self, *args, **kwargs):
        self._update_simulation_display_info()


    def _on_simulation_stopped(self, *args, **kwargs):
        self._simulation_display_info.text = ''


    def _on_simulation_paused(self, *args, **kwargs):
        self._update_simulation_display_info()


    def _on_simulation_resumed(self, *args, **kwargs):
        self._update_simulation_display_info()


    def _on_background_color_changed(self, *args, **kwargs):
        # This method is called whenever the background color is changed
        self._update_background_color()



    def _on_drawing_selected(self, event_type, source, *args, **kwargs):
        # This is invoked when a 3D drawing is selected
        self._update_drawings_display_info()



    def _on_drawing_unselected(self, event_type, source, *args, **kwargs):
        # This is invoked when a 3D drawing is unselected
        self._update_drawings_display_info()



    def _on_symbol_value_changed(self, event_type, source, symbol):
        if not self.is_simulation_running():
            self._update_3D_drawings()




    ######## Update ########


    def _update_simulation_display_info(self):
        display = self._simulation_display_info
        lines = [
            f'simulation is {"paused" if self._simulation.is_paused() else "resumed"}',
            't = {:.3f} secs'.format(self._system.get_time().get_value()),
            f'{int(self._simulation.get_real_update_frequency())} updates/sec'
        ]
        display.text = '\n'.join(lines)


    def _update_drawings_display_info(self):
        display = self._drawings_display_info

        # Get current selected drawing
        selected = get_selected_drawing()

        text = ''
        if selected is not None:
            # If any drawing is currently selected...
            info = []
            if isinstance(selected, PointDrawing):
                point = selected.point
                if point != self._system.O:
                    position = point.position
                    text += f'point {point.name} \n'
                    info.extend([
                        ['x', position.x],
                        ['y', position.y],
                        ['z', position.z],
                        ['base', position.base.name]
                    ])
                else:
                    text += f'origin point'

            elif isinstance(selected, VectorDrawing):
                vector = selected.vector
                if isinstance(selected, PositionVectorDrawing):
                    a, b = selected.start_point, selected.end_point
                    text += f'position vector ({a.name} -> {b.name}) \n'
                elif isinstance(selected, VelocityVectorDrawing):
                    frame, point = selected.frame, selected.point
                    text += f'velocity vector of {point.name} with respect {frame.name} \n'
                else:
                    text += f'vector {vector.name}'
                info.extend([
                    ['x', vector.x],
                    ['y', vector.y],
                    ['z', vector.z],
                    ['base', vector.base.name]
                ])

            elif isinstance(selected, FrameDrawing):
                frame = selected.frame
                text += f'frame {frame.name} \n'
                info.extend([
                    ['point', frame.point.name],
                    ['scale', frame.scale],
                    ['base', frame.base.name]
                ])

            elif isinstance(selected, SolidDrawing):
                solid = selected.solid
                text += f'solid {solid.name} \n'
                info.extend([
                    ['point', solid.point.name],
                    ['base', solid.base.name],
                    ['mass', f'{solid.mass.name} = {solid.mass.value}'],
                    ['CM', solid.CM.name],
                    ['IT', solid.IT.name]
                ])

            if info:
                def fixedlen(s, n):
                    if len(s) < n-4:
                        return s
                    return s[:n-4] + ' ...'
                # Display selected object info as tabular data
                info = zip(map(itemgetter(0), info), map(partial(fixedlen, n=50), map(str, map(itemgetter(1), info))))
                text += tabulate(info, headers=(), tablefmt='orgtbl', colalign=['left', 'right'])

        # Update displayed text
        display.text = text





    def _update_drawings(self):
        # This method is called whenever the drawings of this scene must be updated
        self._update_2D_drawings()
        self._update_3D_drawings()


    def _update_2D_drawings(self):
        # This method is called when 2D drawings of this scene must be updated
        for drawing in self.get_2D_drawings():
            drawing._update()


    def _update_3D_drawings(self):
        # This method is called when 3D drawings of this scene must be updated
        for drawing in self.get_3D_drawings():
            drawing._update()


    def _update_background_color(self):
        # This method is called whenever the background color must be updated
        renderer = self._renderer
        renderer.SetBackground(*self._background_color.rgb)
        renderer.SetBackgroundAlpha(self._background_color.a)






    ######## Getters ########


    def is_simulation_running(self):
        '''is_simulation_running() -> bool

        :return: True if the simulation is running. False otherwise.
        :rtype: bool

        '''
        return self._simulation.is_running()



    def is_simulation_paused(self):
        '''is_simulation_paused() -> bool

        :return: True if the simulation is paused. False otherwise.
        :rtype: bool

        '''
        return self._simulation.is_paused()



    def is_simulation_stopped(self):
        '''is_simulation_stopped() -> bool

        :return: True if the simulation is stopped. False otherwise.
        :rtype: bool

        '''
        return self._simulation.is_stopped()


    def is_simulation_looped(self):
        '''is_simulation_looped() -> bool

        :return: True if the simulation is in loop mode. False otherwise (only relevant
            when time limit is set)
        :rtype: bool
        '''
        return self._simulation.is_looped()


    def get_simulation_time_limit(self):
        '''get_simulation_time_limit() -> float | None
        Get the simulation time limit if any. None otherwise

        :rtype: float, None
        '''
        return self._simulation.get_time_limit()



    def get_simulation_update_frequency(self):
        '''get_simulation_update_frequency() -> float

        :return: The current simulation update frequency (in number of updates per second)
        :rtype: float

        '''
        return self._simulation.get_update_frequency()



    def get_simulation_real_update_frequency(self):
        '''get_simulation_real_update_frequency() -> float

        :return: The current simulation real update frequency (in number of updates per second)
        :rtype: float

        '''
        return self._simulation.get_real_update_frequency()



    def get_simulation_time_multiplier(self):
        '''get_simulation_time_multiplier() -> float

        :return: The current simulation time multiplier
        :rtype: float

        '''
        return self._simulation.get_time_multiplier()


    def get_simulation_delta_time(self):
        '''get_simulation_delta_time() -> float | None
        :return: The current simulation delta time if it has a fixed value. None otherwise
        :rtype: float
        '''
        return self._simulation.get_delta_time()




    def get_drawings(self):
        '''get_drawings() -> List[Drawing]

        :return: All the drawings previously created in the scene.
        :rtype: List[Drawing]

        '''
        return self.get_children(kind=Drawing)


    def get_2D_drawings(self):
        '''get_2D_drawings() -> List[Drawing2D]

        :return: All the 2D drawings previously created in the scene
        :rtype: List[Drawing2D]

        '''
        return self.get_children(kind=Drawing2D)


    def get_3D_drawings(self):
        '''get_3D_drawings() -> List[Drawing2D]

        :return: All the 3D drawings previously created in the scene
        :rtype: List[Drawing3D]

        '''
        return self.get_children(kind=Drawing3D)



    def get_background_color(self):
        '''get_background_color() -> Color

        :return: The background color of the scene
        :rtype: Color

        '''
        return self._background_color



    def get_render_mode(self):
        '''get_render_mode() -> str

        :return: The current rendering mode: 'wireframe', 'solid' or 'points'
        :rtype: str

        '''
        return self._render_mode


    def get_camera(self):
        '''get_camera() -> Camera
        Get the camera to view this scene.
        :rtype Camera
        '''
        return self._camera


    def get_camera_position(self):
        '''get_camera_position() -> Vector3
        Get the current position of the camera to view this scene
        :rtype: Vector3
        '''
        return self._camera.get_position()


    def get_camera_focal_point(self):
        '''get_camera_focal_point() -> Vector3
        Get the current camera focal point
        :rtype: Vector3
        '''
        return self._camera.get_focal_point()



    def get_grid(self):
        '''get_grid() -> Grid
        Get the grid of the scene
        :rtype: Grid
        '''
        return self._grid




    def _get_drawing_by_handler(self, handler):
        for drawing in self.get_drawings():
            if drawing.get_handler() == handler or\
                any(map(partial(eq, handler), map(methodcaller('get_handler'), drawing.get_predecessors(Drawing)))):
                return drawing
        return None

    def _get_2D_drawing_by_handler(self, handler):
        drawing = self._get_drawing_by_handler(handler)
        if not isinstance(drawing, Drawing2D):
            return None
        return drawing

    def _get_3D_drawing_by_handler(self, handler):
        drawing = self._get_drawing_by_handler(handler)
        if not isinstance(drawing, Drawing3D):
            return None
        return drawing



    ######## Setters ########


    def set_simulation_looped(self, looped=True):
        '''set_simulation_looped(looped: bool)
        Enable/Disable simulation looping mode (only relevant when time limit is set)
        '''
        self._simulation.set_looped(looped)


    def set_simulation_time_limit(self, limit):
        '''set_simulation_time_limit(limit: numeric | None)
        Set simulation time limit.
        '''
        self._simulation.set_time_limit(limit)


    def set_simulation_delta_time(self, delta_t):
        '''set_simulation_delta_time(delta_t: numeric | None)
        Set simulation delta time
        '''
        self._simulation.set_delta_time(delta_t)


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

        self._render_mode = mode
        self.fire_event('render_mode_changed')



    def set_camera_position(self, *args):
        '''set_camera_position(...)
        Changes the position of the camera used to view this scene.
        '''
        self._camera.set_position(*args)



    def set_camera_focal_point(self, *args):
        '''set_camera_focal_point(...)
        Changes the focal point of the camera used to view this scene.
        '''
        self._camera.set_focal_point(*args)





    ######## Simulation controls ########


    def start_simulation(self, *args, **kwargs):
        '''start_simulation()
        Starts the simulation.

        :raises RuntimeError: If the simulation already started

        '''
        self._simulation.start(*args, **kwargs)



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
        drawings = self.get_drawings()
        for drawing in drawings:
            if drawing == self._grid:
                continue
            self.remove_child(drawing)



    def add_drawing(self, drawing):
        '''add_drawing(drawing: Drawing)
        Add manually a new drawing object to the scene
        '''
        if not isinstance(drawing, Drawing):
            raise TypeError('Input argument must be a Drawing instance')
        # Set drawing default visibility
        hierachy = drawing.__class__.__mro__
        hierachy = hierachy[:hierachy.index(Drawing)+1]
        for cls in hierachy:
            try:
                if self._drawings_default_visibility[cls]:
                    drawing.show()
                else:
                    drawing.hide()
                break
            except KeyError:
                pass

        # Add the drawing to the scene
        self.add_child(drawing)




    def _apply_point_transform(self, drawing, point):
        system = self._system
        OC = system.position_vector(system.O, point)
        base = OC.get_base()
        R = system.rotation_matrix(system.xyz, base)
        T = R * OC
        drawing.add_transform(Transform.translation(T))


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





    def draw_point(self, point, scale=1, **kwargs):
        '''draw_point(point: Point, ...) -> PointDrawing
        Draw the given point in the scene

        :param point: The point to draw
        :type point: Point, str

        :param scale: Scale of the drawing. It can be a single value or a list of three values
            (indicating the scale on each dimension). Values can be numbers or symbolic
            expressions

        :param color: Color of the drawing. It can be a list of three or four numeric
            values in the range [0, 1] to indicate the rgb or rgba components of the
            color. It can also be a predefined color name (string)

            .. seealso:: :func:`get_predefined_colors`
        :param numeric radius: Radius of the sphere which is used to draw the point.
            By default is 0.06
        :param numeric resolution: Resolution of the sphere geometry.
            By default is 15

        :rtype: PointDrawing


        The next example draws the origin point with green color. The radius of the sphere
        geometry is set to 0.25

            :Example:

            >>> drawing = draw_point('O', color='green', radius=0.25)


        '''
        # Validate & parse point argument
        if not isinstance(point, (Point, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(point, str):
            point = self._system.get_point(point)

        # Create a point drawing
        drawing = PointDrawing(point, **kwargs)

        # Setup drawing transformation
        drawing.scale(scale)
        OC = self._system.position_vector(self._system.O, point).in_base(self._system.xyz)
        drawing.translate(OC)
        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def draw_frame(self, frame, scale=1, **kwargs):
        '''draw_frame(frame: Frame, ...) -> FrameDrawing
        Draw the given frame in the 3D scene.

        :param scale: Scale of the drawing. It can be a single value or a list of three values
            (indicating the scale on each dimension). Values can be numbers or symbolic
            expressions

        :param axis_shaft_radius: Radius of the shaft of each axis. By default is 0.03
        :param axis_tip_radius: Radius of the tip of each axis. By default is 0.1
        :param origin_radius: Radius of the sphere drawn at the origin. By default is 0.06

        :param axis_shaft_resolution: Resolution of the shaft of each axis. By default is 10
        :param axis_tip_resolution: Resolution of the tip of each axis. By default is 15
        :param origin_resolution: Resolution of the sphere drawn at the origin. By default is 15

        :param axis_shaft_color: Color of the shaft of each axis. By default is white.
        :param axis_tip_colors: A list of three colors, one color for each axis. Default is red, green and blue
        :param origin_color: Color of the sphere drawn at the origin. By default is white.


        :rtype: FrameDrawing

        The next example draws the 'abs' frame. The arrow colors are set to yellow, magenta and cyan
        for the x, y and z axis respectively. Finally, the frame is scaled by the parameter 'a':

            :Example:

            >>> a = new_param('a', 1.2)
            >>> drawing = draw_frame('abs', scale=a, axis_tip_colors=['yellow', 'magenta', 'cyan'])

        '''
        # Validate & parse point argument
        if not isinstance(frame, (Frame, str)):
            raise TypeError('Input argument must be a Point or str instance')
        if isinstance(frame, str):
            frame = self._system.get_frame(frame)

        # Create a frame drawing
        drawing = FrameDrawing(frame, **kwargs)

        # Setup drawing transformation
        drawing.scale(scale)
        point = frame.get_point()
        pv = self._system.position_vector(self._system.O, point)

        R = self._system.rotation_matrix(self._system.xyz, frame.get_base())
        T = pv.in_base(self._system.xyz)

        drawing.rotate(R)
        drawing.translate(T)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def _draw_vector(self, cls, point, vector, *args, **kwargs):
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
        drawing = cls(vector, *args, **kwargs)

        # Setup drawing transformation
        self._apply_vector_transform(drawing, vector)
        v = self._system.position_vector(self._system.O, point).in_base(self._system.xyz)
        drawing.translate(v)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing



    def draw_vector(self, point, vector, **kwargs):
        '''draw_vector(point: Point, vector: Vector3D, ...) -> VectorDrawing
        Draws a vector starting from the given point

        :param point: The point that will be the origin of the vector
        :param vector: The vector to draw
        :type point: Point, str
        :type vector: Vector3D, str

        :param shaft_radius: Radius of the shaft. By default is 0.03
        :param tip_radius: Radius of the tip. By default is 0.1
        :param origin_radius: Radius of the sphere drawn at the origin. By default is 0.06

        :param shaft_resolution: Resolution of the shaft. By default is 10
        :param tip_resolution: Resolution of the tip. By default is 15
        :param origin_resolution: Resolution of the sphere drawn at the origin. By default is 15

        :param shaft_color: Color of the shaft. By default is white
        :param tip_color: Color of the tip. By default is yellow
        :param origin_color: Color of the sphere drawn at the origin. By default is white

        :rtype: VectorDrawing

        The next example illustrates how to draw a vector with components sin(a), 0 and cos(a) with the
        point 'O' as the origin point. The color of the tip is set to red.

            :Example:

            >>> a = new_param('a')
            >>> v = new_vector('v', sin(a), 0, cos(a))
            >>> drawing = draw_vector('O', v, tip_color='red')

        '''
        return self._draw_vector(VectorDrawing, point, vector, **kwargs)




    def draw_position_vector(self, a, b, **kwargs):
        '''draw_position_vector(start: Point, end: Point, ...) -> PositionVectorDrawing
        Draw a vector from the point a to b

        :rtype: VectorDrawing

        .. note::
            .. seealso:: :func:`draw_vector`
            .. seealso:: :func:`position_vector`

        '''
        if not isinstance(a, (Point, str)):
            raise TypeError('a must be a Point or str object')
        if not isinstance(b, (Point, str)):
            raise TypeError('b must be a Point or str object')
        if isinstance(a, str):
            a = self._system.get_point(a)
        if isinstance(b, str):
            b = self._system.get_point(b)

        return self._draw_vector(PositionVectorDrawing, a, self._system.position_vector(a, b), a, b, **kwargs)



    def draw_velocity_vector(self, frame, point, **kwargs):
        '''draw_velocity_vector(frame: Frame, point: Point, ...) -> VelocityVectorDrawing
        Draw the velocity vector of the given point with respect the specified frame

        :rtype: VectorDrawing

        .. note::
            .. seealso:: :func:`draw_vector`
            .. seealso:: :func:`velocity_vector`
        '''
        if not isinstance(frame, (Frame, str)):
            raise TypeError('frame must be a Frame or str object')
        if not isinstance(point, (Point, str)):
            raise TypeError('point must be a Point or str object')
        if isinstance(frame, str):
            frame = self._system.get_frame(frame)
        if isinstance(point, str):
            point = self._system.get_point(point)

        return self._draw_vector(VelocityVectorDrawing, point, self._system.velocity_vector(frame, point), frame, point, **kwargs)




    def _draw_stl(self, cls, filepath, color, scale, *args, **kwargs):
        # Create STL geometry
        geometry = read_stl(filepath)

        # Create the drawing object
        drawing = cls(*args, **kwargs)
        drawing.set_geometry(geometry)
        drawing.set_color(color)

        # Setup drawing transformation
        drawing.scale(scale)

        # Add the drawing to the scene
        self.add_drawing(drawing)

        return drawing




    def draw_stl(self, filepath, color=(1, 1, 0), scale=5):
        '''draw_stl(filepath: str, color, scale) -> Drawing3D
        Draw the given stl model in the 3D scene.

        :param filepath: Path of the stl file.
        :param color: Color of the drawing. It can be a list of three or four numeric
            values in the range [0, 1] to indicate the rgb or rgba components of the
            color. It can also be a predefined color name (string)
        :param scale: Scale of the drawing. It can be a single value or a list of three values
            (indicating the scale on each dimension). Values can be numbers or symbolic
            expressions

        :rtype: Drawing3D

        '''
        return self._draw_stl(Drawing3D, filepath, color, scale)




    def draw_scad(self, filepath, color=(1, 1, 0), scale=5, **kwargs):
        '''draw_scad(filepath: str, color, scale, ...) -> Drawing3D
        Draws the given scad model in the 3D scene.

        :param filepath: Path of the scad file.
        :param color: Color of the drawing. It can be a list of three or four numeric
            values in the range [0, 1] to indicate the rgb or rgba components of the
            color. It can also be a predefined color name (string)
        :param scale: Scale of the drawing. It can be a single value or a list of three values
            (indicating the scale on each dimension). Values can be numbers or symbolic
            expressions

        :rtype: Drawing3D

        You can parametrize the scad model by specifything extra keyword arguments.
        The next example draws the scad file 'Arm.scad' (included in the four_bar example)
        setting the parameter ``n_facets`` to 20

            :Example:

            >>> drawing = draw_scad('Arm.scad', n_facets=20)

        '''
        # Convert the scad file to a stl
        stl_filename = scad_to_stl(filepath, **kwargs)
        return self.draw_stl(filepath, color, scale)




    def draw_solid(self, solid, color=(1, 1, 0), scale=5):
        '''draw_solid(solid: Solid, ...) -> Drawing3D
        Draws the given solid in the 3D scene. A stl file in the working directory with
        the same name as the solid must exist.

        :param solid: Is the solid to be drawn
        :type solid: Solid, str

        :rtype: Drawing3D

        .. note::
            This is a shorthand for ``draw_stl(solid.get_name() + '.stl', ...)``

            .. seealso:: :func:`draw_stl`

        '''
        # Validate & parse point argument
        if not isinstance(solid, (Solid, str)):
            raise TypeError('solid argument must be a Vector3D or str instance')

        if isinstance(solid, str):
            solid = self._system.get_solid(solid)

        # Create the drawing
        drawing = self._draw_stl(SolidDrawing, solid.get_name() + '.stl', color, scale, solid)

        # Setup drawing transformation
        point = solid.get_point()
        pv = self._system.position_vector(self._system.O, point)

        R = self._system.rotation_matrix(self._system.xyz, solid.get_base())
        T = pv.in_base(self._system.xyz)

        drawing.rotate(R)
        drawing.translate(T)


        return drawing




    def draw_text(self, **kwargs):
        '''draw_text(text: str, position, color, font_size) -> TextDrawing
        Draws text in the screen

        :param text: The text to be drawn.
        :param position: The position (two numbers) in which text should appear in normalized
            screen coordinates (in the range 0 to 1). By default is (0, 0)
        :param color: Color of the text. It can be a list of three or four numeric
            values in the range [0, 1] to indicate the rgb or rgba components of the
            color. It can also be a predefined color name (string)

        :param font_size: Size of the font. By defaut is 20
        :param font_family: Font family. Must be 'courier', 'times' or 'arial'
        :param bold: If True, set bold text mode on
        :param italic: If True, set italic text mode on

        :rtype: TextDrawing

        '''
        drawing = TextDrawing(*args, **kwargs)
        self.add_drawing(drawing)
        return drawing




    def get_screenshot(self, width=640, height=480):
        '''get_screenshot() -> IPython.display.Image | None
        Take a screenshot of the scene and return it as IPython image if called within
        a jupyter notebook environment.

        To be implemented: A parameter ``file`` to save the image in a file.

        :rtype: IPython.Image | None
        '''
        if not isinstance(width, int) or width <= 0:
            raise TypeError('width must be an integer greater than zero')

        if not isinstance(height, int) or height <= 0:
            raise TypeError('height must be an integer greater than zero')

        simulation = self._simulation

        simulation_stopped = simulation.is_stopped()
        if simulation_stopped:
            simulation.start()
        self._update_drawings()
        if simulation_stopped:
            simulation.stop()

        window = vtkRenderWindow()
        window.SetOffScreenRendering(1)
        window.AddRenderer(self._renderer)
        window.SetSize(width, height)
        window.Render()

        filter = vtkWindowToImageFilter()
        filter.SetInput(window)
        filter.Update()

        writer = vtkPNGWriter()
        writer.SetCompressionLevel(0)
        writer.SetWriteToMemory(1)
        writer.SetInputConnection(filter.GetOutputPort())
        writer.Write()

        if _is_ipython_avaliable and _is_notebook_environment:
            return IPython.display.Image(memoryview(writer.GetResult()).tobytes())




    def record_simulation(self, width=640, height=480, file=None, step_callback=None, delta_t=None, time_limit=None):
        '''record_simulation() -> Ipython.display.Video | None
        Record the simulation of this scene and save the results in a video ( ogg format ).
        The video is stored in a file with the given name as argument ( by default its stored
        in a temporal file ).

        :return: An Ipython display video object which embeds the recorded simulation if working on a jupyter
        notebook environment or None otherwise.

        .. note::

            If you set this to a specific file and you embed the video in notebook jupyter cell,
            you will experience problems when trying to record the simulation a second time ( the video will
            not be updated because jupyter inserts the video in its cache )
        '''

        # Validate & parse input arguments
        if not isinstance(width, int) or width <= 0:
            raise TypeError('width must be an integer greater than zero')

        if not isinstance(height, int) or height <= 0:
            raise TypeError('height must be an integer greater than zero')

        if step_callback is not None and not callable(step_callback):
            raise TypeError('step_callback must be a callable object')

        if self.is_simulation_looped():
            raise RuntimeError('Simulation cannot be looped in order to be recorded')

        if time_limit is None:
            if self.get_simulation_time_limit() is None:
                raise RuntimeError('Simulation must have a time limit in order to be recorded')
        else:
            self.set_simulation_time_limit(time_limit)

        if delta_t is not None:
            self.set_simulation_delta_time(delta_t)

        simulation = self._simulation
        delta_t = simulation.get_delta_time()
        time_limit = simulation.get_time_limit()


        filepath = file

        # If file is not specified, save the video in a temporal file
        if filepath is None:
            file = tempfile.NamedTemporaryFile()
            filepath = file.name
            file.close()

        # Create a new VTK window for off-screen rendering
        window = vtkRenderWindow()
        window.SetOffScreenRendering(1)
        window.AddRenderer(self._renderer)
        window.SetSize(width, height)
        window.Render()

        filter = vtkWindowToImageFilter()
        filter.SetInput(window)
        filter.Update()

        # Prepare an OGG file writer
        writer = vtkOggTheoraWriter()
        writer.SetFileName(filepath)
        writer.SetRate(floor(1/delta_t))
        writer.SetInputConnection(filter.GetOutputPort())
        writer.Start()

        # Stop the simulation if it was already started
        if not simulation.is_stopped():
            simulation.stop()


        def on_step(*args, **kwargs):
            # This is a callback that will be called on each simulation step
            progress = floor((simulation.get_elapsed_time() / simulation.get_time_limit()) * 100)
            progress = min(progress, 100)
            print('\r'*15 + 'progress:  ' + str(progress).ljust(3) + '%', end='', flush=True)
            if step_callback is not None:
                step_callback()
            # Update drawings
            self._update_drawings()
            # Render a new frame of the simulation
            window.Render()
            filter.Modified()
            writer.Write()


        self.add_event_handler(on_step, 'simulation_step')
        self._drawings_display_info.hide()
        # Start the simulation
        self.start_simulation()

        try:
            # Perform the simulation
            while simulation.is_running():
                simulation._update(delta_t)

            writer.End()

            print()
            print('completed      ', flush=True)

            if _is_ipython_avaliable and _is_notebook_environment:
                return IPython.display.Video(filepath, embed=True, mimetype='video/ogg')
        finally:
            self.remove_event_handler(on_step)
            self._drawings_display_info.show()



    ######## Show / hide geometry ########


    def toogle_drawings(self, points=None, vectors=None, frames=None, solids=None, grid=None, others=None, simulation_info=None):
        classes = (
            PointDrawing,
            VectorDrawing,
            FrameDrawing,
            SolidDrawing,
        )
        f = (points, vectors, frames, solids)
        _classes = tuple(map(classes.__getitem__, filter(f.__getitem__, range(len(f)))))

        # Update drawings default visibility ( for new drawings created after this call )
        self._drawings_default_visibility.update(dict(chain(
            map(lambda cls: (cls, False), map(classes.__getitem__, filter(lambda i: f[i] is False, range(len(f))))),
            map(lambda cls: (cls, True), _classes)
        )))
        if others is not None:
            self._drawings_default_visibility[Drawing] = others

        # Update the visibility of the drawings already created before this call
        for drawing in self.get_3D_drawings():
            if any(map(partial(isinstance, drawing), _classes)) or not isinstance(drawing, classes) and others:
                drawing.show()
            else:
                if any(map(partial(isinstance, drawing), classes)):
                    if any(map(lambda i: isinstance(drawing, classes[i]) and f[i] is False, range(len(f)))):
                        drawing.hide()
                elif others is False:
                    drawing.hide()

        # Change simulation info display visibility
        if simulation_info is False:
            self._simulation_display_info.hide()
        elif simulation_info is True:
            self._simulation_display_info.show()

        # Change grid visibility
        if grid is False:
            self.grid.hide()
        elif grid is True:
            self.grid.show()

        # Trigger events
        for group, arg in [('points', points), ('vectors', vectors), ('frames', frames), ('solids', solids), ('grid', grid), ('others', others)]:
            if arg is None:
                continue
            self.fire_event('drawings_group_visibility_changed', group, arg)



    def get_drawings_group_visibility(self, group):
        if group not in ('points', 'vectors', 'frames', 'solids', 'grid', 'simulation_info', 'others'):
            raise ValueError(f'Invalid drawing group name {str(group)}')
        if group not in ('grid', 'simulation_info'):
            cls = dict(
                points=PointDrawing,
                vectors=VectorDrawing,
                frames=FrameDrawing,
                solids=SolidDrawing,
                others=Drawing
            )[group]
            return self._drawings_default_visibility.get(cls, True)
        elif group == 'grid':
            return self.grid.is_visible()
        return self._simulation_display_info.is_visible()





    def hide_simulation_display_info(self):
        '''hide_simulation_display_info()
        Hides the simulation display info
        '''
        self.toogle_drawings(simulation_info=False)


    def show_simulation_display_info(self):
        '''hide_simulation_display_info()
        Shows the simulation display info
        '''
        self.toogle_drawings(simulation_info=True)



    def show_grid(self):
        '''show_grid()
        Shows the grid of the scene
        '''
        self.toogle_drawings(grid=True)


    def hide_grid(self):
        '''hide_grid()
        Hides the grid of the scene
        '''
        self.toogle_drawings(grid=False)




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



    @property
    def grid(self):
        '''
        Property that can be used to get the grid of the scene

        .. seealso::
            :func:`get_grid`

        '''
        return self.get_grid()




# This imports are moved here to avoid circular dependencies
from .drawing import Drawing
from .drawing2D import *
from .drawing3D import *
from .grid import GridDrawing
from .geometry import Geometry, read_stl
from .viewer import get_selected_drawing, get_viewer, open_viewer
from .scad import scad_to_stl
