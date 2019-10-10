'''
Author: Víctor Ruiz Gómez
Description: This file contains the definition of the class Point
'''


######## Class Point ########

cdef class Point(Object):
    '''
    Represents a geometric point defined within a system.
    '''


    ######## C Attributes ########


    cdef c_Point* _c_handler



    ######## Constructor & Destructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Point*>handler




    ######## Getters ########


    def get_position_vector(self):
        '''get_position_vector() -> Vector3D
        Get the position vector of this point
        :rtype: Vector3D
        '''
        return _vector_from_c(self._c_handler.get_Position_Vector())


    def get_position(self):
        '''get_position() -> Vector3D
        This is an alias of get_position_vector()
        :rtype: Vector3D
        .. seealso:: get_position_vector
        '''
        if not self.has_previous():
            raise RuntimeError
        return self.get_position_vector()


    def get_previous(self):
        '''get_previous() -> Point
        Get the previous point.
        :rtype: Point
        :raise RuntimeError: If this point dont a preceding one
        '''
        cdef c_Point* c_prev_point = self._c_handler.get_Previous_Point()
        if c_prev_point == NULL:
            raise RuntimeError(f'Point {self.name} dont have a preceding one')
        return Point(<Py_ssize_t>c_prev_point)


    def has_previous(self):
        '''has_previous() -> bool
        Check if this point has a previous one
        :rtype: bool
        '''
        return self._c_handler.get_Previous_Point() != NULL


    ######## Properties ########

    @property
    def position_vector(self):
        '''
        Only read property that returns the position vector of this point
        :rtype: Vector3D
        '''
        return self.get_position_vector()


    @property
    def position(self):
        '''
        This is an alias of position_vector property
        :rtype: Vector3D
        .. seealso:: position_vector
        '''
        return self.get_position()


    @property
    def previous(self):
        '''
        Only read property that returns the previous point.
        :rtype: Point
        :raise RuntimeError: If this point dont have a preceding one.
        .. seealso:: get_previous
        '''
        return self.get_previous()





NamedObject.register(Point)
