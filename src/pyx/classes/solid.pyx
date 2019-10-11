'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class Solid.
'''



######## Class Solid ########

cdef class Solid(Frame):


    ######## Getters ########


    cpdef get_CM(self):
        return _vector_from_c((<c_Solid*>self._c_handler).get_CM())


    cpdef get_IT(self):
        return _tensor_from_c((<c_Solid*>self._c_handler).get_IT())


    cpdef get_G(self):
        return Point(<Py_ssize_t>(<c_Solid*>self._c_handler).get_G())


    cpdef get_mass(self):
        return SymbolNumeric(<Py_ssize_t>(<c_Solid*>self._c_handler).get_mass())



    ######## Setters ########


    ######## Properties ########


    @property
    def CM(self):
        return self.get_CM()


    @property
    def IT(self):
        return self.get_IT()


    @property
    def G(self):
        return self.get_G()


    @property
    def mass(self):
        return self.get_mass()
