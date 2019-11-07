'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class NumericFunction
'''


######## Class NumericFunction ########

class NumericFunction:
    '''
    Instances of this class represents numerical functions and
    are returned by the method ``get_numeric_function``

    .. seealso:: :func:`get_numeric_function`

    '''

    ######## Constructor ########

    def __init__(self, atoms, outputs, globals=None):
        ## Validate input arguments

        # Validate atoms argument
        assert isinstance(atoms, dict)
        assert all(map(lambda key: isinstance(key, str) and key.isidentifier(), atoms.keys()))
        assert all(map(lambda value: isinstance(value, str) and value, atoms.values()))

        # Validate outputs argument
        assert isinstance(outputs, (list, tuple))
        output = tuple(outputs)
        assert output
        assert all(map(lambda output: isinstance(output, (list, tuple)), outputs))
        outputs = tuple(map(tuple, outputs))
        assert len(frozenset(map(len, outputs))) == 1
        assert outputs[0]
        for output in outputs:
            assert all(map(lambda item: isinstance(item, str), output)) and all(output)

        # Validate globals argument
        assert globals is None or isinstance(globals, dict)
        if globals is not None:
            assert all(map(lambda key: isinstance(key, str) and key.isidentifier(), globals.keys()))
        else:
            globals = {'sin': sin, 'cos': cos, 'tan': tan}


        # Initialize internal fields
        self._atoms = atoms
        self._outputs = outputs
        self._code = None
        self._globals = globals




    def _compile(self):
        # This private method is used to compile the internal numeric function
        lines = [f'{name} = {value}' for name, value in self.atoms.items()]

        if isinstance(self.outputs[0], tuple):
            lines.append(f'__output__ = [' + ', '.join(['[' + ', '.join(row) + ']' for row in self.outputs]) + ']')
        else:
            lines.append(f'__output__ = [{", ".join(self.outputs)}]')
        source = '\n'.join(lines)
        self._code = compile(source, '<string>', 'exec', optimize=2)




    ######## Getters ########

    def get_atoms(self):
        '''get_atoms() -> Dict[str, str]
        Get the atoms associated to this numeric function.

        :return: A dictionary where keys are atom names and the values are their
            expressions
        :rtype: Dict[str, str]

        '''
        return self._atoms

    def get_outputs(self):
        '''get_outputs() -> List[str]
        Get the list of output expressions for this numeric function

        :rtype: List[str]

        '''
        return self._outputs



    def get_globals(self):
        '''get_globals() -> Dict[str, Any]
        Get the global variables and functions used by this numeric function
        '''
        return self._globals





    ######## Export/Import  ########

    @classmethod
    def load_from_file(cls, filename):
        '''load_from_file(filename: str) -> NumericFunction
        Create a numeric function with the information provided by the file in the given
        path (previously created by the function ``save_to_file``)

        .. seealso::
            :func:`save_to_file`

        '''
        if not isinstance(filename, str):
            raise TypeError('filename must be a string')
        with open(filename, 'r') as file:
            data = json.load(file)
        try:
            return cls(**data)
        except TypeError:
            raise RuntimeError(f'Failed to load numeric function from "{filename}"')


    def save_to_file(self, filename):
        '''save_to_file(filename: str)
        Save this numeric function to a file.

        '''
        if not isinstance(filename, str):
            raise TypeError('filename must be a string')
        data = {
            'atoms': self.atoms,
            'outputs': self.outputs
        }
        with open(filename, 'w') as file:
            json.dump(data, file)



    ######## Function evaluation ########

    def __call__(self, *args, **kwargs):
        '''
        Evaluate this numeric function with the provided positional & keyword arguments
        '''
        if args:
            assert len(args) == 1
            inputs = args[0]
            assert isinstance(inputs, dict)
            assert all(map(lambda key: isinstance(key, str) and key, inputs.keys()))
        else:
            inputs = {}

        inputs.update(kwargs)
        assert all(map(lambda value: isinstance(value, float), inputs.values()))

        # Compile numeric function body if needed
        if self._code is None:
            self._compile()

        # Evaluate the function
        globals = {}
        globals.update(self._globals)
        globals.update(inputs)
        locals = {}

        exec(self._code, globals, locals)
        result = np.array(locals['__output__'], dtype=np.float64)
        return result



    ######## Properties ########


    @property
    def atoms(self):
        '''
        Only read property that returns the atoms of this numeric function

        :rtype: Dict[str, str]

        '''
        return self.get_atoms()

    @property
    def outputs(self):
        '''
        Only read property that returns the outputs of this numeric function
        '''
        return self.get_outputs()

    @property
    def globals(self):
        '''
        Only read property that returns the global variables ir functions used by
        this numeric function
        '''
        return self.get_globals()





    ######## Printing ########
