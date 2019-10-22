'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Drawing3D
'''



######## Class Drawing3D ########

cdef class Drawing3D(Object):
    '''
    Objects of this class represents drawable elements. They are defined with a
    point, base, vector, scale and color.
    '''

    ######## Attributes ########

    cdef c_Drawing3D* _c_handler


    ######## Constructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Drawing3D*>handler



    ######## Getters ########


    cpdef get_file(self):
        '''get_file() -> str
        Get the file of this drawing object

        :rtype: str

        '''
        return (<bytes>self._c_handler.get_file()).decode()


    cpdef get_type(self):
        '''get_type() -> str
        Get the type of this drawing

        :rtype: str

        '''
        return (<bytes>self._c_handler.get_type()).decode()


    cpdef get_color(self):
        '''get_color() -> List[Expr]
        Get the color components of this drawing

        :rtype: List[Expr]

        '''
        cdef c_lst color = self._c_handler.get_color()
        return [_expr_from_c(color.op(i)) for i in range(0, color.nops())]


    cpdef get_point(self):
        '''get_point() -> Point
        Get the point of this drawing

        :rtype: Point

        '''
        return Point(<Py_ssize_t>self._c_handler.get_Point())


    cpdef get_scale(self):
        '''get_scale() -> numeric
        Get the scale of this drawing

        :rtype: numeric

        '''
        return self._c_handler.get_scale().to_double()


    cpdef get_vector(self):
        '''get_vector() -> Vector3D
        Get the vector of this drawing

        :rtype: Vector3D

        '''
        return _vector_from_c_value(self._c_handler.get_vector())




    ######## Setters ########


    cpdef set_file(self, file):
        '''set_file(file: str)
        Set the file for this drawing

        :type file: str

        '''
        if not isinstance(file, str):
            raise TypeError('Input argument must be a string')
        self._c_handler.set_file(<bytes>file.encode())


    def set_color(self, *args):
        '''set_color(...)
        Set the color of the drawing object.

        You can pass the color components as positional arguments or in a single
        list:

            :Example:

            >>> a = new_drawing('a', get_frame('abs'))
            >>> a.set_color(1, 1, 0, 1)
            >>> a.get_color()
            [1, 1, 0, 1]
            >>> a.set_color([1, 0, 1, 0.5])
            [1, 0, 1, 0.5]

        '''
        if len(args) not in (1, 4):
            raise TypeError('Unexpected number of input arguments')

        try:
            if len(args) != 1:
                values = args
            else:
                values = args[0]
                if not isinstance(values, Iterable):
                    raise TypeError
            values = tuple(map(_parse_numeric_value, values))
            if len(values) != 4:
                raise TypeError
        except TypeError:
            raise TypeError('You must pass a list of four values or four positional arguments')

        cdef c_lst c_color
        for value in values:
            c_color.append(c_ex(c_numeric(<double>value)))

        self._c_handler.set_color(c_color)




    cpdef set_scale(self, scale):
        '''set_scale(scale: numeric)
        Set the scale of this drawing

        :type scale: numeric

        '''
        scale = _parse_numeric_value(scale)
        self._c_handler.set_scale(c_numeric(<double>scale))


    cpdef set_vector(self, vector):
        '''set_vector(vector: Vector3D)
        Set the vector of this drawing

        :type vector: Vector3D

        '''
        if not isinstance(vector, Vector3D):
            raise TypeError('Input argument must be a vector')
        self._c_handler.set_vector(c_deref(<c_Vector3D*>(<Vector3D>vector)._get_c_handler()))



    ######## Properties ########


    @property
    def file(self):
        '''
        Property that can be used to fetch/modify the file of this drawing object.

        :rtype: str

        .. note:: This property used internally the methods ``get_file`` and
            ``set_file``

            .. seealso:: :func:`get_file`

            .. seealso:: :func:`set_file`

        '''
        return self.get_file()

    @file.setter
    def file(self, file):
        self.set_file(file)


    @property
    def point(self):
        '''
        Read only property that fetch the point of this drawing object.

        :rtype: Point

        .. note:: This calls internally to ``get_point``

            .. seealso:: :func:`get_point`

        '''
        return self.get_point()


    @property
    def scale(self):
        '''
        Property that can be used to fetch/modify the scale of this drawing object.

        :rtype: str

        .. note:: This property used internally the methods ``get_scale`` and
            ``set_scale``

            .. seealso:: :func:`get_scale`

            .. seealso:: :func:`set_scale`

        '''
        return self.get_scale()

    @scale.setter
    def scale(self, value):
        self.set_scale(value)


    @property
    def type(self):
        '''
        Read only property that fetch the type of this drawing object.

        :rtype: Point

        .. note:: This calls internally to ``get_type``

            .. seealso:: :func:`get_type`

        '''
        return self.get_type()



    @property
    def vector(self):
        '''
        Read only property that fetch the vector of this drawing object.

        :rtype: Point

        .. note:: This calls internally to ``get_vector``

            .. seealso:: :func:`get_vector`

        '''
        return self.get_vector()

    @vector.setter
    def vector(self, v):
        self.set_vector(v)


    @property
    def color(self):
        '''
        Property that can be used to fetch/modify the color of this drawing object.

        :rtype: str

        .. note:: This property used internally the methods ``get_color`` and
            ``set_color``

            .. seealso:: :func:`get_color`

            .. seealso:: :func:`set_color`

        '''
        return self.get_color()

    @color.setter
    def color(self, values):
        self.set_color(values)


    @property
    def r(self):
        # TODO
        pass

    @property
    def g(self):
        # TODO
        pass

    @property
    def b(self):
        # TODO
        pass

    @property
    def a(self):
        # TODO
        pass




NamedObject.register(Drawing3D)
GeometricObject.register(Drawing3D)
