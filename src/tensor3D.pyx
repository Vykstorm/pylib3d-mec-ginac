'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Tensor3D
'''




######## Class Tensor3D ########

cdef class Tensor3D(Matrix):

    ######## Constructor ########

    def __init__(self, values, base, system):
        if not isinstance(system, _System):
            raise TypeError(f'system must be a valid System object')

        if not isinstance(base, Base):
            base = system.get_base(base)


        # Call matrix initializer
        super().__init__(shape=(3, 3), values=values)




    ######## Getters ########


    def get_base(self):
        pass


    ######## Setters ########


    def set_base(self, base):
        pass



    ######## Operations ########


    ######## Properties ########


    @property
    def base(self):
        return self.get_base()



    ######## Printing ########
