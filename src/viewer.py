
class Drawing3D:
    '''
    This class represents any kind of drawing. Is the base class for PointDrawing,
    LineDrawing, VectorDrawing and FrameDrawing
    '''
    pass


class PointDrawing(Drawing3D):
    '''
    Instances of this class represents point drawings.
    '''
    pass

class VectorDrawing(Drawing3D):
    '''
    Instances of this class represents vector drawings.
    '''
    pass

class LineDrawing(Drawing3D):
    '''
    Instances of this class represents line drawings.
    '''
    pass

class FrameDrawing(Drawing3D):
    '''
    Instances of this class represents frame drawings.
    '''
    pass


class Camera:
    '''
    An instance of this class represent a camera which is used to visualize the scene.
    '''
    pass



class Scene:
    '''
    Instances of this class can be used to draw points, frames, vectors, ...
    '''

    ######## Constructor ########

    def __init__(self, system):
        self.system = system




    ######## Drawing creation routines ########


    def draw_point(point, radius=1, scale=1, color='black', resolution=15):
        '''draw_point(...) -> PointDrawing
        Create a new point drawing (is rendered as a sphere with the given radius and
        resolution)

        :param point: The point to be drawn
        :param radius: The radius of the sphere. By default is 1
        :param scale: Scale of the drawing. It can be a single number or a list of three
            numbers indicating the scale of the drawing on each dimension.
        :param color: The color of the drawing. It can be a color name or a list of the
            three or four numeric values in the range [0 , 1] indicating the r,g,b[, a]
            color components.
        :param resolution: Resolution of the sphere mesh. By default is 15

        :rtype: PointDrawing

        :raises TypeError: If the given input arguments have invalid types.
        :raises ValueError: If the given input arguments have invalid values.

        '''
        pass




    def draw_vector(origin, vector,
        tip_radius=0.1, shaft_radius=0.03, origin_radius=0.06, tip_size=0.25,
        shaft_resolution=10, tip_resolution=25, origin_resolution=15, show_origin=True,
        scale=1, shaft_color='gray', tip_color='red', origin_color='black'):
        '''draw_vector(...) -> VectorDrawing
        Create a new vector drawing. Is rendered as a cylinder with a cone in the top and
        a sphere in the origin (if show_origin is set to True)

        :param origin: Is the origin point of the vector.
        :param vector: Is the vector to be drawn
        :param tip_radius: Radius of the tip of the vector. By default is 0.1
        :param shaft_radius: Radius of the shaft of the vector. By default is 0.03
        :param origin_radius: Radius of the sphere drawn at the origin. By default is 0.06
        :param tip_size: Size of the tip of the vector. By default is 0.25
        :param shaft_resolution: Resolution of the shaft of the vector. By default is 10
        :param tip_resolution: Resolution of the tip of the vector. By default is 25
        :param origin_resolution: Resolution of the sphere drawn at the origin. By default is 15
        :param show_origin: If true, a sphere is drawn at the origin.
        :param scale: Scale of the drawing. It can be a single number or a list of three
            numbers indicating the scale of the drawing on each dimension.
        :param shaft_color: The color of the shaft of the vector. It can be a color name or a list of the
            three or four numeric values in the range [0 , 1] indicating the r,g,b[, a]
            color components.
        :param tip_color: The color of the tip of the vector
        :param origin_color: The color of the sphere drawn at the origin


        :rtype: VectorDrawing

        :raises TypeError: If the given input arguments have invalid types.
        :raises ValueError: If the given input arguments have invalid values.

        '''
        pass




    def draw_line(start, end, scale=1, color='black'):
        '''draw_line(...) -> LineDrawing
        Draw a simple line between the given points

        :param start: The starting point
        :param end: The ending point
        :param scale: Scale of the drawing. It can be a single number or a list of three
            numbers indicating the scale of the drawing on each dimension.
        :param color: The color of the line. It can be a color name or a list of the
            three or four numeric values in the range [0 , 1] indicating the r,g,b[, a]
            color components.

        :rtype: LineDrawing

        :raises TypeError: If the given input arguments have invalid types.
        :raises ValueError: If the given input arguments have invalid values.

        '''
        pass



    def draw_frame(frame,
        axis_tip_radius=0.1, axis_shaft_radius=0.03, axis_tip_size=0.25, origin_radius=0.06,
        axis_shaft_resolution=10, axis_tip_resolution=25, origin_resolution=15,
        scale=1, axis_shaft_color='gray', axis_tip_colors=['red', 'green', 'blue'], origin_color='black'):
        '''draw_frame(...) -> FrameDrawing
        Draw the given frame; A sphere will be draw at the origin point of the frame. Also three
        vectors representing the axis of the frame.

        :param frame: The frame to be drawn
        :param axis_tip_radius: Radius of the tip of the axis. By default is 0.1
        :param axis_shaft_radius: Radius of the shaft of the axis. By default is 0.03
        :param axis_tip_size: Size of the tip of the axis. By default is 0.25
        :param origin_radius: Radius of the sphere drawn at the origin. By default is 0.06
        :param axis_shaft_resolution: Resolution of the shaft of the axis. By default is 10
        :param axis_tip_resolution: Resolution of the tip of the vector. By default is 25
        :param origin_resolution: Resolution of the sphere drawn at the origin. By default is 15
        :param scale: Scale of the drawing. It can be a single number or a list of three
            numbers indicating the scale of the drawing on each dimension.

        :param axis_shaft_color: The color of the shaft of the axis. It can be a color name or a list of the
            three or four numeric values in the range [0 , 1] indicating the r,g,b[, a]
            color components. By defaut is gray.
        :param axis_tip_colors: A tuple of three items with the colors for the tip of the axis on
            each dimension (x, y and z). By default is red, green and blue
        :param origin_color: Color of the sphere drawn at the origin. By default is black.

        :rtype: FrameDrawing

        :raises TypeError: If the given input arguments have invalid types.
        :raises ValueError: If the given input arguments have invalid values.

        '''
        pass



    ######## Getters ########


    def get_drawings():
        '''get_drawings() -> List[Drawing3D]
        Get all the drawings created.

        :rtype: List[Drawing3D]

        '''
        pass



    def get_point_drawings():
        '''get_point_drawings() -> List[PointDrawing]
        Get all the point drawings created.

        :rtype: List[PointDrawing]

        '''
        pass


    def get_vector_drawings():
        '''get_vector_drawings() -> List[PointDrawing]
        Get all the vector drawings created.

        :rtype: List[VectorDrawing]

        '''
        pass



    def get_line_drawings():
        '''get_line_drawings() -> List[PointDrawing]
        Get all the line drawings created.

        :rtype: List[LineDrawing]

        '''
        pass



    def get_frame_drawings():
        '''get_frame_drawings() -> List[FrameDrawing]
        Get all the frame drawings created

        :rtype: List[FrameDrawing]

        '''
        pass



    def get_camera():
        '''get_camera() -> Camera
        Get the camera used to view this scene

        :rtype: Camera

        '''



    ######## Properties ########



    @property
    def drawings(self):
        '''
        Only read property that returns all the drawings of this scene

        .. seealso:: :func:`get_drawings`
        '''
        return self.get_drawings()


    @property
    def point_drawings(self):
        '''
        Only read property that returns all the point drawings of this scene

        .. seealso:: :func:`get_point_drawings`
        '''
        return self.get_point_drawings()


    @property
    def line_drawings(self):
        '''
        Only read property that returns all the line drawings of this scene

        .. seealso:: :func:`get_line_drawings`
        '''
        return self.get_line_drawings()


    @property
    def vector_drawings(self):
        '''
        Only read property that returns all the vector drawings of this scene

        .. seealso:: :func:`get_vector_drawings`
        '''
        return self.get_vector_drawings()


    @property
    def framw_drawings(self):
        '''
        Only read property that returns all the frame drawings of this scene

        .. seealso:: :func:`get_frame_drawings`
        '''
        return self.get_frame_drawings()


    @property
    def camera(self):
        '''
        Only read property that returns the camera used to view this scene

        .. seealso:: :func: `get_camera`

        '''
        return self.get_camera()





    ######## Scene management ########


    def set_background_color(color):
        '''set_background_color(...)
        Change the background color when drawing the scene.
        You can specify the red, green, blue and alpha color components in a list
        or as multiple positional arguments. All values must be in the range [0, 1]

            :Example:

            >>> set_background_color([1, 0.5, 0.5])
            >>> set_background_color([1, 0.5, 0.5, 0.85])

            >>> set_background_color(1, 0.5, 0.5)
            >>> set_background_color(1, 0.5, 0.5, 0.85)

        It can also be a string (e.g: 'blue')

            :Example:

            >>> set_background_color('blue')


        Opacity can also be set using the keyword arugment 'alpha' if the color is specified
        as a string.

            :Example:

            >>> set_background_color('blue', alpha=0.65)

        '''
        pass




    def set_draw_update_rate(freq):
        '''set_draw_update_rate(freq: int)
        Set the draw update frequency of the drawings (translation and rotation transformations
        will be also evaluated numerically as such update frequency when possible)

        :param freq: Update rate frequency in updates per second. Must be an integer greater than zero
        :type freq: int

        '''
        pass




    def show_drawings():
        '''show_drawings()
        Open a new window an start rendering all the drawings on it.
        '''
        pass



    def hide_drawings():
        '''hide_drawings()
        Close the window which is used to render the drawings (this method dont do anything if
        show_drawings() wasnt called before)

        .. seealso:: :func:`show_drawings`

        '''
        pass
