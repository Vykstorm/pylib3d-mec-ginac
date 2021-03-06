'''
Author: Víctor Ruiz Gómez
Description: This file loads the runtime settings configuration generated in the
instalation process
'''


######## Import statements ########

from types import SimpleNamespace
from os.path import dirname, join
import json
import os
from itertools import starmap
from math import floor


## Load runtime settings
try:
    # From file autogenerated by the installation process
    with open(join(dirname(__file__), 'config.json')) as file:
        runtime_config = json.load(file)
        if not isinstance(runtime_config, dict):
            raise RuntimeError

    # From environment variables
    def get_env_value(key, default):
        if key in os.environ:
            try:
                value = os.environ[key].lower()
                if value in ('true', 'on', 'enabled'):
                    return True
                if value in ('false', 'off', 'disabled'):
                    return False
                try:
                    value = float(value)
                    if floor(value) == value:
                        return floor(value)
                    return value
                except:
                    pass
                return value
            except:
                raise RuntimeError(f'Invalid value for "{key}" setting')
        return default

    runtime_config = dict(zip(runtime_config.keys(), starmap(get_env_value, runtime_config.items())))

    runtime_config = SimpleNamespace(**runtime_config)


except RuntimeError as e:
    if e.args:
        raise e
    raise RuntimeError('Invalid runtime configuration')
