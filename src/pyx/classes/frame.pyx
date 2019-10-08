'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Frame
'''


######## Class Frame ########

cdef class Frame(Object):


    ######## Attributes ########


    cdef c_Frame* _c_handler



    ######## Constructor ########

    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Frame*>handler



    ######## Getters ########

    cpdef get_point(self):
        return Point(<Py_ssize_t>self._c_handler.get_Point())


    cpdef get_scale(self):
        return self._c_handler.get_scale().to_double()



    ######## Setters ########


    cpdef set_point(self, point):
        if not isinstance(point, Point):
            raise TypeError('Input argument must be a Point object')
        self._c_handler.set_Point((<Point>point)._c_handler)



    ######## Properties ########

    @property
    def point(self):
        return self.get_point()

    @point.setter
    def point(self, point):
        self.set_point(point)


    @property
    def scale(self):
        return self.get_scale()






NamedObject.register(Frame)
GeometricObject.register(Frame)
