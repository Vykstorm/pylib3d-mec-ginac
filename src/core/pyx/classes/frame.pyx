'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Frame
'''


######## Class Frame ########

cdef class Frame(Object):
    '''
    Objects of this class represents geometric frames. They are defined with a
    point, scale and a base.
    '''


    ######## Attributes ########


    cdef c_Frame* _c_handler
    cdef object _owner



    ######## Constructor ########

    def __cinit__(self, Py_ssize_t handler, _System owner=None):
        self._c_handler = <c_Frame*>handler
        self._owner = owner



    ######## Getters ########

    cpdef get_point(self):
        '''get_point() -> Point
        Get the point of this frame

        :rtype: Point

        '''
        return Point(<Py_ssize_t>self._c_handler.get_Point())


    cpdef get_scale(self):
        '''get_scale() -> float

        Get the scale of this frame

        :rtype: float
        '''
        return self._c_handler.get_scale().to_double()



    ######## Setters ########


    cpdef set_point(self, point):
        '''set_point(point: Point)
        Changes the point of this frame.

        :raise TypeError: If the input argument has not a valid type

        '''
        if not isinstance(point, Point):
            raise TypeError('Input argument must be a Point object')
        self._c_handler.set_Point((<Point>point)._c_handler)



    ######## Properties ########

    @property
    def point(self):
        '''
        Property that returns the point of this frame. It can also be used to
        assign a new point.

        :rtype: Point

        .. note::
            This uses internally the methods ``get_point`` and ``set_point``

            .. seealso:: :func:`get_point` :func:`set_point`

        '''
        return self.get_point()

    @point.setter
    def point(self, point):
        self.set_point(point)


    @property
    def scale(self):
        '''
        Read only property that returns the scale of this frame.

        :rtype: float

        .. note::
            This used internally the method ``get_scale``

            .. seealso:: :func:`get_scale`
        '''
        return self.get_scale()






NamedObject.register(Frame)
GeometricObject.register(Frame)
