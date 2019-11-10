'''
Author: Víctor Ruiz Gómez
Description:
This file defines the class Solid.
'''



######## Class Solid ########

cdef class Solid(Frame):
    '''
    Objects of this class represent solids.
    '''

    ######## Getters ########


    cpdef get_CM(self):
        '''get_CM() -> Vector3D
        Get the center of mass of this solid.

        :rtype: Vector3D

        '''
        return _vector_from_c((<c_Solid*>self._c_handler).get_CM())


    cpdef get_IT(self):
        '''get_IT() -> Tensor3D
        Get the inertia tensor of this solid.

        :rtype: Tensor3D

        '''
        return _tensor_from_c((<c_Solid*>self._c_handler).get_IT())


    cpdef get_G(self):
        # TODO fix me
        return Point(<Py_ssize_t>(<c_Solid*>self._c_handler).get_G())


    cpdef get_mass(self):
        '''get_mass() -> SymbolNumeric
        Get the mass of this solid.

        :rtype: SymbolNumeric

        '''
        return SymbolNumeric(<Py_ssize_t>(<c_Solid*>self._c_handler).get_mass())



    ######## Setters ########


    ######## Properties ########


    @property
    def CM(self):
        '''
        Only read property that returns the center of mass of this solid.

        :rtype: Vector3D

        .. note:: This calls internally to `get_CM`

            .. seealso:: :func:`get_CM`

        '''
        return self.get_CM()


    @property
    def IT(self):
        '''
        Only read property that returns the intertia tensor of this solid.

        :rtype: Tensor3D

        .. note:: This calls internally to `get_IT`

            .. seealso:: :func:`get_IT`

        '''
        return self.get_IT()


    @property
    def G(self):
        return self.get_G()


    @property
    def mass(self):
        '''
        Only read property that returns the mass of this solid.

        :rtype: SymbolNumeric

        .. note:: This calls internally to `get_mass`

            .. seealso:: :func:`get_mass`

        '''
        return self.get_mass()
