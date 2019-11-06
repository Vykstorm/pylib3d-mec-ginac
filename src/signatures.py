
from inspect import isclass
from functools import wraps


class parse:
    '''
    This class can be used as a decorator to validate and parse the keyword arguments passed to a
    function in a simple manner.

    The next example checks that the keyword argument "a" is an integer and "b" is either
    a list or tuple

        :Example:

        >>> @parse(a=int, b=(list, tuple))
        >>> def foo(a, b):
        >>>     pass
        >>> foo(1, [])
        >>> foo(None, [])
        TypeError: Invalid type for "a" argument: Expected int instance but got NoneType
        >>> foo(1, True)
        TypeError: Invalid type for "b" argument: Expected list or tuple instance but got bool


    You can also pass a callback function to validate an specific argument

        :Example:

        >>> def foo(value):
        >>>    if not isinstance(value, str):
        >>>        raise TypeError('string expected')
        >>>    return value.lower()

        >>> @parse(a=foo)
        >>> def bar(a):
        >>>     return a

        >>> foo(a='Hello World!')
        'hello world!'
        >>> foo(a=1)
        TypeError: Invalid type for "a" argument: string expected


    In the example above, foo function verifies that the argument "a" is a string
    and parses its value (returns it lower cased).





    '''
    def __init__(self, **kwargs):
        def create_validator(param, spec):
            if isclass(spec):
                cls = spec
                # Type spec is a class (check that the input argument is an instance of the given class)
                def validator(x):
                    if not isinstance(x, cls):
                        raise TypeError(f'Expected {cls.__name__} instance but got {type(x).__name__}')
                    return x
            elif isinstance(spec, (tuple, list)):
                # Type spec is a list of classes (check that the input argument is an instance of one of the given classes)
                if len(spec) == 0 or not all(map(isclass, spec)):
                    raise TypeError
                classes = tuple(spec)

                def validator(x):
                    if not isinstance(x, classes):
                        raise TypeError(f'Expected {" or ".join([cls.__name__ for cls in classes])} instance but got {type(x).__name__}')
                    return x

            elif callable(spec):
                # Type spec is a function.
                validator = spec
            else:
                raise TypeError

            return validator

        self._validators = {}
        for param, spec in kwargs.items():
            try:
                self._validators[param] = create_validator(param, spec)
            except TypeError:
                raise TypeError(f'Invalid type specification for parameter "{param}"')



    def __call__(self, func):
        @wraps(func)
        def validated_func(*args, **kwargs):
            for name, value in kwargs.items():
                if name not in self._validators:
                    continue
                validator = self._validators[name]
                try:
                    kwargs[name] = validator(value)
                except TypeError as e:
                    raise TypeError(f'Invalid type for "{name}" argument: {e.args[0]}')
                except ValueError as e:
                    raise ValueError(f'Invalid value for "{name}" argument: {e.args[0]}')


            return func(*args, **kwargs)

        return validated_func


def foo(value):
    if not isinstance(value, str):
        raise TypeError('string expected')
    return value.lower()


@parse(a=foo)
def foo(a):
    return a
