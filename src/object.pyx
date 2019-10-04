'''
Author: Víctor Ruiz Gómez
Description: This file defines the class Object which is the base class of the
rest of the classes defined by this extension (except System).
'''



######## Mixin classes ########


class NamedObject(ABC):
    pass


class LatexRenderable(ABC):
    def print_latex(self):
        try:
            from IPython.display import display, Math
        except ImportError:
            raise ImportError('You must have installed IPython to use print_latex function')
        display(Math(self.to_latex()))




######## Class Object ########


cdef class Object:
    '''
    This is the base class of Expr, SymbolNumeric, Base, Matrix, Vector and Point
    classes
    '''
    def __getattr__(self, key):
        if isinstance(self, NamedObject):
            if key == 'name':
                return self.get_name()

        if isinstance(self, LatexRenderable):
            if key == 'latex':
                return self.to_latex()
            if key == 'print_latex':
                return MethodType(LatexRenderable.print_latex, self)

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")


    def __dir__(self):
        entries = super().__dir__()
        if isinstance(self, NamedObject):
            entries.append('name')
        if isinstance(self, LatexRenderable):
            entries.extend(['latex', 'print_latex'])
        return entries


    def __repr__(self):
        return self.__str__()





######## Global methods ########

def get_name(obj):
    if not isinstance(obj, NamedObject):
        raise TypeError('Invalid input argument: Expected SymbolNumeric, Base, Matrix, Vector3D or Point')
    return obj.get_name()


def to_latex(obj):
    if not isinstance(obj, LatexRenderable):
        raise TypeError('Invalid input argument: Expected SymbolNumeric, Expr, Matrix or Vector3D')
    return obj.to_latex()


def print_latex(obj):
    if not isinstance(obj, LatexRenderable):
        raise TypeError('Invalid input argument: Expected SymbolNumeric, Expr, Matrix or Vector3D')
    obj.print_latex()
