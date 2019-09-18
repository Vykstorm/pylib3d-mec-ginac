'''
Author: Víctor Ruiz Gómez
This is a helper module for the setup.py script. It defines a method parse_source
which takes the contents of each .pyx definition file an expands the jinja2 code macros and
directives.
This can also be run as a script file. Execute "python source.py --help" to get more information.
'''

from jinja2 import Template, Environment
from operator import attrgetter


def parse_source(source, **kwargs):
    '''
    Parses the given source code (which is usually the contents of a .pyx definition file)
    by expanding jinja2 code macros and directives.
    This is useful to auto-generate getter/setter methods in Cython extensions.

    The next custom jinja2 filters are provided:
    - pytitle(x: str) -> str
        Takes the given input string and capitalize the first letter on each word (separated
        by underscores or spaces). Then, both underscores and space chars are removed.
        This is useful to translate an arbitrary name into a Python name class

        pytitle('joint unknown') -> 'JointUnknown'
        pytitle('joint_unknown') -> 'JointUnknown'
        pytitle('foo_bar_qux') -> 'FooBarQux'


    - ctitle(x: str) -> str
        Is the same as pytitle but doesnt remove underscores (Useful to translate names to C attributes)

        ctitle('joint unknown') -> 'Joint_Unknown'
        ctitle('joint_unknown') -> 'Joint_Unknown'
        ctitle('foo_bar_qux') -> 'Foo_Bar_Qux'


    - getter(x: str) -> str
        Adds the prefix get_ to the string

        getter('coordinates') -> 'get_coordinates'


    - setter(x: str) -> str
        Adds the prefix set_ to the string

        setter('parameters') -> 'get_parameters'


    - plural(x: str) -> str
        Adds the suffix to make the word plural

        plural('acceleration') -> 'accelerations'
        plural('velocity') -> 'velocities'


    The output of a filter can be used as an input for a second filter in the templates.
    e.g:
    class Foo:
        {% for attr in ('house', 'tree') %}
        def {{attr | plural | getter}}(self):
            pass
        {% endfor %}

    it will generate the next code:
    class Foo:
        def get_houses(self):
            pass

        def get_trees(self):
            pass


    The next variables are also avaliable in the templates:

    - symbol_types:
        A list with all kind of numeric symbols in the lib3d_mec_ginac library.
        ['coordinate', 'velocity', 'acceleration', 'aux_coordinate', 'aux_velocity',
         'aux_acceleration', 'parameter', 'joint_unknown', 'input']

    - geometric_types:
        A list with all kind of geometry objects defined in the lib3d_mec_ginac library.
        ['base', 'frame', 'solid', 'tensor3D', 'matrix', 'vector3D', 'point', 'wrench3D', 'drawing3D']
    '''


    ## Custom filters
    def pytitle(x):
        return x.title().replace('_', '').replace(' ', '')

    def ctitle(x):
        return x.title().replace(' ', '_')

    def getter(x):
        return 'get_' + x

    def setter(x):
        return 'set_' + x

    def plural(x):
        if x.lower() == 'velocity':
            return x[:-1] + 'ies'
        return x + 's'


    ## Custom tests


    ## Global variables
    vars = {
        'symbol_types': [
            'coordinate', 'velocity', 'acceleration', 'aux_coordinate', 'aux_velocity',
            'aux_acceleration', 'parameter', 'joint_unknown', 'input'
        ],

        'geometric_types': [
            'base', 'frame', 'solid', 'tensor3D', 'matrix', 'vector3D',
            'point', 'wrench3D', 'drawing3D'
        ]
    }


    # Create environment & add custom filters and tests
    env = Environment()
    filters = [pytitle, ctitle, plural, getter, setter]
    env.filters.update(dict(zip(map(attrgetter('__name__'), filters), filters)))

    # Parse source code
    context = {}
    context.update(kwargs)
    context.update(vars)
    return env.from_string(source).render(**context)





if __name__ == '__main__':
    ## Run this file as script

    from argparse import ArgumentParser, FileType, RawDescriptionHelpFormatter
    from sys import stdout

    parser = ArgumentParser(
        description=parse_source.__doc__,
        formatter_class=RawDescriptionHelpFormatter
    )
    parser.add_argument('file', type=FileType('r'), help='Source file to read the code from')
    parser.add_argument('--output', '-o', type=FileType('w'), help='Write the parsed code in this file. By default is printed on stdout', default=stdout)
    args = parser.parse_args()
    f_in, f_out = args.file, args.output

    f_out.write(parse_source(f_in.read()))

    f_in.close()
    f_out.close()
