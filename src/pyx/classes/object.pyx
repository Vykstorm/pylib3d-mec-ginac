'''
Author: Víctor Ruiz Gómez
Description:


Cython doesn't support multiple inheritance if the derived class is defined with the
prefix "cdef".

To circunvent this and to make the code more reusable and mantainable for
the classes SymbolNumeric, Expr, Matrix, Vector3D, Tensor3D, Base and Point, which share
some behaviour, they must be derived from the Object class.

Base class will provide the next instance methods depending on the kind of object:

                    get_name   to_latex   get_base
SymbolNumeric            yes        yes         no
       Matrix            yes        yes         no
     Vector3D            yes        yes        yes
     Tensor3D            yes        yes        yes
         Base            yes         no         no
        Point            yes         no         no
        Frame            yes         no        yes
         Expr             no        yes         no

* Those classes with the method "get_name" avaliable, also will have the property "name"
* Classes with "to_latex" will have also the method "print_latex" and property "latex"
* Finally, objects with geometric base (with "get_base" method) have also "in_base" method
    to perform a base change operation and the property "base"
'''





######## Mixin classes ########


class NamedObject(ABC):
    '''
    Objects with name inherit the properties and methods defined within this class:
    * Method get_name
    * Property name
    * Metamethod __eq__
    '''

    def get_name(self):
        '''get_name() -> str
        Get the name of the object
        :rtype: str
        '''
        cdef c_string c_name
        if isinstance(self, SymbolNumeric):
            c_name = (<SymbolNumeric>self)._c_handler.get_name()
        elif isinstance(self, Matrix):
            c_name = (<Matrix>self)._get_c_handler().get_name()
        elif isinstance(self, Base):
            c_name = (<Base>self)._c_handler.get_name()
        elif isinstance(self, Point):
            c_name = (<Point>self)._c_handler.get_name()
        elif isinstance(self, Frame):
            c_name = (<Frame>self)._c_handler.get_name()
        else:
            raise RuntimeError

        return (<bytes>c_name).decode()


    @property
    def name(self):
        '''
        Only read property that returns the name of the object
        :rtype: str
        '''
        return self.get_name()



    def __eq__(self, other):
        '''
        Compare the object against other:
        * An object with name is always different to an object without name.
        * An object with name is equal to another object with name if and only if their names are equal
        '''
        if self is other:
            return True
        return isinstance(other, NamedObject) and self.get_name() == other.get_name()





class LatexRenderable(ABC):
    '''
    Objects which can be rendered to latex inherit the properties and methods defined within this class:
    * Methods to_latex and print_latex
    * Property latex
    '''

    def to_latex(self):
        '''to_latex() -> str
        Get this object formatted to latex
        :rtype: str
        '''
        return _to_latex(self)


    def print_latex(self):
        '''print_latex()
        Print this object on Ipython in latex format
        '''
        _print_latex_ipython(self.to_latex())


    @property
    def latex(self):
        '''
        Only read property that returns this object formatted to latex
        :rtype: str
        '''
        return self.to_latex()





class GeometricObject(ABC):
    '''
    Objects defined within a geometric base inherit the properties and methods defined within this class:
    * Methods get_base, in_base
    * Property base
    '''

    def get_base(self):
        '''get_base() -> Base
        Get the base of the object.
        :rtype: Base
        '''
        cdef c_Base* c_base
        #Base(<Py_ssize_t>(<c_Vector3D*>self._get_c_handler()).get_Base())
        if isinstance(self, Vector3D):
            c_base = (<c_Vector3D*>(<Vector3D>self)._get_c_handler()).get_Base()
        elif isinstance(self, Tensor3D):
            c_base = (<c_Tensor3D*>(<Tensor3D>self)._get_c_handler()).get_Base()
        elif isinstance(self, Frame):
            c_base = (<Frame>self)._c_handler.get_Base()
        else:
            raise RuntimeError

        return Base(<Py_ssize_t>c_base)


    def in_base(self, base):
        '''in_base(base: Base)
        Perform a base change operation to the given base
        :param Base base: The new base
        :raise TypeError: If the input argument is not a Base object
        '''
        raise NotImplementedError()


    @property
    def base(self):
        '''
        Property that returns the base of the object. You can also use it as
        a setter to perform a base change operation.
        :rtype: Base
        '''
        return self.get_base()


    @base.setter
    def base(self, x):
        self.in_base(x)






######## Class Object ########


cdef class Object:
    '''
    This is the base class of Expr, SymbolNumeric, Base, Matrix, Vector and Point
    classes.
    It emulates multiple inheritance to the abstract classes defined above
    (NamedObject, LatexRenderable, GeometricObject)
    '''

    @property
    def _bases(self):
        # Returns all the abstract interfaces implemented by this instance
        return [cls for cls in (NamedObject, LatexRenderable, GeometricObject) if isinstance(self, cls)]

    @property
    def _inherited_methods(self):
        # Returns all the inherited methods from the abstract interfaces
        # implemented by this instance
        methods = {}
        for base in self._bases:
            for name, value in base.__dict__.items():
                if not name.startswith('_') and callable(value):
                    methods[name] = value
        return methods


    @property
    def _inherited_properties(self):
        # Returns all the inherited properties from the abstract interfaces
        # implemented by this instance
        props = {}
        for base in self._bases:
            for name, value in base.__dict__.items():
                if not name.startswith('_') and isinstance(value, property):
                    props[name] = value
        return props


    def __getattr__(self, key):
        # Attribute lookup metamethod overloading.
        if key in self._inherited_methods:
            # The attribute is a method defined in one of the abstract classes.
            return MethodType(self._inherited_methods[key], self)

        if key in self._inherited_properties:
            prop = self._inherited_properties[key]
            if hasattr(prop, 'fget'):
                # The attribute is a property with getter defined in one of the abstract
                # classes.
                return prop.fget(self)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


    def __setattr__(self, key, value):
        # Attribute setter metamethod overloading.
        if key in self._inherited_properties:
            prop = self._inherited_properties[key]
            if hasattr(prop, 'fset'):
                # The attribute is a property with setter defined in one of the abstract classes.
                # Invoke the setter with the given value.
                prop.fset(self, value)
                return
        object.__setattr__(self, key, value)


    def __dir__(self):
        entries = super().__dir__()
        # Add implemented properties & methods to dir entries
        entries.extend(self._inherited_methods)
        entries.extend(self._inherited_properties)
        return entries


    def __eq__(self, other):
        # Use NamedObject.__eq__ to compare this instance with the given object
        # if it implements the interface NamedObject
        if isinstance(self, NamedObject):
            return NamedObject.__eq__(self, other)
        # Otherwise, use default __eq__ implementation
        return super().__eq__(self, other)


    def __str__(self):
        # Print the object
        return _to_str(self)

    def __repr__(self):
        return self.__str__()
