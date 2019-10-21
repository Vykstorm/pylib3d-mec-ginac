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
        return (<bytes>self._c_handler.get_file()).decode()


    cpdef get_type(self):
        return (<bytes>self._c_handler.get_type()).decode()


    cpdef get_color(self):
        cdef c_lst color = self._c_handler.get_color()
        return [_expr_from_c(color.op(i)) for i in range(0, color.nops())]


    cpdef get_point(self):
        return Point(<Py_ssize_t>self._c_handler.get_Point())


    cpdef get_scale(self):
        return self._c_handler.get_scale().to_double()


    cpdef get_vector(self):
        return _vector_from_c_value(self._c_handler.get_vector())




    ######## Setters ########


    cpdef set_file(self, file):
        if not isinstance(file, str):
            raise TypeError('Input argument must be a string')
        self._c_handler.set_file(<bytes>file.encode())


    def set_color(self, *args):
        # TODO
        pass


    cpdef set_scale(self, scale):
        scale = _parse_numeric_value(scale)
        self._c_handler.set_scale(c_numeric(<double>scale))


    cpdef set_vector(self, vector):
        if not isinstance(vector, Vector3D):
            raise TypeError('Input argument must be a vector')
        self._c_handler.set_vector(c_deref(<c_Vector3D*>(<Vector3D>vector)._get_c_handler()))



    ######## Properties ########


    @property
    def file(self):
        return self.get_file()

    @file.setter
    def file(self, file):
        self.set_file(file)


    @property
    def scale(self):
        return self.get_scale()

    @scale.setter
    def scale(self, value):
        self.set_scale(value)


    @property
    def vector(self):
        return self.get_vector()

    @vector.setter
    def vector(self, v):
        self.set_vector(v)


    @property
    def color(self):
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
