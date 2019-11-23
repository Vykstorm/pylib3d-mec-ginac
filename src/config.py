'''
Author: Víctor Ruiz Gómez
Description: This file loads the runtime settings configuration generated in the
instalation process
'''


######## Import statements ########

from types import SimpleNamespace
from os.path import dirname, join
import json



## Load runtime settings
try:
    with open(join(dirname(__file__), 'config.json')) as file:
        data = json.load(file)
        if not isinstance(data, dict):
            raise RuntimeError
        runtime_config = SimpleNamespace(**data)

except RuntimeError:
    raise RuntimeError('Failed to read runtime configuration')
