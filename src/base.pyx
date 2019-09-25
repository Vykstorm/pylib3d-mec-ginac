'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Base
'''



######## Imports ########

# Import cython internal library
cimport cython

# C++ standard library imports
from libcpp.string cimport string as c_string

# Import .pxd declarations
from src.cbase cimport Base as c_Base
from src.cexpression cimport ex as c_ex

# Python imports
from operator import attrgetter




######## Class Base ########


cdef class Base:
    '''
    Objects of this class represent geometric bases defined within a system.
    '''

    ######## C Attributes ########


    cdef c_Base* _c_handler




    ######## Constructor & Destructor ########


    def __cinit__(self, Py_ssize_t handler):
        self._c_handler = <c_Base*>handler




    ######## Getters ########


    cpdef get_name(self):
        '''get_name() -> str
        :returns: The name of this base
        :rtype: str
        '''
        return self._c_handler.get_name().decode()



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




    ######## Properties ########


    @property
    def name(self):
        '''
        Read only property that returns the name of this base
        :rtype: str
        '''
        return self.get_name()


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
        This is an alias of previous_base
        '''
        return self.get_previous_base()


    @property
    def rotation_angle(self):
        '''
        Read only property that returns the rotation angle of this base
        :type: Expr
        '''
        return self.get_rotation_angle()



    ######## Metamethods ########


    def __eq__(self, other):
        if not isinstance(other, Base):
            return False
        return self.get_name() == other.get_name()



    def __hash__(self):
        return hash((Base, self.get_name()))



    def __str__(self):
        s = f'Base {self.name}'

        if self.has_previous():
            ancestors = []
            prev = self.get_previous()
            ancestors.append(prev)
            while prev.has_previous():
                prev = prev.get_previous()
                ancestors.append(prev)

            s += ', ancestors: ' + ' -> '.join(map(attrgetter('name'), ancestors))

        return s


    def __repr__(self):
        return self.__str__()
