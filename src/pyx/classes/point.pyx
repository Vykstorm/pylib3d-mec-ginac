'''
Author: Víctor Ruiz Gómez
Description: This file contains the definition of the class Point
'''


######## Class Point ########

cdef class Point(Object):


    ######## C Attributes ########


    cdef c_Point* _c_handler



    ######## Constructor & Destructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Point*>handler




    ######## Getters ########


    def get_position_vector(self):
        return _vector_from_c(self._c_handler.get_Position_Vector())


    def get_offset(self):
        if not self.has_previous():
            raise RuntimeError
        return self.get_position_vector()


    def get_previous(self):
        cdef c_Point* c_prev_point = self._c_handler.get_Previous_Point()
        if c_prev_point == NULL:
            raise RuntimeError(f'Point {self.name} dont have a preceding one')
        return Point(<Py_ssize_t>c_prev_point)


    def has_previous(self):
        return self._c_handler.get_Previous_Point() != NULL


    ######## Properties ########

    @property
    def position_vector(self):
        return self.get_position_vector()


    @property
    def offset(self):
        return self.get_offset()


    @property
    def previous(self):
        return self.get_previous()





NamedObject.register(Point)
