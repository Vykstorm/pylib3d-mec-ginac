'''
Author: Víctor Ruiz Gómez
Description: This module defines the class Tensor3D
'''




######## Class Tensor3D ########

cdef class Tensor3D(Matrix):

    ######## Constructor ########

    def __init__(self, values=None, base=None, system=None):
        if values is None and base is None and system is None:
            # Construct without arguments is reserved for internal implementation purposes
            self._c_handler = NULL
            return

        if not isinstance(system, _System):
            raise TypeError(f'system must be a valid System object')

        if not isinstance(base, Base):
            base = system.get_base(base)

        values = Matrix(shape=(3, 3), values=list(values))


        # Call matrix initializer
        self._c_handler = new c_Tensor3D(
            c_deref((<Matrix>values)._get_c_handler()),
            (<Base>base)._c_handler
        )
        self._owns_c_handler = True




    ######## Getters ########


    def get_base(self):
        return Base(<Py_ssize_t>(<c_Vector3D*>self._get_c_handler()).get_Base())




    ######## Setters ########



    ######## Operations ########



    ######## Properties ########


    @property
    def base(self):
        return self.get_base()



    ######## Printing ########
