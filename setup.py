'''
Author: Víctor Ruiz Gómez
Description:
Setup script to install pylib3d-mec-ginac library.
'''

# Import statements
from setuptools.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension
from os import listdir
from os.path import join, abspath, dirname
from functools import reduce, partial
from re import sub, DOTALL
from itertools import chain
import json
from contextlib import contextmanager
import sys
from io import StringIO
import builtins




######## PACKAGE DESCRIPTION ########

# Name of this library
NAME = 'pylib3d-mec-ginac'

# Version of the library
VERSION = '1.0.0'

# Author details
AUTHOR = 'Victor Ruiz Gomez'
AUTHOR_EMAIL = 'victorruizgomezdev@gmail.com'


root_dir = dirname(__file__)

# Library description
DESCRIPTION = 'Python extension for the library lib3d_mec_ginac'

with open(join(root_dir, 'README.md'), 'r') as f:
    LONG_DESCRIPTION = f.read()

# License
with open(join(root_dir, 'LICENSE.txt'), 'r') as f:
    LICENSE = f.read()

# Classifiers
CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Framework :: Buildout :: Extension',
    'Programming Language :: Cython',
    'Programming Language :: C++'
]

# Keywords
KEYWORDS = [
    'cython', 'c++', 'bindings',
    'extension', 'wrapper'
]


######## PYTHON PACKAGE SETUP ########


# Name of the root package of this library
ROOT_PACKAGE = 'lib3d_mec_ginac'

# Directory of the root package of this library
ROOT_PACKAGE_DIR = join(root_dir, 'src')

# List of all packages (including subpackages but not the extension) to be installed within this library
PACKAGES = list(chain([ROOT_PACKAGE], map(ROOT_PACKAGE.__add__, ('.core', '.drawing', '.utils'))))





######## C COMPILER CONFIGURATION ########

# Directory that contains all lib3d-mec-ginac headers
LIB3D_MEC_GINAC_INCLUDE_DIR = abspath('../lib_3d_mec_ginac/include/lib_3d_mec_ginac')

# Directory where lib3d-mec-ginac libraries are located
LIB3D_MEC_GINAC_LIBRARY_DIR = abspath('../lib_3d_mec_ginac/lib')

# Directories containing header files used to build the extensions
INCLUDE_DIRS = [
    '/usr/local/include',
    '/usr/include',
    LIB3D_MEC_GINAC_INCLUDE_DIR
]

# Directories to search for libraries at link time
LIBRARY_DIRS = [
    LIB3D_MEC_GINAC_LIBRARY_DIR,
    '/usr/local/lib'
]

# Directories to search for dynamic libraries at runtime
RUNTIME_LIBRARY_DIRS = [
    LIB3D_MEC_GINAC_LIBRARY_DIR
]

# Name of the libraries for the extensions to link against
LIBRARIES = [
    'cln',
    'ginac',
    '_3d_mec_ginac-2.0'
]


######## EXTENSION SETUP ########

# Name of the Cython extension
EXTENSION_NAME = 'lib3d_mec_ginac_ext'

# Path to the directory containing additional C++ files to be compiled in the extension
CPP_DIR = join(ROOT_PACKAGE_DIR, 'core', 'cpp')

# Path to the directory containing all the .pyx file definitions of the extension
PYX_DIR = join(ROOT_PACKAGE_DIR, 'core', 'pyx')

# Path to the directory containing all the .pxd files of the extension
PXD_DIR = join(ROOT_PACKAGE_DIR, 'core', 'pxd')

# All .pyx file definitions of the extension
PYX_FILES = list(map(partial(join, PYX_DIR), chain(
    # Modules at .../pyx/
    ['imports.pyx', 'globals.pyx', 'parse.pyx', 'views.pyx', 'print.pyx', 'latex.pyx', 'numeric.pyx'],

    # Modules at .../pyx/classes/
    map(partial(join, 'classes'), [
        'object.pyx', 'system.pyx', 'symbol.pyx', 'expression.pyx',
        'base.pyx', 'matrix.pyx', 'vector3D.pyx', 'tensor3D.pyx',
        'point.pyx', 'frame.pyx', 'solid.pyx', 'wrench3D.pyx'
    ])
)))

# This variable points to the file which will be autogenerated, containing all the source code
# of all the .pyx files of the extension
PYX_MAIN = join(PYX_DIR, 'main.pyx')

# This variable will have all the path to the source files used to compile the extension
EXTENSION_SOURCES = list(chain([PYX_MAIN], map(partial(join, CPP_DIR), listdir(CPP_DIR))))


# This list holds all the extensions defined by this library
EXTENSIONS = [
    Extension(
        name=EXTENSION_NAME,
        sources=EXTENSION_SOURCES,
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        runtime_library_dirs=RUNTIME_LIBRARY_DIRS,
        libraries=LIBRARIES,
        language='c++',
        extra_compile_args=['-w']
    )
]




