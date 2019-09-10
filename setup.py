'''
Author: Víctor Ruiz Gómez
Description:
Setup script to install pylib3d-mec-ginac library.
'''

# Import statements
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
from os import listdir
from os.path import join
from io import StringIO


######## PACKAGE DESCRIPTION ########

# Name of this library
NAME = 'pylib3d-mec-ginac'

# Version of the library
VERSION = '1.0.0'

# Author details
AUTHOR = 'Victor Ruiz Gomez'
AUTHOR_EMAIL = 'victorruizgomezdev@gmail.com'

# Library description
DESCRIPTION=''
LONG_DESCRIPTION=''

# License
with open('LICENSE', 'r') as f:
    LICENSE = f.read()

# Classifiers
CLASSIFIERS = [
    'Development Status :: 1 - Planning',
    'Framework :: Buildout :: Extension',
    'Programming Language :: Cython',
    'Programming Language :: C++'
]


######## PYTHON PACKAGE SETUP ########

# Name of the library inside python
PACKAGE = 'lib3d_mec_ginac'

# Diretory where source files of the package can be found
PACKAGE_DIR = 'src'



######## C EXTENSION CONFIGURATION VARIABLES ########

# This variable points to the directory where lib3d-mec-ginac library lives
LIB3D_MEC_GINAC_DIR = '../lib3d-mec-ginac'

# Directories containing header files used to build the extensions
INCLUDE_DIRS = [
    '/usr/local/include',
    '/usr/include',
    f'{LIB3D_MEC_GINAC_DIR}/include/lib_3d_mec_ginac'
]

# Directories to search for libraries at link time
LIBRARY_DIRS = [
    f'{LIB3D_MEC_GINAC_DIR}/lib',
    '/usr/local/lib'
]

# Directories to search for dynamic libraries at runtime
RUNTIME_LIBRARY_DIRS = [
    f'{LIB3D_MEC_GINAC_DIR}/lib'
]

# Name of the libraries for the extensions to link against
LIBRARIES = [
    'cln',
    'ginac',
    '_3d_mec_ginac-2.0'
]

# Here we merge all cython source (from .pyx files) to generate just 1 dynamic
# library
source = StringIO()
for filename in listdir('src'):
    if not filename.endswith('.pyx') or filename.startswith('main'):
        continue
    with open(join('src', filename), 'r') as file:
        source.write(file.read())
        source.write('\n')

# Merged source code will be written in src/merged.pyx
with open(join('src', 'merged.pyx'), 'w') as file:
    file.write(source.getvalue())



# This list holds all the extensions defined by this library
EXTENSIONS = [
    Extension(
        name=f'{PACKAGE}_ext',
        sources=['src/merged.pyx', 'src/extern.cpp'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        runtime_library_dirs=RUNTIME_LIBRARY_DIRS,
        libraries=LIBRARIES,
        language='c++',
        extra_compile_args=['-w']
    )
]



# Now invoke distutils setup
setup(
    name=NAME,
    version=VERSION,

    author=AUTHOR,
    author_email=AUTHOR_EMAIL,

    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    license=LICENSE,

    classifiers=CLASSIFIERS,

    packages=[PACKAGE],
    package_dir={PACKAGE:PACKAGE_DIR},
    ext_modules=cythonize(EXTENSIONS, compiler_directives={'language_level': 3}),
)
