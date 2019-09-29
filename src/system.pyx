'''
Author: Víctor Ruiz Gómez
Description: This module defines the interface between Python and C++ for the
class System
'''




######## Class System ########


## Class which acts like a bridge between Python and C++ System class
cdef class _System:


    ######## C Attributes ########

    cdef c_System* _c_handler




    ######## Constructor & Destructor ########


    def __cinit__(self):
        # Initialize C++ System object
        self._c_handler = new c_System()

    def __dealloc__(self):
        del self._c_handler




    ######## C Getters ########


    cdef c_symbol_numeric_list _get_c_symbols_by_type(self, c_string kind):
        '''
        Get all symbols of the given type defined within this system
        :param kind: Kind of symbols to retrieve. e.g: 'parameter'
        :type kind: std::string
        :rtype: std::vector[symbol_numeric*]
        '''
        if kind == b'coordinate':
            return self._c_handler.get_Coordinates()
        if kind == b'velocity':
            return self._c_handler.get_Velocities()
        if kind == b'acceleration':
            return self._c_handler.get_Accelerations()
        if kind == b'aux_coordinate':
            return self._c_handler.get_AuxCoordinates()
        if kind == b'aux_velocity':
            return self._c_handler.get_AuxVelocities()
        if kind == b'aux_acceleration':
            return self._c_handler.get_AuxAccelerations()
        if kind == b'parameter':
            return self._c_handler.get_Parameters()
        if kind == b'input':
            return self._c_handler.get_Inputs()
        if kind == b'joint_unknown':
            return self._c_handler.get_Joint_Unknowns()



    cdef c_symbol_numeric_list _get_c_symbols(self):
        '''
        Get all symbols within this system
        :rtype: std::vector[symbol_numeric*]
        '''
        cdef c_vector[c_symbol_numeric_list] containers
        containers.push_back(self._c_handler.get_Coordinates())
        containers.push_back(self._c_handler.get_Velocities())
        containers.push_back(self._c_handler.get_Accelerations())
        containers.push_back(self._c_handler.get_AuxCoordinates())
        containers.push_back(self._c_handler.get_AuxVelocities())
        containers.push_back(self._c_handler.get_AuxAccelerations())
        containers.push_back(self._c_handler.get_Parameters())
        containers.push_back(self._c_handler.get_Inputs())
        containers.push_back(self._c_handler.get_Joint_Unknowns())

        cdef c_symbol_numeric_list symbols
        cdef size_t num_symbols = 0

        for container in containers:
            num_symbols += container.size()
        symbols.reserve(num_symbols)

        for container in containers:
            symbols.insert(symbols.end(), container.begin(), container.end())

        return symbols



    cdef c_vector[c_Base*] _get_c_bases(self):
        return self._c_handler.get_Bases()


    cdef c_vector[c_Matrix*] _get_c_matrices(self):
        return self._c_handler.get_Matrixs()


    cdef c_vector[c_Vector3D*] _get_c_vectors(self):
        return self._c_handler.get_Vectors()




    ######## Getters ########


    cpdef get_symbol(self, name, kind=None):
        name = _parse_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)

        # Find a numeric symbol by name
        cdef c_symbol_numeric_list c_symbols
        if kind is None:
            c_symbols = self._get_c_symbols()
        else:
            c_symbols = self._get_c_symbols_by_type(kind)

        cdef c_symbol_numeric* c_symbol
        for c_symbol in c_symbols:
            if c_symbol.get_name() == <c_string>name:
                return SymbolNumeric(<Py_ssize_t>c_symbol)

        # No symbol with such name exists
        if kind is None:
            raise IndexError(f'Symbol "{name.decode()}" not created yet')

        kind_title = kind.decode().replace("_", " ")
        if self.has_symbol(name):
            raise IndexError(f'Symbol "{name.decode()}" is not a {kind_title}')
        raise IndexError(f'{kind_title} "{name.decode()}" not created yet')



    cpdef has_symbol(self, name, kind=None):
        name = _parse_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)

        # Check if symbol exists
        cdef c_symbol_numeric_list c_symbols
        if kind is None:
            c_symbols = self._get_c_symbols()
        else:
            c_symbols = self._get_c_symbols_by_type(kind)

        for c_symbol in c_symbols:
            if c_symbol.get_name() == <c_string>name:
                return True
        return False



    cpdef get_symbols(self):
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols()
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return symbols



    cpdef get_symbols_by_type(self, kind=None):
        if kind is None:
            return _System.get_symbols(self)
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols_by_type(_parse_symbol_type(kind))
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol) for c_symbol in c_symbols]
        return symbols



    cpdef _get_geom_obj(self, name, kind):
        name, kind = _parse_name(name), _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_vector[c_Vector3D*] c_vectors
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix
        cdef c_Vector3D* c_vector

        if kind == b'base':
            c_bases = self._get_c_bases()
            for c_base in c_bases:
                if c_base.get_name() == <c_string>name:
                    return Base(<Py_ssize_t>c_base)
            raise IndexError(f'Base "{name.decode()}" not created yet')

        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            for c_matrix in c_matrices:
                if c_matrix.get_name() == <c_string>name:
                    return _matrix_from_c(c_matrix)
            raise IndexError(f'Matrix "{name.decode()}" not created yet')

        elif kind == b'vector':
            c_vectors = self._get_c_vectors()
            for c_vector in c_vectors:
                if c_vector.get_name() == <c_string>name:
                    return _vector_from_c(c_vector)
            raise IndexError(f'Vector "{name.decode()}" not created yet')
        else:
            raise RuntimeError




    cpdef _has_geom_obj(self, name, kind):
        name, kind =  _parse_name(name), _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_vector[c_Vector3D*] c_vectors
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix
        cdef c_Vector3D* c_vector

        if kind == b'base':
            c_bases = self._get_c_bases()
            for c_base in c_bases:
                if c_base.get_name() == <c_string>name:
                    return True
        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            for c_matrix in c_matrices:
                if c_matrix.get_name() == <c_string>name:
                    return True
        elif kind == b'vector':
            c_vectors = self._get_c_vectors()
            for c_vector in c_vectors:
                if c_vector.get_name() == <c_string>name:
                    return True
            return False
        else:
            raise RuntimeError

        return False



    cpdef _get_geom_objs(self, kind):
        kind = _parse_geom_obj_type(kind)

        cdef c_vector[c_Base*] c_bases
        cdef c_vector[c_Matrix*] c_matrices
        cdef c_vector[c_Vector3D*] c_vectors
        cdef c_Base* c_base
        cdef c_Matrix* c_matrix
        cdef c_Vector3D* c_vector

        if kind == b'base':
            c_bases = self._get_c_bases()
            return [Base(<Py_ssize_t>c_base) for c_base in c_bases]
        elif kind == b'matrix':
            c_matrices = self._get_c_matrices()
            return [_matrix_from_c(c_matrix) for c_matrix in c_matrices]
        elif kind == b'vector':
            c_vectors = self._get_c_vectors()
            return [_vector_from_c(c_vector) for c_vector in c_vectors]
        else:
            raise RuntimeError




    ######## Constructors ########


    cdef c_symbol_numeric* _new_c_parameter(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Parameter(name, tex_name, c_numeric(value))


    cdef c_symbol_numeric* _new_c_input(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Input(name, tex_name, c_numeric(value))


    cdef c_symbol_numeric* _new_c_joint_unknown(self, c_string name, c_string tex_name, double value):
        return self._c_handler.new_Joint_Unknown(name, tex_name, c_numeric(value))


    cdef c_symbol_numeric* _new_c_aux_coordinate(self,
        c_string name,     c_string vel_name,     c_string acc_name,
        c_string tex_name, c_string vel_tex_name, c_string acc_tex_name,
        double   value,    double   vel_value,    double   acc_value):
        return self._c_handler.new_AuxCoordinate(
            name, vel_name, acc_name,
            tex_name, vel_tex_name, acc_tex_name,
            c_numeric(value), c_numeric(vel_value), c_numeric(acc_value))


    cdef c_symbol_numeric* _new_c_coordinate(self,
        c_string name,     c_string vel_name,     c_string acc_name,
        c_string tex_name, c_string vel_tex_name, c_string acc_tex_name,
        double   value,    double   vel_value,    double   acc_value):
        return self._c_handler.new_Coordinate(
            name, vel_name, acc_name,
            tex_name, vel_tex_name, acc_tex_name,
            c_numeric(value), c_numeric(vel_value), c_numeric(acc_value))



    cpdef new_symbol(self, kind, args, kwargs):
        # Validate & parse input arguments
        args = list(args)
        kind = _parse_symbol_type(kind)
        if kind in _derivable_symbol_types:
            raise ValueError(f'You cant create a {kind.decode().replace("_", " ")} symbol by hand')

        cdef c_symbol_numeric* c_symbol
        cdef c_symbol_numeric* vel_c_symbol
        cdef c_symbol_numeric* acc_c_symbol


        # Signature of the method depends on the type of symbol
        if kind in (b'parameter', b'input', b'joint_unknown'):
            # Parse optional arguments
            if not kwargs and len(args) == 2:
                if not isinstance(args[-1], (str, bytes)):
                    kwargs['value'] = args.pop()

            name, tex_name, value = _apply_signature(
                ['name', 'tex_name', 'value'],
                {'tex_name': b'', 'value': 0.0},
                args, kwargs
            )
            name, tex_name, value = _parse_name(name), _parse_tex_name(tex_name), _parse_numeric_value(value)

            # Check if a symbol with the name specified already exists
            if self.has_symbol(name):
                raise IndexError(f'A symbol with the name "{name.decode()}" already exists')

            # Apply a different constructor for each symbol type
            if kind == b'parameter':
                c_symbol = self._new_c_parameter(name, tex_name, value)
            elif kind == b'input':
                c_symbol = self._new_c_input(name, tex_name, value)
            elif kind == b'joint_unknown':
                c_symbol = self._new_c_joint_unknown(name, tex_name, value)

            return SymbolNumeric(<Py_ssize_t>c_symbol)


        elif kind.endswith(b'coordinate'):
            # Parse optional arguments
            if not kwargs and len(args) in range(1, 10):
                kwargs['name'] = args.pop(0)

                params = ['vel_name', 'acc_name', 'tex_name', 'vel_tex_name', 'acc_tex_name']
                while args and params and isinstance(args[0], (str, bytes)):
                    kwargs[params.pop(0)] = args.pop(0)

                params = ['value', 'vel_value', 'acc_value']
                while args and params:
                    kwargs[params.pop(0)] = args.pop(0)

            bounded_args = _apply_signature(
                ['name', 'vel_name', 'acc_name', 'tex_name', 'vel_tex_name', 'acc_tex_name', 'value', 'vel_value', 'acc_value'],
                {'vel_name': None, 'acc_name': None, 'tex_name': None, 'vel_tex_name': None, 'acc_tex_name': None,
                'value': 0.0, 'vel_value': 0.0, 'acc_value': 0.0},
                args, kwargs
            )

            names = [_parse_name(arg) if arg is not None else None for arg in bounded_args[:3]]
            tex_names = [_parse_tex_name(arg) if arg is not None else None for arg in bounded_args[3:6]]
            values = [_parse_numeric_value(arg) for arg in bounded_args[6:9]]

            names[1:] = [name or b'd'*k + names[0] for k, name in enumerate(names[1:], 1)]
            if tex_names[0]:
                tex_names[1:] = [tex_name or b'\\' + b'd'*k + b'ot{' + tex_names[0] + b'}' for k, tex_name in enumerate(tex_names[1:], 1)]
            else:
                tex_names = [tex_name or b'' for tex_name in tex_names]


            # Check if the name of the coordinate or its components is already in use by other symbol
            for name in names:
                if self.has_symbol(name):
                    raise IndexError(f'A symbol with the name "{name.decode()}" already exists')

            # Apply a different constructor for each symbol type
            if kind.startswith(b'aux_'):
                c_symbol = self._new_c_aux_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
                vel_c_symbol, acc_c_symbol = self._c_handler.get_AuxVelocity(names[1]), self._c_handler.get_AuxAcceleration(names[2])
            else:
                c_symbol = self._new_c_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
                vel_c_symbol, acc_c_symbol = self._c_handler.get_Velocity(names[1]), self._c_handler.get_Acceleration(names[2])

            return SymbolNumeric(<Py_ssize_t>c_symbol), SymbolNumeric(<Py_ssize_t>vel_c_symbol), SymbolNumeric(<Py_ssize_t>acc_c_symbol)

        else:
            raise RuntimeError




    cpdef new_base(self, name, args, kwargs):
        # Validate & parse base name
        name = _parse_name(name)


        # Check if a base with the given name already exists
        if self.has_base(name):
            raise IndexError(f'Base "{name.decode()}" already exists')

        # Validate & parse previous base, rotation tupla and angle arguments
        args = list(args)

        if args:
            new_args = []
            if not isinstance(args[0], (str, bytes, Base)):
                new_args.append(None)
            else:
                new_args.append(args.pop(0))

            if len(args) > 2:
                rotation_tupla = args[:3]
                args = args[3:]
                new_args.append(rotation_tupla)
            new_args.extend(args)
            args = new_args

        previous, rotation_tupla, rotation_angle = _apply_signature(
            ['previous', 'rotation_tupla', 'rotation_angle'],
            {'previous': None, 'rotation_tupla': (0, 0, 0), 'rotation_angle': 0},
            args, kwargs
        )

        if previous is not None:
            if not isinstance(previous, Base):
                try:
                    previous = self.get_base(previous)
                except IndexError as e:
                    raise ValueError(*e.args)
        else:
            previous = self.get_base(b'xyz')

        if not isinstance(rotation_tupla, (Iterable, Matrix)):
            raise TypeError(f'Rotation tupla must be an iterable or a Matrix object')

        if len(rotation_tupla) != 3:
            raise ValueError(f'Rotation tupla must have exactly three components')

        rotation_tupla = tuple(rotation_tupla)
        rotation_tupla = tuple(map(Expr, rotation_tupla))
        rotation_angle = Expr(rotation_angle)

        # Finally create the base
        cdef c_ex a, b, c, d
        cdef c_Base* c_prev_base

        c_prev_base = (<Base>previous)._c_handler
        a = (<Expr>rotation_tupla[0])._c_handler
        b = (<Expr>rotation_tupla[1])._c_handler
        c = (<Expr>rotation_tupla[2])._c_handler
        d = (<Expr>rotation_angle)._c_handler

        return Base(<Py_ssize_t>self._c_handler.new_Base(name, c_prev_base.get_name(), a, b, c, d))



    cpdef new_matrix(self, name, args, kwargs):
        # Validate & parse name argument
        name = _parse_name(name)

        # Check if a matrix with the same name already exists
        if self.has_matrix(name):
            raise IndexError(f'Matrix "{name.decode()}" already exists')

        # Create the matrix
        matrix = Matrix(*args, **kwargs)

        # Register the matrix with the given name in the system
        cdef c_Matrix* c_matrix = matrix._get_c_handler()
        c_matrix.set_name(name)
        self._c_handler.new_Matrix(c_matrix)
        (<Matrix>matrix)._owns_c_handler = False

        return matrix


    cpdef new_vector(self, name, args, kwargs):
        # Validate & parse name argument
        name = _parse_name(name)

        # Check if a matrix with the same name already exists
        if self.has_vector(name):
            raise IndexError(f'Vector "{name.decode()}" already exists')

        # Create the vector
        kwargs['system'] = self
        vector = Vector3D(*args, **kwargs)

        # Register the matrix with the given name in the system
        cdef c_Vector3D* c_vector = <c_Vector3D*>vector._get_c_handler()
        c_vector.set_name(name)
        self._c_handler.new_Vector3D(c_vector)
        (<Vector3D>vector)._owns_c_handler = False

        return vector
