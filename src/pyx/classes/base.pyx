'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Base
'''




######## Class Base ########


cdef class Base(Object):
    '''
    Objects of this class represent geometric bases defined within a system.
    '''

    ######## C Attributes ########


    cdef c_Base* _c_handler




    ######## Constructor & Destructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Base*>handler




    ######## Getters ########


    cpdef get_previous_base(self):
        '''get_previous_base() -> Base
        Get the previous base.
        :returns: The previous base of this one if it has.
        :rtype: Base
        :raises RuntimeError: If this base dont any previous one
        '''
        cdef c_Base* c_prev_base = self._c_handler.get_Previous_Base()
        if c_prev_base == NULL:
            raise RuntimeError(f'base {self.name} dont have a preceding one')
        return Base(<Py_ssize_t>c_prev_base)

    get_previous = get_previous_base



    cpdef bint has_previous_base(self):
        '''has_previous_base() -> Base
        Check if this base has a previous one.
        :returns: True if this base has a preceding base, False otherwise.
        :rtype: bool
        '''
        return self._c_handler.get_Previous_Base() != NULL

    has_previous = has_previous_base



    cpdef get_rotation_angle(self):
        '''get_rotation_angle() -> Expr
        Get the rotation angle of this base
        :rtype: Expr
        '''
        return _expr_from_c(self._c_handler.get_Rotation_Angle())


    cpdef get_rotation_tupla(self):
        '''get_rotation_tupla() -> Matrix
        Get the rotation tupla of this base
        :rtype: Matrix
        '''
        return _matrix_from_c_value(self._c_handler.get_Rotation_Tupla())



    ######## Properties ########


    @property
    def previous_base(self):
        '''
        Read only property that returns the previous base
        :rtype: Base
        '''
        return self.get_previous_base()


    @property
    def previous(self):
        '''
        This is an alias of previous_base property
        .. seealso:: previous_base
        '''
        return self.get_previous_base()


    @property
    def rotation_angle(self):
        '''
        Read only property that returns the rotation angle of this base
        :rtype: Expr
        '''
        return self.get_rotation_angle()


    @property
    def rotation_tupla(self):
        '''
        Read only property that returns the rotation tupla of this base
        :rtype: Matrix
        '''
        return self.get_rotation_tupla()




NamedObject.register(Base)
