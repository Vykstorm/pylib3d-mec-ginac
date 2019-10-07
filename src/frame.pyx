'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Frame
'''


######## Class Frame ########

cdef class Frame(Object):


    ######## Attributes ########


    cdef c_Frame* _c_handler




    ######## Getters ########


    cpdef get_name(self):
        return (<bytes>self._c_handler.get_name()).decode()


    cpdef get_base(self):
        return Base(<Py_ssize_t>self._c_handler.get_Base())


    cpdef get_point(self):
        return Point(<Py_ssize_t>self._c_handler.get_Point())


    cpdef get_scale(self):
        return self._c_handler.get_scale().to_double()



    ######## Setters ########


    cpdef set_base(self, base):
        if not isinstance(base, Base):
            raise TypeError('Input argument must be a Base object')
        self._c_handler.set_Base((<Base>base)._c_handler)


    cpdef set_point(self, point):
        if not isinstance(point, Point):
            raise TypeError('Input argument must be a Point object')
        self._c_handler.set_Point((<Point>point)._c_handler)



    ######## Properties ########


    @property
    def base(self):
        return self.get_base()

    @base.setter
    def base(self, base):
        self.set_base(base)


    @property
    def point(self):
        return self.get_point()

    @point.setter
    def point(self, point):
        self.set_point(point)


    @property
    def scale(self):
        return self.get_scale()




    ######## Printing ########






NamedObject.register(Frame)