######## RUNTIME CONFIGURATION ########


RUNTIME_CONFIG = {
    # openscad command line utility executable (this is used to convert scad
    # to stl files).
    'OPENSCADCMD': 'openscad',

    # Enable/Disable atomization by default
    'ATOMIZATION': 'off',

    # Gravity direction by default
    'GRAVITY_DIRECTION': 'up',

    # Open 3D scene viewer when importing the package
    'SHOW_DRAWINGS': False,

    # Default simulation update frequency
    'SIMULATION_UPDATE_FREQUENCY': 30,

    # Default simulation time multiplier
    'SIMULATION_TIME_MULTIPLIER': 1
}


# Configuration file where runtime settings will be stored (relative to the root package)
RUNTIME_CONFIG_FILE = 'config.json'










######## INSTALLATION PROCEDURE ########

if __name__ == '__main__':

    ## Helper functions

    # Context manager to supress messages on stdout and stderr
    @contextmanager
    def output_suppressed():
        prev_stdout, sys.stdout = sys.stdout, StringIO()
        prev_stderr, sys.stderr = sys.stderr, StringIO()
        yield
        sys.stdout, sys.stderr = prev_stdout, prev_stderr

    # Class to avoid "command line option ‘-Wstrict-prototypes’ is valid" warning
    class BuildExt(build_ext):
        def build_extensions(self):
            if '-Wstrict-prototypes' in self.compiler.compiler_so:
                self.compiler.compiler_so.remove('-Wstrict-prototypes')
            super().build_extensions()

    # Function to flush the content of stdout after something is printed
    def print(*args, **kwargs):
        builtins.print(*args, flush=True, **kwargs)




    ## Check library dependencies
    print("\u2022 Checking library dependencies", end='')

    try:
        from Cython.Build import cythonize
        import asciitree
        import tabulate
        import numpy
        import vtk
    except ImportError as e:
        # Generate error message if missing dependencies
        print(f'Failed to import "{e.name}" module')
        print('Make sure to install dependencies with "pip install -r requirements.txt"')
        exit(-1)

    from vtk import vtkVersion
    if vtkVersion.GetVTKMajorVersion() < 8 or vtkVersion.GetVTKMinorVersion() < 1 or vtkVersion.GetVTKBuildVersion() < 2:
        print('version of the vtk library must be >= 8.1.2')
        exit(-1)

    '''
    try:
        import vtk.tk.vtkTkRenderWindowInteractor
    except ImportError as e:
        print(f'Failed to import VTK Tkinter extension')
        exit(-1)

    '''
    print(" [done]")


    ## Create config.json (this is used to configure the library at runtime)
    print(f"\u2022 Generating runtime settings file", end='')
    with open(join(ROOT_PACKAGE_DIR, RUNTIME_CONFIG_FILE), 'w') as file:
        json.dump(RUNTIME_CONFIG, file)
    print(' [done]')


    ## Merge .pyx definition files into one
    print(f"\u2022 Generating {PYX_MAIN} file", end='')
    with open(PYX_MAIN, 'w') as f_out: # All source code will be merged to this file
        # Insert a header comment in the output file
        f_out.write('\n'.join([
            "'"*3,
            f'Author: {AUTHOR}',
            'Description: This is an autogenerated source file made by the setup.py script.',
            'It contains all Cython definitions (methods & classes) of this library extension in order to interact with lib3d_mec_ginac',
            f'Version : {VERSION}',
            "'"*3
        ]))
        f_out.write('\n'*3)

        for filename in PYX_FILES:
            with open(filename, 'r') as f_in:
                code = sub("'''.*?'''", '#'*8 + f' {filename} ' + '#'*8, f_in.read(), count=1, flags=DOTALL)
                f_out.write(code)
                f_out.write('\n'*3)
    print(' [done]')



    ## Generate C-Python extension
    print('\u2022 Generating cpython extension', end='')
    with output_suppressed():
        extensions = cythonize(EXTENSIONS,
            compiler_directives={'language_level': 3}, nthreads=2, force=True)
    print(' [done]')


    ## Invoke distutils setup
    print("\u2022 Compiling extension and installing package", end='')
    with output_suppressed():
        setup(
            name=NAME,
            version=VERSION,

            author=AUTHOR,
            author_email=AUTHOR_EMAIL,

            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            license=LICENSE,

            keywords=KEYWORDS,
            classifiers=CLASSIFIERS,

            packages=PACKAGES,
            package_dir={ROOT_PACKAGE: ROOT_PACKAGE_DIR},
            package_data={ROOT_PACKAGE: [RUNTIME_CONFIG_FILE, 'examples']},
            ext_modules=extensions,
            cmdclass={'build_ext': BuildExt},
        )
    print(' [done]')


    # Helper tip
    print(f'Type python -i -c "from {ROOT_PACKAGE} import *" to open a console with this library imported')
