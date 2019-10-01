'''
Author: Víctor Ruiz Gómez
Description: This file contains the definition of the class Point
'''


######## Class Point ########

cdef class Point:


    ######## C Attributes ########


    cdef c_Point* _c_handler



    ######## Constructor & Destructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Point*>handler




    ######## Getters ########


    def get_name(self):
        return (<bytes>self._c_handler.get_name()).decode()


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
    def name(self):
        return self.get_name()


    @property
    def position_vector(self):
        return self.get_position_vector()


    @property
    def offset(self):
        return self.get_offset()


    @property
    def previous(self):
        return self.get_previous()



    ######## Metamethods ########


    def __str__(self):
        #if self.has_previous():
        #    return f'Point "{self.name}", position = {self.offset} (base {self.offset.base.name}), previous = {self.previous.name}'
        if not self.has_previous():
            return 'Origin point'

        return tabulate([[
            self.name, self.offset.x, self.offset.y, self.offset.z, self.offset.base.name, self.previous.name
        ]], headers=('name', 'x', 'y', 'z', 'base', 'previous'), tablefmt='plain')


    def __repr__(self):
        return self.__str__()
