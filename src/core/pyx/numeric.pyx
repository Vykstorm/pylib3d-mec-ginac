'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class NumericFunction
'''

from collections import deque



######## Class NumericFunction ########

class NumericFunction:
    '''
    Instances of this class represents numerical functions and
    are returned by the method ``get_numeric_function``

    .. seealso:: :func:`get_numeric_function`

    '''

    ######## Constructor ########

    def __init__(self, atoms, outputs, globals=None, output_arrays=None):
        '''
        Initialize the numeric function. This class is not intended to be instantiated
        by the user directly.

        :param atoms: Must be a dictionary where keys are atom names (valid python identifiers
            also), and values will be the expressions assigned to each atom
            (they must be non empty strings)


        :param outputs: Must be a matrix with strings representing the expressions to be evaluated
            as the outputs of the numeric function.

        :param globals: Additional global functions needed to evaluate the atoms or the outputs
            of the numeric function (by default only sin, cos, tan can be used)

        :param output_arrays: An optional iterable (or the number) of independent preallocated numpy arrays where this numeric
            function will store the evaluation results (for optimization purposes).
            The first evaluation will store the result in the first array. The second in the next one
            and so on until the list is exhausted. Then the first array will be selected again.



            :Example:

            >>> func = NumericFunction(
            >>>     atoms={'atom1': 'x ** 2', 'atom2': 'y ** 2', 'atom3': 'z ** 2'},
            >>>     outputs=[
            >>>         ['atom1 * x + y * z', 'atom2 * (y - z)'],
            >>>         ['atom3 * z - 1', 'atom1 + atom3 * y + 1']
            >>>     ]
            >>> )
            >>> func({'x'=1.0, 'y'=2.0, 'z'=3.0})
            array([[ 7., -4.],
                   [26., 20.]])


        '''
        ## Validate input arguments
        if globals is None:
            globals = {'sin': math.sin, 'cos': math.cos, 'tan': math.tan}

        # Initialize internal fields
        self._atoms = atoms
        self._outputs = outputs
        self._code = None
        self._globals = globals

        if output_arrays is None:
            output_arrays = 1

        if isinstance(output_arrays, int):
            self._output_arrays = deque([np.zeros(self.get_outputs_shape(), dtype=np.float64) for i in range(0, output_arrays)])
        else:
            self._output_arrays = deque(output_arrays)

        # Compile numeric function body if needed
        if self._code is None:
            self._compile()




    def _compile(self):
        # This private method is used to compile the internal numeric function
        lines = [f'{name} = {value}' for name, value in self.atoms.items()]

        n, m = self.outputs_shape
        outputs = chain.from_iterable(self._outputs)
        lines.append(f'__output__.flat = [ {", ".join( outputs )} ]')
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
        '''get_outputs() -> List[List[str]]
        Get the list of output expressions for this numeric function

        :rtype: List[str]

        '''
        return self._outputs


    def get_outputs_shape(self):
        '''get_outputs_shape() -> int, int
        Get the number of rows and columns of the numpy output arrays when evaluating
        this function.

        :rtype: int, int

        '''
        return len(self._outputs), len(self._outputs[0])



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
        This is an alias of ``evaluate``

        .. seealso:: :func:`evaluate`

        '''
        return self.evaluate(*args, **kwargs)



    def evaluate(self, inputs={}):
        '''
        Evaluate this numeric function

        :param inputs: Must be a dictionary with additional inputs for the numeric function.
            The keys must be valid python variable names and values must be all floats.

        :return: This function evaluated numerically. Returns a numpy array.
        :rtype: np.ndarray

        '''
        output_array = self._output_arrays.popleft()
        self._output_arrays.append(output_array)

        locals = inputs
        locals['__output__'] = output_array

        exec(self._code, self._globals, locals)
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
    def outputs_shape(self):
        '''
        Only read property that returns the shape of the numpy output arrays
        when evaluating this numeric function

        :rtype: int, int

        '''
        return self.get_outputs_shape()


    @property
    def globals(self):
        '''
        Only read property that returns the global variables ir functions used by
        this numeric function
        '''
        return self.get_globals()





    ######## Printing ########
