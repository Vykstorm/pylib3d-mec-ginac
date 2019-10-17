'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class Printer, which can be used to print symbols,
matrices, expressions or any other kind of object defined by this extension.

ConsolePrinter and LatexPrinter are subclasses of Printer. The first one is used
to visualize objects in terminal mode and the second to print them in latex format

..note:: The class LatexPrinter is defined in the module latex.pyx
'''



######## Class printer ########

cdef class Printer:
    '''
    Subclasses of Printer can be used to print any kind of object which inherits from
    Object class:

        :Example:

        >> printer = ConsolePrinter()

        # Print a symbol
        >> printer.print(new_param('a', 1))
        a = 1

        # Print a expression
        >> b, c = new_param('b', tex_name='\\beta', 2), new_param('c', tex_name='\\gamma', 3)
        >> printer.print(b + c)
        '\\beta+\\gamma'

        # Print a table of parameters (a view)
        >> printer.print(get_params())
        name   value
        a        1.0
        b        2.0
        c        3.0
    '''

    def print(self, x):
        '''
        Prints the given object or view using this printer.

        :param obj: The object to be printed
        :rtype: str

        :raises NotImplementedError if the object couldnt be printed
        '''
        if isinstance(x, Object):
            return self.print_object(x)
        if isinstance(x, View):
            return self.print_view(x)
        raise NotImplementedError



    def print_object(self, Object obj):
        if isinstance(obj, Expr):
            return self.print_expr(obj)

        if isinstance(obj, SymbolNumeric):
            return self.print_symbol(obj)

        if isinstance(obj, Matrix):
            return self.print_matrix(obj)

        if isinstance(obj, Base):
            return self.print_base(obj)

        if isinstance(obj, Point):
            return self.print_point(obj)

        if isinstance(obj, Frame):
            return self.print_frame(obj)

        if isinstance(obj, Wrench3D):
            return self.print_wrench(obj)

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




    def print_view(self, View view):
        # This method is used to print views
        if isinstance(view, TableView):
            return self.print_table_view(view)
        raise NotImplementedError


    def print_table_view(self, TableView table_view):
        raise NotImplementedError









######## Class ConsolePrinter ########


cdef class ConsolePrinter(Printer):
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

        if isinstance(matrix, Vector3D):
            return self.print_vector(matrix)

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



    cpdef print_vector(self, Vector3D vector):
        lines = map(str, vector)
        return '[\n' + ',\n'.join(lines) + '\n] ' + f'base "{vector.base.name}"'




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




    cpdef print_table_view(self, TableView table_view):
        # This method is used to print table views
        return tabulate(table_view.data, table_view.headers, tablefmt='plain')
