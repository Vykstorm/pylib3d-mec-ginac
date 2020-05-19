'''
Author: Víctor Ruiz Gómez
Description:
Setup script to install pylib3d-mec-ginac library.
'''

# Import statements


# setuptools & distutils
from setuptools.command.build_ext import build_ext
from distutils.core import setup
from distutils.extension import Extension
from sysconfig import get_path

# system, os & file managing
import os, sys
from sys import version_info
from os import listdir, environ
from os.path import join, abspath, dirname, relpath, exists
from shutil import copyfile

# other imports
from functools import partial
from operator import methodcaller
from re import sub, DOTALL
from itertools import chain
import json
from contextlib import contextmanager
import builtins
from io import StringIO
import subprocess



######## INSTALLATION CONFIGURATION ########

# Remove all graphical interface modules ( minimum installation )
INSTALL_GUI = environ.get('INSTALL_GUI', 'yes') in ('yes', 'true')



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
LICENSE = 'GPLv3'


# Classifiers
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Buildout :: Extension',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Cython',
    'Programming Language :: C++',
    'Operating System :: POSIX :: Linux',
    'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
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
_packages = ['.core', '.utils']
if INSTALL_GUI:
    _packages.extend(['.drawing', '.gui', '.gui.idle'])

PACKAGES = list(chain([ROOT_PACKAGE], map(ROOT_PACKAGE.__add__, _packages)))

# Configuration file where runtime settings will be stored (relative to the root package)
RUNTIME_CONFIG_FILE = 'config.json'

# Extra files included on each package
PACKAGE_DATA = {
    ROOT_PACKAGE: [RUNTIME_CONFIG_FILE]
}
if INSTALL_GUI:
    PACKAGE_DATA[f'{ROOT_PACKAGE}.gui.idle'] = ['*.def', 'Icons/*']



######## C COMPILER CONFIGURATION ########

# Directory containing header files used to build the extensions
INCLUDE_DIR = 'include'

# Directory where to search for dynamic libraries
LIBRARIES_DIR = 'lib/linux/x86_64'

# Name of the dynamic libraries to use
LIBRARIES = [
    'cln',
    'ginac',
    '_3d_mec_ginac'
]

# Directory where to search for dynamic libraries at runtime
if exists(get_path('platlib')):
    RUNTIME_LIBRARIES_DIR = get_path('platlib')
else:
    RUNTIME_LIBRARIES_DIR = get_path('platstdlib')





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
    ]),

    # Extra modules
    ['constants.pyx']
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
        include_dirs=[INCLUDE_DIR],
        library_dirs=[abspath(LIBRARIES_DIR)],
        runtime_library_dirs=[RUNTIME_LIBRARIES_DIR],
        libraries=LIBRARIES,
        language='c++',
        extra_compile_args=['-w']
    )
]



######## PACKAGE DEPENDENCIES ########

# Compatible python version
PYTHON_VERSION = '>=3.7'

# Package dependencies
with open(join(root_dir, 'requirements.txt'), 'r') as file:
    DEPENDENCIES = file.readlines()

# Extra dependencies to be processed by setup tools
DEPENDENCIES += [
    'asciitree>=0.3.3',
    'tabulate>=0.8.5',
    'numpy>=1.17.2'
]

if INSTALL_GUI:
    DEPENDENCIES.append('vtk-tk>=9.0.0')

# Extra dependency links
DEPENDENCY_LINKS = []
if INSTALL_GUI:
    DEPENDENCY_LINKS.append('https://vtk-tk-support.herokuapp.com/')




######## RUNTIME CONFIGURATION ########


RUNTIME_CONFIG = {
    # openscad command line utility executable (this is used to convert scad
    # to stl files).
    'OPENSCADCMD': 'openscad',

    # Enable/Disable atomization by default
    'ATOMIZATION': 'off',

    # Gravity direction by default
    'GRAVITY_DIRECTION': 'up',

    # Default simulation update frequency
    'SIMULATION_UPDATE_FREQUENCY': 30,

    # Default simulation time multiplier
    'SIMULATION_TIME_MULTIPLIER': 1
}











######## INSTALLATION PROCEDURE ########

if __name__ == '__main__':


    ## Helper functions & variables

    # File where installation logs will be written
    logfile = open('setup.log.txt', 'w')

    # Context manager to supress messages on stdout and stderr
    @contextmanager
    def output_suppressed():
        prev_stdout, sys.stdout = sys.stdout, logfile
        prev_stderr, sys.stderr = sys.stderr, logfile
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
    try:
        from Cython.Build import cythonize
    except ImportError:
        # Generate error message if missing dependencies
        print('Failed to import Cython')
        print('Make sure to install Cython before you run the installation process')
        exit(-1)
    print(" [done]")


    ## Create config.json (this is used to configure the library at runtime)
    print(f"- Generating runtime settings file", end='')
    with open(join(ROOT_PACKAGE_DIR, RUNTIME_CONFIG_FILE), 'w') as file:
        json.dump(RUNTIME_CONFIG, file)
    print(' [done]')


    ## Merge .pyx definition files into one
    print(f"- Generating {PYX_MAIN} file", end='')
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



    ## Finally install runtime dependency libraries
    print('- Installing runtime dependency libraries', end='')
    with output_suppressed():
        for lib in listdir(LIBRARIES_DIR):
            src, dst = join(LIBRARIES_DIR, lib), join(RUNTIME_LIBRARIES_DIR, lib)
            print(f'Copying file {src} to {dst}')
            copyfile(src, dst)
    print(' [done]')


    ## Generate C-Python extension
    print('- Generating cpython extension', end='')
    with output_suppressed():
        extensions = cythonize(EXTENSIONS,
            compiler_directives={'language_level': 3}, nthreads=2, force=True)
    print(' [done]')


    ## Invoke distutils setup
    print("- Compiling extension and installing package", end='')
    with output_suppressed():
        setup(
            name=NAME,
            version=VERSION,

            author=AUTHOR,
            author_email=AUTHOR_EMAIL,

            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            long_description_content_type = 'text/markdown',
            license=LICENSE,

            keywords=KEYWORDS,
            classifiers=CLASSIFIERS,

            python_requires=PYTHON_VERSION,
            install_requires=DEPENDENCIES,
            dependency_links=DEPENDENCY_LINKS,
            packages=PACKAGES,
            package_dir={ROOT_PACKAGE: ROOT_PACKAGE_DIR},
            package_data=PACKAGE_DATA,
            ext_modules=extensions,
            cmdclass={'build_ext': BuildExt},
            zip_safe=False
        )
    print(' [done]')

    # Helper tip
    print(f'Type -> python -c "import lib3d_mec_ginac" <- to verify the installation')
    print(f'Type -> python -m lib3d_mec_ginac <- to start using the library in interactive mode')
