'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class ObjectPrinter, which can be used to print symbols,
matrices, expressions or any other kind of object defined by this extension.

ConsoleObjectPrinter and LatexObjectPrinter are subclasses of Printer. The first one is used
to visualize objects in terminal mode and the second to print them in latex format

..note:: The class LatexObjectPrinter is defined in the module latex.pyx

                ObjectPrinter
                     ^
      ---------------|--------------
      |                            |
ObjectConsolePrinter          ObjectLatexPrinter

'''



######## Class printer ########

cdef class ObjectPrinter:
    '''
    Subclasses of Printer can be used to print any kind of objects defined by this extension:

        :Example:

        >> ConsolePrinter().print(new_param('a', 1))
        a = 1

        >> b, c = new_param('b', tex_name='\\beta'), new_param('c', tex_name='\\gamma')
        >> LatexPrinter().print(b + c)
        '\\beta+\\gamma'
    '''

    def print(self, x):
        '''
        Prints the given object using this printer.

        :param obj: The object to be printed
        :rtype: str

        :raises NotImplementedError if the object couldnt be printed
        '''
        if not isinstance(x, Object):
            raise NotImplementedError

        if isinstance(x, Expr):
            return self.print_expr(x)

        if isinstance(x, SymbolNumeric):
            return self.print_symbol(x)

        if isinstance(x, Matrix):
            return self.print_matrix(x)

        if isinstance(x, Base):
            return self.print_base(x)

        if isinstance(x, Point):
            return self.print_point(x)

        if isinstance(x, Frame):
            return self.print_frame(x)

        if isinstance(x, Wrench3D):
            return self.print_wrench(x)

        raise NotImplementedError



    def print_expr(self, Expr expr):
        # This method is used to print a expression
        raise NotImplementedError

    def print_symbol(self, SymbolNumeric symbol):
        # This method is used to print a numeric symbol
        raise NotImplementedError

    def print_matrix(self, Matrix matrix):
        # This method is used to print a matrix (including vectors and tensors)
        raise NotImplementedError

    def print_base(self, Base base):
        # This method is used to print a base
        raise NotImplementedError

    def print_point(self, Point point):
        # This method is used to print a point
        raise NotImplementedError

    def print_frame(self, Frame frame):
        # This method is used to print a frame (also solids)
        raise NotImplementedError

    def print_wrench(self, Wrench3D wrench):
        # This method is used to print a wrench
        raise NotImplementedError










######## Class ConsolePrinter ########


cdef class ObjectConsolePrinter(ObjectPrinter):
    '''
    Specialization of the class Printer to print objects in terminal mode.
    '''

    cpdef print_expr(self, Expr expr):
        # This method is used to print a expression

        cdef c_ginac_printer* c_printer = new c_ginac_python_printer(c_sstream())
        expr._c_handler.print(c_deref(c_printer))
        x = (<bytes>(<c_sstream*>&c_printer.s).str()).decode()
        del c_printer

        try:
            # Try to format the expression as a number (remove decimals if its integer)
            x = float(x)
            if floor(x) == x:
                x = floor(x)
            else:
                x = round(x, 4)
            return str(x)
        except:
            # Otherwise, returns the whole expression as-is
            return x



    cpdef print_symbol(self, SymbolNumeric symbol):
        # This method is used to print numeric symbols
        return f'{symbol.get_name()} = {round(symbol.get_value(), 4)}'



    cpdef print_matrix(self, Matrix matrix):
        # This method is used to print matrices (including vectors and tensors)

        values = tuple(map(str, matrix.get_values()))
        n, m = matrix.get_shape()
        if m == 1:
            m, n = n, 1

        col_sizes = [max([len(values[i*m + j]) for i in range(0, n)])+1 for j in range(0, m)]
        delimiters = '[]' if n == 1 or m == 1 else '\u2502'*2

        lines = []
        for i in range(0, n):
            line = ' '.join([values[i*m + j].rjust(col_size) for j, col_size in zip(range(0, m), col_sizes)])
            line = delimiters[0] + line + ' ' + delimiters[1]
            lines.append(line)

        if n > 1 and m > 1:
            # Insert decoratives
            row_width = len(lines[0]) - 2
            head = '\u256d' + ' '*row_width + '\u256e'
            tail = '\u2570' + ' '*row_width + '\u256f'
            lines.insert(0, head)
            lines.append(tail)

        return '\n'.join(lines)



    cpdef print_base(self, Base base):
        # This method is used to print bases

        s = f'Base {base.name}'

        if base.has_previous():
            ancestors = []
            prev = base.get_previous()
            ancestors.append(prev)
            while prev.has_previous():
                prev = prev.get_previous()
                ancestors.append(prev)

            s += ', ancestors: ' + ' -> '.join(map(attrgetter('name'), ancestors))

        return s
