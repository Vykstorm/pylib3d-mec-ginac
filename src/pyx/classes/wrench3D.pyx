'''
Author: Víctor Ruiz Gómez
Description:
This file defines the Wrench3D class
'''




cdef Wrench3D _wrench_from_c(c_Wrench3D* x):
    wrench = Wrench3D()
    wrench._c_handler, wrench._owns_c_handler = x, False
    return wrench


cdef Wrench3D _wrench_from_c_value(c_Wrench3D x):
    wrench = Wrench3D()
    wrench._c_handler = new c_Wrench3D(
        x.get_name(), x.get_Force(), x.get_Moment(), x.get_Point(),
        x.get_Solid(), x.get_Type()
    )
    wrench._owns_c_handler = True
    return wrench




cdef class Wrench3D(Object):

    ######## Constructor ########

    cdef c_Wrench3D* _c_handler
    cdef bint _owns_c_handler



    ######## Constructor & Destructor ########

    def __cinit__(self):
        self._c_handler = NULL


    def __dealloc__(self):
        if self._c_handler != NULL and self._owns_c_handler:
            del self._c_handler



    ######## Getters ########


    cpdef get_force(self):
        return _vector_from_c_value(self._c_handler.get_Force())


    cpdef get_moment(self):
        return _vector_from_c_value(self._c_handler.get_Moment())


    cpdef get_solid(self):
        return Solid(<Py_ssize_t>self._c_handler.get_Solid())


    cpdef get_type(self):
        return (<bytes>self._c_handler.get_Type()).decode()



    ######## Operations ########


    cpdef unatomize(self):
        return _wrench_from_c_value(self._c_handler.unatomize())


    cpdef at_point(self, point):
        if not isinstance(point, Point):
            raise TypeError('Input argument must be a Point object')
        return _wrench_from_c_value(self._c_handler.at_Point((<Point>point)._c_handler))



    ######## Unary arithmetic operations ########


    def __pos__(self):
        pass


    def __neg__(self):
        pass


    ######## Binary arithmetic operations ########


    def __add__(Wrench3D self, other):
        pass


    def __sub__(Wrench3D self, other):
        pass


    def __mul__(left_op, right_op):
        pass


    def __truediv__(left_op, right_op):
        pass



    ######## Properties ########


    @property
    def force(self):
        return self.get_force()


    @property
    def moment(self):
        return self.get_moment()


    @property
    def solid(self):
        return self.get_solid()


    @property
    def type(self):
        return self.get_type()



NamedObject.register(Wrench3D)
