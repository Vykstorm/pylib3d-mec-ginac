'''
Author: Víctor Ruiz Gómez
Description:


This file defines the base class for SymbolNumeric, Expr, Matrix, Vector3D,
Tensor3D, Base, Point and Frame classes

The base class is called "Object", and it defines a few properties
& methods:

* get_name method and "name" property avaliable for:
SymbolNumeric, Matrix, Vector3D, Tensor3D, Base, Point and Frame

* print_latex, to_latex methods and "latex" property for:
SymbolNumeric, Expr, Matrix, Vector3D and Tensor3D

* get_base, in_base methods and "base" property for:
Vector3D, Tensor3D and Frame
'''



######## Mixin classes ########


class NamedObject(ABC):
    def __eq__(self, other):
        return (self is other) or ((type(self) == type(other)) and self.get_name() == other.get_name())

    @property
    def name(self):
        return self.get_name()

    def get_name(self):
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




class LatexRenderable(ABC):

    def print_latex(self):
        _print_latex_ipython(self.to_latex())

    def to_latex(self):
        return _to_latex(self)

    @property
    def latex(self):
        return self.to_latex()




class GeometricObject(ABC):

    def get_base(self):
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
        raise NotImplementedError()

    @property
    def base(self):
        return self.get_base()

    @base.setter
    def base(self, x):
        self.in_base(x)





######## Class Object ########


cdef class Object:
    '''
    This is the base class of Expr, SymbolNumeric, Base, Matrix, Vector and Point
    classes
    '''

    @property
    def _bases(self):
        return [cls for cls in (NamedObject, LatexRenderable, GeometricObject) if isinstance(self, cls)]

    @property
    def _inherited_methods(self):
        methods = {}
        for base in self._bases:
            for name, value in base.__dict__.items():
                if not name.startswith('_') and callable(value):
                    methods[name] = value
        return methods


    @property
    def _inherited_properties(self):
        props = {}
        for base in self._bases:
            for name, value in base.__dict__.items():
                if not name.startswith('_') and isinstance(value, property):
                    props[name] = value
        return props


    def __getattr__(self, key):
        if key in self._inherited_methods:
            return MethodType(self._inherited_methods[key], self)

        if key in self._inherited_properties:
            prop = self._inherited_properties[key]
            if hasattr(prop, 'fget'):
                return prop.fget(self)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


    def __setattr__(self, key, value):
        if key in self._inherited_properties:
            prop = self._inherited_properties[key]
            if hasattr(prop, 'fset'):
                prop.fset(self, value)
                return
        object.__setattr__(self, key, value)


    def __dir__(self):
        entries = super().__dir__()
        entries.extend(self._inherited_methods)
        entries.extend(self._inherited_properties)
        return entries


    def __eq__(self, other):
        if isinstance(self, NamedObject) and isinstance(other, NamedObject):
            return NamedObject.__eq__(self, other)
        return super().__eq__(self, other)

    def __str__(self):
        return _to_str(self)

    def __repr__(self):
        return self.__str__()
