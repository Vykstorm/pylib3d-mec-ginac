'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class NumericFunction
'''

import json
from math import cos, sin, tan


######## Class NumericFunction ########

class NumericFunction:

    ######## Constructor ########

    def __init__(self, name, atoms, outputs, use_numpy=True):
        # Validate input arguments
        if not isinstance(name, str) or not str:
            raise TypeError('name must be a non empty string')
        if not isinstance(atoms, dict):
            raise TypeError('atoms must be a dictionary')
        if not isinstance(outputs, (list, tuple)) or not outputs:
            raise TypeError('outputs must be a non empty list')
        outputs = tuple(outputs)

        if not all(map(lambda key: isinstance(key, str) and key, atoms.keys())):
            raise TypeError('atom names must be non empty strings')
        if not all(map(lambda value: isinstance(value, str) and value, atoms.values())):
            raise TypeError('atom expressions must be non empty strings')

        if not all(map(lambda output: isinstance(output, str) and output, outputs)):
            raise TypeError('outputs must be a list of non empty strings')

        if not isinstance(use_numpy, bool):
            raise TypeError('use_numpy must be bool')

        # Initialize internal fields
        self._name = name
        self._atoms = atoms
        self._outputs = outputs
        self._use_numpy = use_numpy
        self._code = None



    def _compile(self):
        # This private method is used to compile the internal numeric function
        lines = [f'{name} = {value}' for name, value in self.atoms.items()]
        lines.append(f'__output__ = [{", ".join(self.outputs)}]')
        source = '\n'.join(lines)
        self._code = compile(source, '<string>', 'exec', optimize=2)




    ######## Getters ########

    def get_name(self):
        '''get_name() -> str
        Get the name of this numeric function

        :rtype: str

        '''
        return self._name

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

    def is_numpy_used(self):
        '''is_numpy_used() -> bool
        If this method returns True, the output of this numeric function will be
        a numpy array. Otherwise, it will be a generic python list

        '''
        return self._use_numpy

    def use_numpy(self):
        '''use_numpy()
        If this method is called, the output of this numeric function will be
        a numpy array.
        '''
        self._use_numpy = True

    def dont_use_numpy(self):
        '''dont_use_numpy()
        If this method is called, the output of this numeric function will be
        a generic python list
        '''
        self._use_numpy = False


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
            'name': self.name,
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
        global_vars = {'cos': cos, 'sin': sin, 'tan': tan}
        global_vars.update(inputs)
        local_vars = {}

        exec(self._code, global_vars, local_vars)
        result = local_vars['__output__']

        if self._use_numpy:
            import numpy as np
            return np.array(result)
        return result



    ######## Properties ########

    @property
    def name(self):
        '''
        Only read property that returns the name of this numeric function

        :rtype: str

        '''
        return self.get_name()

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


    ######## Printing ########

    def __str__(self):
        return f"Numeric function {self.get_name()}"

    def __repr__(self):
        return self.__str__()
