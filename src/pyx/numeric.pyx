'''
Author: Víctor Ruiz Gómez
Description:
This module defines the class NumericFunction
'''

import json
import ast


######## Class NumericFunction ########

class NumericFunction:

    ######## Constructor ########

    def __init__(self, name, atoms, outputs, use_numpy=True):
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

        self._name = name
        self._atoms = atoms
        self._outputs = outputs
        self._use_numpy = use_numpy
        self._func = None



    def _compile(self):
        pass



    ######## Getters ########

    def get_name(self):
        return self._name

    def get_atoms(self):
        return self._atoms

    def get_outputs(self):
        return self._outputs

    def is_numpy_used(self):
        return self._use_numpy

    def use_numpy(self):
        self._use_numpy = True

    def dont_use_numpy(self):
        self._use_numpy = False


    ######## Export/Import  ########

    @classmethod
    def load_from_file(cls, filename):
        if not isinstance(filename, str):
            raise TypeError('filename must be a string')
        with open(filename, 'r') as file:
            data = json.load(filename)
        try:
            return cls(**data)
        except TypeError:
            raise RuntimeError(f'Failed to load numeric function from "{filename}"')


    def save_to_file(self, filename):
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
        if args:
            assert len(args) == 1
            inputs = args[0]
            assert isinstance(inputs, dict)
            assert all(map(lambda key: isinstance(key, str) and key, inputs.keys()))
        else:
            inputs = {}

        inputs.update(kwargs)
        assert all(map(lambda value: isinstance(value, float), inputs.values()))

        # Compile numeric function if needed
        if self._func is None:
            self._compile()

        output = self._func(inputs)
        return output



    ######## Properties ########

    @property
    def name(self):
        return self.get_name()

    @property
    def atoms(self):
        return self.get_atoms()

    @property
    def outputs(self):
        return self.get_outputs()


    ######## Printing ########

    def __str__(self):
        return f"Numeric function {self.get_name()}"

    def __repr__(self):
        return self.__str__()
