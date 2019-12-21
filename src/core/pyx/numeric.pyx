'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class NumericFunction
'''



######## class CythonNumericFunctionExtensionsCompiler  ########

class CythonNumericFunctionExtensionsCompiler:
    '''
    Helper class to compile numeric functions as cython extensions
    '''
    _singleton = None
    _numfuncs_dir = '_numfuncs'
    _stdout_logfile = '.stdout.log.txt'
    _stderr_logfile = '.stderr.log.txt'


    def __init__(self):
        self._numfuncs_count = 0
        self._initialized = False


    def compile(self, source, funcname):
        if not self._initialized:
            self._initialized = True
            numfuncs_dir = self._numfuncs_dir
            try:
                if os.path.exists(numfuncs_dir) and not os.path.isdir(numfuncs_dir):
                    raise RuntimeError
                if not os.path.exists(numfuncs_dir):
                    os.mkdir(numfuncs_dir)
                with open(os.path.join(numfuncs_dir, '__init__.py'), 'w') as file:
                    pass

                for filename in filter(methodcaller('startswith', '_numfunc_'), os.listdir(numfuncs_dir)):
                    os.remove(os.path.join(numfuncs_dir, filename))

            except FileExistsError:
                raise RuntimeError


        # Save the source code in a external file
        self._numfuncs_count += 1
        module_name = f'_numfunc_{self._numfuncs_count}'

        filename = f'{module_name}.pyx'
        filepath_name = os.path.join(self._numfuncs_dir, filename)

        with open(filepath_name, 'w') as file:
            file.write(source)

        # Call a subprocess to generate the cython extension
        environ = os.environ.copy()
        environ['CFLAGS'] = f'-I {np.get_include()}'

        stdout, stderr = open(os.path.join(self._numfuncs_dir, self._stdout_logfile), 'a'), open(os.path.join(self._numfuncs_dir, self._stderr_logfile), 'a')
        try:
            subprocess.run(['cythonize', '-i', '-q', '-f', '-3', filepath_name], env=environ, stdout=stdout, stderr=stderr)
        finally:
            stdout.close()
            stderr.close()

        # Import the function from the extension
        return getattr(importlib.__import__('.'.join([self._numfuncs_dir, module_name]), globals(), locals(), [funcname]), funcname)


_numfuncs_extension_compiler = CythonNumericFunctionExtensionsCompiler()





######## Class NumericFunction ########

class NumericFunction:
    '''
    Instances of this class represents numerical functions and
    are returned by the method ``get_numeric_function``

    .. seealso:: :func:`get_numeric_function`

    '''

    ######## Constructor ########

    def __init__(self, atoms, outputs, system, output_arrays=None, c_optimized=False):
        '''
        Initialize the numeric function. This class is not intended to be instantiated
        by the user directly.

        :param atoms: Must be a dictionary where keys are atom names (valid python identifiers
            also), and values will be the expressions assigned to each atom
            (they must be non empty strings)

        :param system: The system where to take the symbol values at.

        :param outputs: Must be a matrix with strings representing the expressions to be evaluated
            as the outputs of the numeric function.

        :param output_arrays: An optional iterable (or the number) of independent preallocated numpy arrays where this numeric
            function will store the evaluation results (for optimization purposes).
            The first evaluation will store the result in the first array. The second in the next one
            and so on until the list is exhausted. Then the first array will be selected again.

        :param c_optimized: If True, compile this numeric function as a Cython extension.
            Otherwise, it is compiled as a python function.
        '''
        # Validate & parse input arguments


        # Parse atoms & output expressions
        def parse_op(match):
            op = match.group()
            try:
                if not op.isidentifier():
                    raise Exception

                if system.has_symbol(op):
                    # Replace symbol names with vector items e.g: a -> params[1]
                    symbol = system.get_symbol(op)
                    if symbol == system.get_time():
                        raise Exception

                    symbol_name, symbol_type = symbol.get_name(), symbol.get_type()
                    index = system._symbols_values[symbol_type].index(symbol_name)
                    return f'{symbol_type}[{index}, 0]'

                # Replace constant names with their numeric values
                if op in ('Euler', 'Pi', 'Tau'):
                    return op.lower()

                raise Exception

            except:
                return op

        parse_expr = partial(sub, '\w+', parse_op)

        # Parse atoms
        atoms = dict(zip(atoms.keys(), map(parse_expr, atoms.values())))

        # Parse outputs
        outputs = np.matrix(outputs)
        outputs = np.matrix(tuple(map(parse_expr, map(methodcaller('item'), outputs.flat)))).reshape(outputs.shape)


        # Initialize internal fields
        self._atoms = atoms
        self._outputs = outputs
        self._system = system
        self._c_optimized = c_optimized


        # Preallocate output arrays
        if output_arrays is None:
            output_arrays = 1

        if isinstance(output_arrays, int):
            self._output_arrays = deque([np.zeros(self._outputs.shape, dtype=np.float64) for i in range(0, output_arrays)])
        else:
            self._output_arrays = deque(output_arrays)

        # Compile numeric function body
        if self._c_optimized:
            self._compile_cython()
        else:
            self._compile_python()




    def _compile_python(self):
        # This private method is used to compile the internal numeric function (unoptimized version)
        symbol_types = tuple(map(methodcaller('decode'), _symbol_types))
        symbols = self._system.get_symbols()

        # Global variables to be used when evaluating the numeric function
        globals = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'euler': math.e, 'tau': math.tau, 'pi': math.pi}
        for symbol_type in symbol_types:
            globals[symbol_type] = self._system.get_symbols_values(kind=symbol_type)
        self._globals = globals

        # Generate the source code to eval the numeric function
        lines = [f'{name} = {value}' for name, value in self.atoms.items()]
        lines.append(f'__output__.flat = [ {", ".join( map(str, self._outputs.flat) )} ]')
        source = '\n'.join(lines)

        # Compile the code
        self._code = compile(source, '<string>', 'exec', optimize=2)




    def _compile_cython(self):
        # This private method is used to compile the internal numeric function (optimized version)

        symbol_types = tuple(map(methodcaller('decode'), _symbol_types))

        ## Generate cython source code
        args = tuple(map(partial(add, 'np.ndarray[np.float64_t, ndim=2] '), chain(symbol_types, ['__output__'])))

        # Imports & function signature
        header = [
            'cimport cython',
            'from math import sin, cos, tan, pi, tau, e as euler',
            'import numpy as np',
            'cimport numpy as np',
            '@cython.boundscheck(False)',
            '@cython.wraparound(False)',
            f'cpdef evaluate({", ".join(args)}):'
        ]

        # Body of the numeric function
        body = [f'cdef np.float64_t {name} = {value}' for name, value in self.atoms.items()]

        n, m = self._outputs.shape
        for i, j in product(range(0, n), range(0, m)):
            body.append(f'__output__[{i}, {j}] = {str(self._outputs[i, j])}')

        # Put all source code together
        lines = []
        lines.extend(header)
        lines.extend(map(partial(add, '\t'), body))
        source = '\n'.join(lines)

        # Compile cython extension
        func = _numfuncs_extension_compiler.compile( source, 'evaluate' )
        self._num_func_optimized = partial(func, *map(self._system.get_symbols_values, symbol_types))





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
        '''get_outputs() -> List[List[str]]
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

    def __call__(self):
        '''
        This is an alias of ``evaluate``

        .. seealso:: :func:`evaluate`

        '''
        return self.evaluate()



    def evaluate(self):
        '''
        Evaluate this numeric function

        :param inputs: Must be a dictionary with additional inputs for the numeric function.
            The keys must be valid python variable names and values must be all floats.

        :return: This function evaluated numerically. Returns a numpy array.
        :rtype: np.ndarray

        '''
        output_array = self._output_arrays.popleft()
        self._output_arrays.append(output_array)

        if self._c_optimized:
            # Evaluate numeric function optimized
            self._num_func_optimized(output_array)
        else:
            # Evaluate numeric function unoptimized
            self._globals['__output__'] = output_array
            exec(self._code, None, self._globals)

        return output_array.view()






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
