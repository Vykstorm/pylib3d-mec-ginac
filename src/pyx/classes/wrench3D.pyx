'''
Author: Víctor Ruiz Gómez
Description:
This file defines the Wrench3D class
'''



cdef class Wrench3D(Object):

    ######## Constructor ########



    ######## Getters ########


    cpdef get_force(self):
        pass


    cpdef get_moment(self):
        pass


    cpdef get_solid(self):
        pass


    cpdef get_type(self):
        pass


    ######## Operations ########


    cpdef unatomize(self):
        pass


    cpdef at_point(self, point):
        pass


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
