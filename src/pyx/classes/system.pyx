'''
Author: Víctor Ruiz Gómez
Description: This module defines the interface between Python and C++ for the
class System
'''


######## Helper types, variables & methods ########

cdef void outError(const char* msg):
    # Redefinition of outError function (to suppress error messages)
    #print((<bytes>msg).decode())
    pass



# C type alias representing a list of numeric symbols (std::vector[symbol_numeric*])
ctypedef c_vector[c_symbol_numeric*] c_symbol_numeric_list


# All numeric symbol types
_symbol_types = frozenset(map(str.encode, (
    'coordinate', 'velocity', 'acceleration',
    'aux_coordinate', 'aux_velocity', 'aux_acceleration',
    'parameter', 'joint_unknown', 'input'
)))

# All symbol types that cannot be created by the user (they are generated
# automatically when other kind of symbols are created)
_derivable_symbol_types = frozenset(map(str.encode, (
    'velocity', 'acceleration', 'aux_velocity', 'aux_acceleration'
)))

# All geometric object types
_geom_types = frozenset(map(str.encode, (
    'matrix', 'vector', 'tensor', 'base', 'point', 'frame', 'solid', 'wrench'
)))




######## Class System ########


## Class which acts like a bridge between Python and C++ System class
cdef class _System:


    ######## C Attributes ########

    cdef c_System* _c_handler
    cdef bint _autogen_latex_names


    ######## Constructor & Destructor ########


    def __cinit__(self):
        # Initialize C++ System object
        self._c_handler = new c_System(outError)

        self._autogen_latex_names = True


    def __dealloc__(self):
        del self._c_handler




    ######## C Getters ########

    cdef void* _get_c_object(self, c_string name, c_string kind):
        '''
        Get the object with the given name & type defined within this system
        :param string name: Name of the symbol
        :param string kind: Type of object ('parameter', 'vector', 'matrix', ...)
        :returns: A generic C pointer to the object or NULL if not object with such
            name or type exists
        :rtype: void*
        '''
        if kind == b'coordinate':
            return <void*>self._c_handler.get_Coordinate(name)
        if kind == b'velocity':
            return <void*>self._c_handler.get_Velocity(name)
        if kind == b'acceleration':
            return <void*>self._c_handler.get_Acceleration(name)
        if kind == b'aux_coordinate':
            return <void*>self._c_handler.get_AuxCoordinate(name)
        if kind == b'aux_velocity':
            return <void*>self._c_handler.get_AuxVelocity(name)
        if kind == b'aux_acceleration':
            return <void*>self._c_handler.get_AuxAcceleration(name)

        if kind == b'parameter':
            return <void*>self._c_handler.get_Parameter(name)
        if kind == b'joint_unknown':
            return <void*>self._c_handler.get_Unknown(name)
        if kind == b'input':
            return <void*>self._c_handler.get_Input(name)

        if kind == b'base':
            return <void*>self._c_handler.get_Base(name)
        if kind == b'matrix':
            return <void*>self._c_handler.get_Matrix(name)
        if kind == b'vector':
            return <void*>self._c_handler.get_Vector3D(name)
        if kind == b'tensor':
            return <void*>self._c_handler.get_Tensor3D(name)
        if kind == b'point':
            return <void*>self._c_handler.get_Point(name)
        if kind == b'frame':
            return <void*>self._c_handler.get_Frame(name)
        if kind == b'solid':
            return <void*>self._c_handler.get_Solid(name)
        if kind == b'wrench':
            return <void*>self._c_handler.get_Wrench3D(name)
        return NULL



    cdef bint _has_c_object(self, c_string name, c_string kind):
        '''
        Check if an object with the given name & type exists within this system
        :param string name: Name of the symbol
        :param string kind: Type of the object ('parameter', 'vector', 'matrix', ...)
        :returns: 1 if the object exists. 0 otherwise
        :rtype: bint
        '''
        return self._get_c_object(name, kind) != NULL



    cdef c_symbol_numeric_list _get_c_symbols(self, c_string kind):
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



    cdef c_Matrix _get_c_symbols_matrix(self, c_string kind):
        '''
        Get the matrix for the symbols of the given type.
        :param string kind: Must be the type of symbols to include in the resulting matrix
        :rtype: Matrix
        '''
        if kind == b'coordinate':
            return self._c_handler.Coordinates()
        if kind == b'velocity':
            return self._c_handler.Velocities()
        if kind == b'acceleration':
            return self._c_handler.Accelerations()
        if kind == b'aux_coordinate':
            return self._c_handler.Aux_Coordinates()
        if kind == b'aux_velocity':
            return self._c_handler.Aux_Velocities()
        if kind == b'aux_acceleration':
            return self._c_handler.Aux_Accelerations()
        if kind == b'parameter':
            return self._c_handler.Parameters()
        if kind == b'input':
            return self._c_handler.Inputs()
        if kind == b'joint_unknown':
            return self._c_handler.Joint_Unknowns()




    cdef c_symbol_numeric_list _get_all_c_symbols(self):
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
        num_symbols += 1
        symbols.reserve(num_symbols)

        for container in containers:
            symbols.insert(symbols.end(), container.begin(), container.end())
        symbols.push_back(&self._c_handler.t)

        return symbols



    cdef c_vector[c_Base*] _get_c_bases(self):
        '''
        Get all bases defined within this system
        :rtype: std::vector[Base*]
        '''
        return self._c_handler.get_Bases()


    cdef c_vector[c_Matrix*] _get_c_matrices(self):
        '''
        Get all matrices defined within this system
        :rtype: std::vector[Matrix*]
        '''
        return self._c_handler.get_Matrixs()


    cdef c_vector[c_Vector3D*] _get_c_vectors(self):
        '''
        Get all vectors defined within this system
        :rtype: std::vector[Vector3D*]
        '''
        return self._c_handler.get_Vectors()


    cdef c_vector[c_Tensor3D*] _get_c_tensors(self):
        return self._c_handler.get_Tensors()


    cdef c_vector[c_Point*] _get_c_points(self):
        '''
        Get all points defined within this system
        :rtype: std::vector[Point*]
        '''
        return self._c_handler.get_Points()


    cdef c_vector[c_Frame*] _get_c_frames(self):
        return self._c_handler.get_Frames()


    cdef c_vector[c_Solid*] _get_c_solids(self):
        return self._c_handler.get_Solids()


    cdef c_vector[c_Wrench3D*] _get_c_wrenches(self):
        return self._c_handler.get_Wrenches()




    ######## Getters ########


    cpdef _get_symbol(self, name, kind=None):
        cdef c_symbol_numeric *c_symbol
        cdef c_symbol_numeric *x
        cdef c_symbol_numeric_list c_symbols

        name = _parse_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)
            c_symbol = <c_symbol_numeric*>self._get_c_object(name, kind)
        else:
            c_symbols = self._get_all_c_symbols()
            c_symbol = NULL
            for x in c_symbols:
                if x.get_name() == <c_string>name:
                    c_symbol = x

        if c_symbol != NULL:
            return SymbolNumeric(<Py_ssize_t>c_symbol, self)

        if kind is None:
            raise IndexError(f'Symbol "{name.decode()}" not created yet')
        kind_title = kind.decode().replace("_", " ")
        if self._has_symbol(name):
            raise IndexError(f'Symbol "{name.decode()}" is not a {kind_title}')
        raise IndexError(f'{kind_title} "{name.decode()}" not created yet')



    cpdef _has_symbol(self, name, kind=None):
        cdef c_symbol_numeric_list c_symbols
        cdef c_symbol_numeric* x

        name = _parse_name(name)
        if kind is not None:
            kind = _parse_symbol_type(kind)
            return self._has_c_object(name, kind)

        c_symbols = self._get_all_c_symbols()
        for x in c_symbols:
            if x.get_name() == <c_string>name:
                return True
        return False


    cpdef _get_symbols_matrix(self, kind):
        cdef c_Matrix c_matrix = self._get_c_symbols_matrix(_parse_symbol_type(kind))
        return _matrix_from_c_value(c_matrix)



    cpdef _get_time(self):
        return SymbolNumeric(<Py_ssize_t>&self._c_handler.t, self)



    cpdef _get_base(self, name):
        name = _parse_name(name)
        cdef c_Base* c_base = <c_Base*>self._get_c_object(name, b'base')
        if c_base == NULL:
            raise IndexError(f'Base "{name.decode()}" doesnt exist')
        return Base(<Py_ssize_t>c_base)


    cpdef _get_matrix(self, name):
        name = _parse_name(name)
        cdef c_Matrix* c_matrix = <c_Matrix*>self._get_c_object(name, b'matrix')
        if c_matrix == NULL:
            raise IndexError(f'Matrix "{name.decode()}" doesnt exist')
        return _matrix_from_c(c_matrix)


    cpdef _get_vector(self, name):
        name = _parse_name(name)
        cdef c_Vector3D* c_vector = <c_Vector3D*>self._get_c_object(name, b'vector')
        if c_vector == NULL:
            raise IndexError(f'Vector "{name.decode()}" doesnt exist')
        return _vector_from_c(c_vector)


    cpdef _get_tensor(self, name):
        name = _parse_name(name)
        cdef c_Tensor3D* c_tensor = <c_Tensor3D*>self._get_c_object(name, b'tensor')
        if c_tensor == NULL:
            raise IndexError(f'Tensor "{name.decode()}" doesnt exist')
        return _tensor_from_c(c_tensor)



    cpdef _get_point(self, name):
        name = _parse_name(name)
        cdef c_Point* c_point = <c_Point*>self._get_c_object(name, b'point')
        if c_point == NULL:
            raise IndexError(f'Point "{name.decode()}" doesnt exist')
        return Point(<Py_ssize_t>c_point)


    cpdef _get_frame(self, name):
        name = _parse_name(name)
        cdef c_Frame* c_frame = <c_Frame*>self._get_c_object(name, b'frame')
        if c_frame == NULL:
            raise IndexError(f'Frame "{name.decode()}" doesnt exist')
        return Frame(<Py_ssize_t>c_frame)


    cpdef _get_solid(self, name):
        name = _parse_name(name)
        cdef c_Solid* c_solid = <c_Solid*>self._get_c_object(name, b'solid')
        if c_solid == NULL:
            raise IndexError(f'Solid "{name.decode()}" doesnt exist')
        return Solid(<Py_ssize_t>c_solid)


    cpdef _get_wrench(self, name):
        name = _parse_name(name)
        cdef c_Wrench3D* c_wrench = <c_Wrench3D*>self._get_c_object(name, b'wrench')
        if c_wrench == NULL:
            raise IndexError(f'Wrench "{name.decode()}" doesnt exist')
        return _wrench_from_c(c_wrench)




    cpdef _has_base(self, name):
        return self._has_c_object(_parse_name(name), b'base')

    cpdef _has_matrix(self, name):
        return self._has_c_object(_parse_name(name), b'matrix')

    cpdef _has_vector(self, name):
        return self._has_c_object(_parse_name(name), b'vector')

    cpdef _has_tensor(self, name):
        return self._has_c_object(_parse_name(name), b'tensor')

    cpdef _has_point(self, name):
        return self._has_c_object(_parse_name(name), b'point')

    cpdef _has_frame(self, name):
        return self._has_c_object(_parse_name(name), b'frame')

    cpdef _has_solid(self, name):
        return self._has_c_object(_parse_name(name), b'solid')

    cpdef _has_wrench(self, name):
        return self._has_c_object(_parse_name(name), b'wrench')




    cpdef _has_object(self, name):
        name = _parse_name(name)
        if self._has_symbol(name):
            return True
        if self._has_base(name):
            return True
        if self._has_matrix(name) or self._has_vector(name):
            return True
        if self._has_point(name) or self._has_frame(name):
            return True
        if self._has_solid(name) or self._has_wrench(name):
            return True
        return False





    ######## Container getters ########


    cpdef _get_all_symbols(self):
        cdef c_symbol_numeric_list c_symbols = self._get_all_c_symbols()
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol, self) for c_symbol in c_symbols]
        return symbols


    cpdef _get_symbols(self, kind=None):
        if kind is None:
            return self._get_all_symbols()
        cdef c_symbol_numeric_list c_symbols = self._get_c_symbols(_parse_symbol_type(kind))
        symbols = [SymbolNumeric(<Py_ssize_t>c_symbol, self) for c_symbol in c_symbols]
        return symbols


    cpdef _get_bases(self):
        cdef c_vector[c_Base*] c_bases = self._c_handler.get_Bases()
        return [Base(<Py_ssize_t>c_base) for c_base in c_bases]

    cpdef _get_matrices(self):
        cdef c_vector[c_Matrix*] c_matrices = self._c_handler.get_Matrixs()
        return [_matrix_from_c(c_matrix) for c_matrix in c_matrices]

    cpdef _get_vectors(self):
        cdef c_vector[c_Vector3D*] c_vectors = self._c_handler.get_Vectors()
        return [_vector_from_c(c_vector) for c_vector in c_vectors]

    cpdef _get_tensors(self):
        cdef c_vector[c_Tensor3D*] c_tensors = self._c_handler.get_Tensors()
        return [_tensor_from_c(c_tensor) for c_tensor in c_tensors]

    cpdef _get_points(self):
        cdef c_vector[c_Point*] c_points = self._c_handler.get_Points()
        return [Point(<Py_ssize_t>c_point) for c_point in c_points]

    cpdef _get_frames(self):
        cdef c_vector[c_Frame*] c_frames = self._c_handler.get_Frames()
        return [Frame(<Py_ssize_t>c_frame) for c_frame in c_frames]

    cpdef _get_solids(self):
        cdef c_vector[c_Solid*] c_solids = self._c_handler.get_Solids()
        return [Solid(<Py_ssize_t>c_solid) for c_solid in c_solids]

    cpdef _get_wrenches(self):
        cdef c_vector[c_Wrench3D*] c_wrenches = self._c_handler.get_Wrenches()
        return [_wrench_from_c(c_wrench) for c_wrench in c_wrenches]




    ######## C Constructors ########


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





    ######## Constructors ########


    cpdef _new_symbol(self, kind, args, kwargs):
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
            name = _parse_name(name, check_syntax=True)
            value = _parse_numeric_value(value)

            if tex_name or not self._autogen_latex_names:
                tex_name = _parse_text(tex_name)
            else:
                # Auto generate latex name
                tex_name = _gen_latex_name(name)


            # Check if a symbol with the name specified already exists
            if self._has_object(name):
                if self._has_symbol(name, kind):
                    # The symbol already exists and has the same type
                    # Only update its latex name and value

                    # Print a warning message
                    warn(f'{kind.decode().replace("_", " ")} "{name.decode()}" already exists. Updating only its latex name and value', UserWarning)

                    symbol = self._get_symbol(name, kind)
                    symbol.set_value(value)
                    symbol.set_tex_name(tex_name)
                    return symbol

                raise IndexError(f'Name "{name.decode()}" its already in use')


            # Apply a different constructor for each symbol type
            if kind == b'parameter':
                c_symbol = self._new_c_parameter(name, tex_name, value)
            elif kind == b'input':
                c_symbol = self._new_c_input(name, tex_name, value)
            elif kind == b'joint_unknown':
                c_symbol = self._new_c_joint_unknown(name, tex_name, value)

            return SymbolNumeric(<Py_ssize_t>c_symbol, self)


        elif kind.endswith(b'coordinate'):
            # Bind input arguments to signature

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
                {'vel_name': b'', 'acc_name': b'', 'tex_name': b'', 'vel_tex_name': b'', 'acc_tex_name': b'',
                'value': 0.0, 'vel_value': 0.0, 'acc_value': 0.0},
                args, kwargs
            )

            # Validate & parse coordinate names
            names = [_parse_text(arg) for arg in bounded_args[:3]]
            names[0] = _parse_name(names[0], check_syntax=True)
            names[1:] = [_parse_name(name, check_syntax=True) if name else (b'd'*k + names[0]) for k, name in enumerate(names[1:], 1)]

            # Validate & parse latex names
            tex_names = [_parse_text(arg) for arg in bounded_args[3:6]]

            # Validate & parse values
            values = [_parse_numeric_value(arg) for arg in bounded_args[6:9]]

            # Auto generate latex
            if self._autogen_latex_names:
                if not tex_names[0]:
                    tex_names[0] = _gen_latex_name(names[0])
                if tex_names[0]:
                    tex_names[1:] = [tex_name or b'\\' + b'd'*k + b'ot{' + tex_names[0] + b'}' for k, tex_name in enumerate(tex_names[1:], 1)]


            # Check if the name of the coordinate or its components is already in use by other symbol
            symbol_types = [b'coordinate', b'velocity', b'acceleration']
            if kind.startswith(b'aux_'):
                symbol_types = [b'aux_' + symbol_type for symbol_type in symbol_types]

            if all(starmap(self._has_symbol, zip(names, symbol_types))):
                # The coordinate and its derivatives already exists.
                # Only update their values and latex names
                symbols = tuple(starmap(self._get_symbol, zip(names, symbol_types)))

                # Print a warning message
                warn(f'Coordinate "{names[0].decode()}" and its derivatives already exists. Updating only their values and latex names', UserWarning)

                for symbol, tex_name, value in zip(symbols, tex_names, values):
                    symbol.set_tex_name(tex_name)
                    symbol.set_value(value)

                return symbols


            for name in names:
                if self._has_object(name):
                    raise IndexError(f'Name "{name.decode()}" its already in use')


            # Apply a different constructor for each symbol type
            if kind.startswith(b'aux_'):
                c_symbol = self._new_c_aux_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
                vel_c_symbol, acc_c_symbol = self._c_handler.get_AuxVelocity(names[1]), self._c_handler.get_AuxAcceleration(names[2])
            else:
                c_symbol = self._new_c_coordinate(names[0], names[1], names[2], tex_names[0], tex_names[1], tex_names[2], values[0], values[1], values[2])
                vel_c_symbol, acc_c_symbol = self._c_handler.get_Velocity(names[1]), self._c_handler.get_Acceleration(names[2])

            return SymbolNumeric(<Py_ssize_t>c_symbol, self), SymbolNumeric(<Py_ssize_t>vel_c_symbol, self), SymbolNumeric(<Py_ssize_t>acc_c_symbol, self)

        else:
            raise RuntimeError




    cpdef _new_base(self, name, args, kwargs):
        # Validate & parse base name
        name = _parse_name(name, check_syntax=True)

        # Check if a base with the given name already exists
        if self._has_object(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

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
                    previous = self._get_base(previous)
                except IndexError as e:
                    raise ValueError(*e.args)
        else:
            previous = self._get_base(b'xyz')

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



    cpdef _new_matrix(self, name, args, kwargs):
        # Validate & parse name argument
        name = _parse_name(name, check_syntax=True)

        # Check if an object with the same name already exists
        if self._has_object(name) and not self._has_matrix(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        # Create the matrix
        matrix = Matrix(*args, **kwargs)
        cdef c_Matrix* c_matrix = (<Matrix>matrix)._get_c_handler()


        if self._has_matrix(name):
            # An existing matrix with the same name already exists.
            # Only update its values
            warn(f'Matrix "{name.decode()}" already exists. Only updating its values', UserWarning)
            _matrix = self._get_matrix(name)
            (<Matrix>_matrix)._get_c_handler().set_matrix(c_matrix.get_matrix())
            return _matrix


        # Register the matrix with the given name in the system
        c_matrix.set_name(name)
        self._c_handler.new_Matrix(c_matrix)
        (<Matrix>matrix)._owns_c_handler = False
        return matrix



    cpdef _new_vector(self, name, args, kwargs):
        # Validate & parse name argument
        name = _parse_name(name, check_syntax=True)

        # Check if a matrix with the same name already exists
        if self._has_object(name) and not self._has_vector(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        # Create the vector
        kwargs['system'] = self
        vector = Vector3D(*args, **kwargs)
        cdef c_Vector3D* c_vector = <c_Vector3D*>vector._get_c_handler()
        cdef c_Vector3D* _c_vector

        if self._has_vector(name):
            # Vector with the same name already exists. Only update its values and base
            warn(f'Vector "{name.decode()}" already exists. Only updating its base & values', UserWarning)

            _vector = self._get_vector(name)
            _c_vector = <c_Vector3D*>(<Vector3D>_vector)._get_c_handler()
            _c_vector.set_Base(c_vector.get_Base())
            _c_vector.set_matrix(c_vector.get_matrix())

            return _vector

        # Register the matrix with the given name in the system
        c_vector.set_name(name)
        self._c_handler.new_Vector3D(c_vector)
        (<Vector3D>vector)._owns_c_handler = False

        return vector



    cpdef _new_tensor(self, name, args, kwargs):
        name = _parse_name(name)

        if self._has_object(name) and not self._has_tensor(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        kwargs['system'] = self
        tensor = Tensor3D(*args, **kwargs)
        cdef c_Tensor3D* c_tensor = <c_Tensor3D*>(<Tensor3D>tensor)._get_c_handler()
        cdef c_Tensor3D* _c_tensor

        if self._has_tensor(name):
            # Vector with the same name already exists. Only update its values and base
            warn(f'Tensor "{name.decode()}" already exists. Only updating its base & values', UserWarning)

            _tensor = self._get_tensor(name)
            _c_tensor = <c_Tensor3D*>(<Tensor3D>_tensor)._get_c_handler()
            _c_tensor.set_Base(c_tensor.get_Base())
            _c_tensor.set_matrix(c_tensor.get_matrix())
            return _tensor


        c_tensor.set_name(name)
        self._c_handler.new_Tensor3D(c_tensor)
        (<Tensor3D>tensor)._owns_c_handler = False
        return tensor




    cpdef _new_point(self, name, args, kwargs):
        name = _parse_name(name, check_syntax=True)

        if self._has_object(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        if len(args) < 2 and 'previous' not in kwargs:
            args = list(args)
            args.insert(0, 'O')

        previous, position = _apply_signature(
            ['previous', 'position'],
            {},
            args,
            kwargs
        )

        if not isinstance(previous, Point):
            previous = self._get_point(previous)

        if not isinstance(position, Vector3D):
            position = self._get_vector(position)

        cdef c_Point* c_prev_point = (<Point>previous)._c_handler
        cdef c_Vector3D* c_pos_vector = <c_Vector3D*>(<Vector3D>position)._c_handler
        cdef c_Point* c_point = self._c_handler.new_Point(name, c_prev_point, c_pos_vector)
        return Point(<Py_ssize_t>c_point)




    cpdef _new_frame(self, name, point, base=None):
        name = _parse_name(name, check_syntax=True)

        if self._has_object(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        if not isinstance(point, Point):
            point = self._get_point(point)

        if base is not None:
            if not isinstance(base, Base):
                base = self._get_base(base)
        else:
            base = self._get_base('xyz')

        return Frame(<Py_ssize_t>self._c_handler.new_Frame(name, (<Point>point)._c_handler, (<Base>base)._c_handler))




    cpdef _new_solid(self, name, point, base, mass, CM, IT):
        name = _parse_name(name, check_syntax=True)

        if self._has_object(name):
            raise IndexError(f'Name "{name.decode()}" its already in use')

        if not isinstance(point, (str, Point)):
            raise TypeError('point argument must be an instance of the class Point or str')

        if not isinstance(point, Point):
            point = self._get_point(point)


        if not isinstance(base, (str, Base)):
            raise TypeError('base argument must be an instance of the class Base or str')

        if not isinstance(base, Base):
            base = self._get_base(base)


        if not isinstance(mass, (str, SymbolNumeric)):
            raise TypeError('mass argument must be an instance of the class SymbolNumeric or str')

        if not isinstance(mass, SymbolNumeric):
            mass = self._get_symbol(mass, kind=b'parameter')
        elif mass.get_type() != 'parameter':
            raise TypeError('mass must be a parameter symbol')


        if not isinstance(CM, (str, Vector3D)):
            raise TypeError('CM argument must be an instance of the class Vector3D or str')

        if not isinstance(CM, Vector3D):
            CM = self._get_vector(CM)


        if not isinstance(IT, (str, Tensor3D)):
            raise TypeError('IT argument must be an instance of the class Tensor3D or str')

        if not isinstance(IT, Tensor3D):
            IT = self._get_tensor(IT)

        return Solid(<Py_ssize_t>self._c_handler.new_Solid(
            name,
            (<Point>point)._c_handler,
            (<Base>base)._c_handler,
            (<SymbolNumeric>mass)._c_handler,
            <c_Vector3D*>(<Vector3D>CM)._get_c_handler(),
            <c_Tensor3D*>(<Tensor3D>IT)._get_c_handler()
        ))



    cpdef _new_wrench(self, name, force, moment, point, solid, type):
        name = _parse_name(name)

        if not isinstance(force, (Vector3D, str)):
            raise TypeError('Force must be a Vector3D or str object')

        if not isinstance(force, Vector3D):
            force = self._get_vector(force)


        if not isinstance(moment, (Vector3D, str)):
            raise TypeError('Moment must be a Vector3D or str object')

        if not isinstance(moment, Vector3D):
            moment = self._get_vector(moment)


        if not isinstance(point, (Point, str)):
            raise TypeError('Point must be a Point or str object')

        if not isinstance(point, Point):
            point = self._get_point(point)


        if not isinstance(solid, (Solid, str)):
            raise TypeError('Moment must be a Solid or str object')

        if not isinstance(solid, Solid):
            solid = self._get_solid(solid)

        type = _parse_text(type)


        return _wrench_from_c(self._c_handler.new_Wrench3D(
            name,
            c_deref(<c_Vector3D*>(<Vector3D>force)._get_c_handler()),
            c_deref(<c_Vector3D*>(<Vector3D>moment)._get_c_handler()),
            (<Point>point)._c_handler,
            <c_Solid*>(<Solid>solid)._c_handler,
            type
        ))




    ######## Kinematic operations ########


    cpdef _reduced_base(self, a, b):
        if not isinstance(a, (str, Base)) or not isinstance(b, (str, Base)):
            raise TypeError('Input arguments must be Base or str objects')

        if not isinstance(a, Base):
            a = self._get_base(a)

        if not isinstance(b, Base):
            b = self._get_base(b)

        return Base(<Py_ssize_t>self._c_handler.Reduced_Base(
            (<Base>a)._c_handler,
            (<Base>b)._c_handler)
        )



    cpdef _reduced_point(self, a, b):
        if not isinstance(a, (str, Point)) or not isinstance(b, (str, Point)):
            raise TypeError('Input arguments must be Point or str objects')

        if not isinstance(a, Point):
            a = self._get_point(a)

        if isinstance(b, str):
            b = self._get_point(b)

        return Point(<Py_ssize_t>self._c_handler.Reduced_Point(
            (<Point>a)._c_handler,
            (<Point>b)._c_handler)
        )



    cpdef _pre_point_branch(self, a, b):
        if not isinstance(a, (str, Point)) or not isinstance(b, (str, Point)):
            raise TypeError('Input arguments must be Point or str objects')

        if not isinstance(a, Point):
            a = self._get_point(a)

        if isinstance(b, str):
            b = self._get_point(b)

        return Point(<Py_ssize_t>self._c_handler.Pre_Point_Branch(
            (<Point>a)._c_handler,
            (<Point>b)._c_handler)
        )




    cpdef _rotation_matrix(self, a, b):
        if not isinstance(a, (str, Base)) or not isinstance(b, (str, Base)):
            raise TypeError('Input arguments must be Base or str objects')

        if not isinstance(a, Base):
            a = self._get_base(a)

        if not isinstance(b, Base):
            b = self._get_base(b)

        return _matrix_from_c_value(self._c_handler.Rotation_Matrix(
            (<Base>a)._c_handler,
            (<Base>b)._c_handler
        ))



    cpdef _position_vector(self, a, b):
        if not isinstance(a, (str, Point)) or not isinstance(b, (str, Point)):
            raise TypeError('Input arguments must be Point or str objects')

        if not isinstance(a, Point):
            a = self._get_point(a)

        if isinstance(b, str):
            b = self._get_point(b)

        return _vector_from_c_value(self._c_handler.Position_Vector(
            (<Point>a)._c_handler,
            (<Point>b)._c_handler
        ))



    cpdef _angular_velocity(self, a, b):
        if not isinstance(a, (str, Base)) or not isinstance(b, (str, Base)):
            raise TypeError('Input arguments must be Base or str objects')

        if not isinstance(a, Base):
            a = self._get_base(a)

        if not isinstance(b, Base):
            b = self._get_base(b)

        return _vector_from_c_value(self._c_handler.Angular_Velocity(
            (<Base>a)._c_handler,
            (<Base>b)._c_handler
        ))



    cpdef _angular_velocity_tensor(self, a, b):
        if not isinstance(a, (str, Base)) or not isinstance(b, (str, Base)):
            raise TypeError('Input arguments must be Base or str objects')

        if not isinstance(a, Base):
            a = self._get_base(a)

        if not isinstance(b, Base):
            b = self._get_base(b)

        return _tensor_from_c_value(self._c_handler.Angular_Velocity_Tensor(
            (<Base>a)._c_handler,
            (<Base>b)._c_handler
        ))



    cpdef _velocity_vector(self, frame, point, solid=None):
        if not isinstance(frame, (str, Frame)):
            raise TypeError('frame must be an instance of Frame or str')

        if not isinstance(point, (str, Point)):
            raise TypeError('point must be an instance of Point or str')

        if solid is not None and not isinstance(solid, (str, Solid)):
            raise TypeError('solid must be None or either an instance of Solid or str')

        if not isinstance(frame, Frame):
            frame = self._get_frame(frame)

        if not isinstance(point, Point):
            point = self._get_point(point)

        if solid is not None and not isinstance(solid, Solid):
            solid = self._get_solid(solid)


        cdef c_Frame* c_frame = (<Frame>frame)._c_handler
        cdef c_Point* c_point = (<Point>point)._c_handler
        if solid is None:
            return _vector_from_c_value(self._c_handler.Velocity_Vector(c_frame, c_point))
        return _vector_from_c_value(self._c_handler.Velocity_Vector(c_frame, c_point, <c_Solid*>(<Solid>solid)._c_handler))



    cpdef _angular_acceleration(self, a, b):
        if not isinstance(a, (str, Base)) or not isinstance(b, (str, Base)):
            raise TypeError('Input arguments must be Base or str objects')

        if not isinstance(a, Base):
            a = self._get_base(a)

        if not isinstance(b, Base):
            b = self._get_base(b)

        return _vector_from_c_value(self._c_handler.Angular_Acceleration(
            (<Base>a)._c_handler,
            (<Base>b)._c_handler
        ))



    cpdef _acceleration_vector(self, frame, point, solid=None):
        if not isinstance(frame, (str, Frame)):
            raise TypeError('frame must be an instance of Frame or str')

        if not isinstance(point, (str, Point)):
            raise TypeError('point must be an instance of Point or str')

        if solid is not None and not isinstance(solid, (str, Solid)):
            raise TypeError('solid must be None or either an instance of Solid or str')

        if not isinstance(frame, Frame):
            frame = self._get_frame(frame)

        if not isinstance(point, Point):
            point = self._get_point(point)

        if solid is not None and not isinstance(solid, Solid):
            solid = self._get_solid(solid)


        cdef c_Frame* c_frame = (<Frame>frame)._c_handler
        cdef c_Point* c_point = (<Point>point)._c_handler
        if solid is None:
            return _vector_from_c_value(self._c_handler.Acceleration_Vector(c_frame, c_point))
        return _vector_from_c_value(self._c_handler.Acceleration_Vector(c_frame, c_point, <c_Solid*>(<Solid>solid)._c_handler))




    cpdef _twist(self, solid):
        if not isinstance(solid, (str, Solid)):
            raise TypeError('Input argument must be a Solid or str object')

        if not isinstance(solid, Solid):
            solid = self._get_solid(solid)
        return _wrench_from_c_value(self._c_handler.Twist(<c_Solid*>(<Solid>solid)._c_handler))




    cpdef _derivative(self, args, kwargs):
        cdef c_Vector3D* c_vector

        if not args:
            raise TypeError('Invalid number of inputs (expected at least 1 positional argument)')
        args = list(args)
        x = args.pop(0)

        if not isinstance(x, (Expr, Matrix)):
            raise TypeError('The first argument must be an expression, matrix or vector')

        if isinstance(x, (Expr, Matrix)) and not isinstance(x, Vector3D):
            if args or kwargs:
                raise TypeError('Invalid number of arguments (only 1 expected)')
            if isinstance(x, Expr):
                return _expr_from_c(self._c_handler.dt((<Expr>x)._c_handler))

            return _matrix_from_c_value(self._c_handler.Dt(c_deref(<c_Matrix*>(<Matrix>x)._get_c_handler())))

        else:
            c_vector = <c_Vector3D*>(<Vector3D>x)._get_c_handler()

            if len(args) + len(kwargs) > 1:
                raise TypeError('Invalid number of arguments (only 2 expected)')
            elif not args and not kwargs:
                return _vector_from_c_value(self._c_handler.dt(c_deref(c_vector)))

            if args:
                y = args[0]
                if not isinstance(y, (str, Base, Frame)):
                    raise TypeError('Second argument after the vector must be a Frame, Base or str object')
                if isinstance(y, str):
                    if not self._has_base(y) and not self._has_frame(y):
                        raise IndexError('There is no frame or base called "{y}"')
                    if self._has_base(y):
                        y = self._get_base(y)
                    else:
                        y = self._get_frame(y)
            else:
                key = next(iter(kwargs))
                if key not in ('base', 'frame'):
                    raise TypeError(f'Got an unexpected keyword argument "{key}"')
                y = next(iter(kwargs.values()))
                if key == 'base':
                    if not isinstance(y, (str, Base)):
                        raise TypeError('base must be a Base or str object')
                    if not isinstance(y, Base):
                        y = self._get_base(y)

                else:
                    if not isinstance(y, (str, Frame)):
                        raise TypeError('frame must be a Frame or str object')
                    if not isinstance(y, Frame):
                        y = self._get_frame(y)

            if isinstance(y, Base):
                return _vector_from_c_value(self._c_handler.Dt(c_deref(c_vector), (<Base>y)._c_handler))
            return _vector_from_c_value(self._c_handler.Dt(c_deref(c_vector), (<Frame>y)._c_handler))






    cpdef _jacobian(self, args, kwargs):
        if len(args) < 2:
            raise TypeError('Invalid number of inputs (expected at least 2 positional arguments)')

        args = list(args)
        x, y = args[:2]
        args = args[2:]

        if not isinstance(x, Matrix):
            raise TypeError('The first argument must be a matrix')

        if not isinstance(y, (Matrix, SymbolNumeric)):
            raise TypeError('The second argument after the matrix must be a matrix or a symbol')

        if isinstance(y, SymbolNumeric):
            if len(args) > 0:
                raise TypeError('Invalid number of inputs (expected at most 2 positional arguments)')

            if kwargs:
                raise TypeError('You cant pass keyword arguments after passing a matrix and a symbol as positional arguments')


            # Derivative of the matrix with respect a symbol
            return _matrix_from_c_value(
                self._c_handler.jacobian(
                    c_deref(<c_Matrix*>(<Matrix>x)._get_c_handler()),
                    c_deref(<c_symbol*>(<SymbolNumeric>y)._c_handler)
                )
            )

        # Derivative of the matrix with resspect another matrix
        if len(args) + len(kwargs) > 1:
            raise TypeError('Invalid number of inputs (expected at most 3 positional or keyword arguments)')

        if args or kwargs:
            if kwargs:
                key = next(iter(kwargs))
                if key != 'symmetric':
                    raise TypeError(f'Got an unexpected keyword argument "{key}"')
                symmetric = next(iter(kwargs.values()))
            else:
                symmetric = args[0]

            if not isinstance(symmetric, (Expr, int)):
                raise TypeError('symmetric argument must be an expression, bool or int')

            symmetric = Expr(symmetric)
        else:
            symmetric = Expr(0)

        return _matrix_from_c_value(
            self._c_handler.jacobian(
                c_deref(<c_Matrix*>(<Matrix>x)._get_c_handler()),
                c_deref(<c_Matrix*>(<Matrix>y)._get_c_handler()),
                (<Expr>symmetric)._c_handler
                )
        )





    cpdef _diff(self, x, symbol):

        if not isinstance(symbol, (str, SymbolNumeric)):
            raise TypeError('symbol must be a SymbolNumeric or str object')

        if isinstance(symbol, str):
            symbol = self._get_symbol(symbol)

        if not isinstance(x, (Expr, Matrix, Wrench3D)):
            raise TypeError('First argument must be a expression, matrix or wrench object')


        cdef c_symbol_numeric* c_symbol = (<SymbolNumeric>symbol)._c_handler

        if isinstance(x, Expr):
            # derivative between expression and symbol
            return _expr_from_c(self._c_handler.diff(
                    (<Expr>x)._c_handler,
                    c_deref(c_symbol)
                    ))

        if isinstance(x, Vector3D):
            # derivative between vector and symbol
            return _vector_from_c_value(self._c_handler.diff(
                c_deref(<c_Vector3D*>(<Vector3D>x)._get_c_handler()),
                c_deref(c_symbol)
            ))

        if isinstance(x, Tensor3D):
            # derivative between tensor and symbol
            return _tensor_from_c_value(self._c_handler.diff(
                c_deref(<c_Tensor3D*>(<Tensor3D>x)._get_c_handler()),
                c_deref(c_symbol)
            ))

        if isinstance(x, Matrix):
            # derivative between matrix and symbol
            return _matrix_from_c_value(self._c_handler.diff(
                c_deref((<Matrix>x)._get_c_handler()),
                c_deref(c_symbol)
            ))

        # derivative between wrench and symbol
        return _wrench_from_c_value(self._c_handler.diff(
            c_deref((<Wrench3D>x)._c_handler),
            c_deref(c_symbol)
        ))




    ######## Solid operations ########


    def _gravity_wrench(self, solid):
        if not isinstance(solid, (str, Solid)):
            raise TypeError('Input argument must be a Solid or str object')
        if isinstance(solid, str):
            solid = self._get_solid(solid)

        return _wrench_from_c(self._c_handler.Gravity_Wrench(<c_Solid*>(<Solid>solid)._c_handler))


    def _inertia_wrench(self, solid):
        if not isinstance(solid, (str, Solid)):
            raise TypeError('Input argument must be a Solid or str object')
        if isinstance(solid, str):
            solid = self._get_solid(solid)
        return _wrench_from_c(self._c_handler.Inertia_Wrench(<c_Solid*>(<Solid>solid)._c_handler))






    ######## Mixin ########

    cpdef _set_autogen_latex_names(self, enabled):
        if not isinstance(enabled, bool):
            raise TypeError('Input argument should be a boolean value')
        self._autogen_latex_names = enabled

    cpdef _is_autogen_latex_names_enabled(self):
        return self._autogen_latex_names











######## Class SymbolsMapping ########


class SymbolsMapping(ObjectsMapping, SymbolsTableView):
    def __init__(self, system, kind=None):
        ObjectsMapping.__init__(self,
            partial(system._get_symbol, kind=kind),
            partial(system._get_symbols, kind=kind),
            partial(system._has_symbol, kind=kind)
        )
        SymbolsTableView.__init__(self, system, kind)





######## Class MatricesMapping ########

class MatricesMapping(ObjectsMapping, MatricesTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_matrix,
            system._get_matrices,
            system._has_matrix
        )
        MatricesTableView.__init__(self, system)




######## Class VectorsMapping ########

class VectorsMapping(ObjectsMapping, VectorsTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_vector,
            system._get_vectors,
            system._has_vector
        )
        VectorsTableView.__init__(self, system)




######## Class TensorsMapping ########

class TensorsMapping(ObjectsMapping, TensorsTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_tensor,
            system._get_tensors,
            system._has_tensor
        )
        TensorsTableView.__init__(self, system)




######## Class BasesMapping ########

class BasesMapping(ObjectsMapping, BasesTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_base,
            system._get_bases,
            system._has_base
        )
        BasesTableView.__init__(self, system)




######## Class PointsMapping ########

class PointsMapping(ObjectsMapping, PointsTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_point,
            system._get_points,
            system._has_point
        )
        PointsTableView.__init__(self, system)



######## Class FramesMapping ########

class FramesMapping(ObjectsMapping, FramesTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_frame,
            system._get_frames,
            system._has_frame
        )
        FramesTableView.__init__(self, system)




######## Class SolidsMapping ########

class SolidsMapping(ObjectsMapping, SolidsTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_solid,
            system._get_solids,
            system._has_solid
        )
        SolidsTableView.__init__(self, system)



######## Class WrenchesMapping ########

class WrenchesMapping(ObjectsMapping, WrenchesTableView):
    def __init__(self, system):
        ObjectsMapping.__init__(self,
            system._get_wrench,
            system._get_wrenches,
            system._has_wrench
        )
        WrenchesTableView.__init__(self, system)
