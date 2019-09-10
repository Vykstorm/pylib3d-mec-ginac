'''
Author: Víctor Ruiz Gómez
Description:
Setup script to install pylib3d-mec-ginac library.
'''

# Import statements
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


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


# Name of the library inside python
PACKAGE = 'lib3d_mec_ginac'

# Diretory where source files of the package can be found
PACKAGE_DIR = 'src'



# Directories containing header files used to build the extensions
INCLUDE_DIRS = [
    '../lib3d-mec-ginac/include/lib_3d_mec_ginac'
]

# Directories to search for libraries at link time
LIBRARY_DIRS = [
    #'../lib3d-mec-ginac/lib'
    '/usr/local/lib'
]

# Direcotires to search for dynamic libraries at runtime
RUNTIME_LIBRARY_DIRS = [
    '../lib3d-mec-ginac/lib'
]

# Name of the libraries for the extensions to link against
LIBRARIES = [
    'ginac',
    'cln',
    #'_3d_mec_ginac-2.0'
]


# This list holds all the extensions defined by this library
EXTENSIONS = [
    Extension(
        name=f'{PACKAGE}_ext',
        sources=['src/*.pyx'],
        include_dirs=INCLUDE_DIRS,
        library_dirs=LIBRARY_DIRS,
        runtime_library_dirs=RUNTIME_LIBRARY_DIRS,
        libraries=LIBRARIES,
        language='c++'
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
    ext_modules=cythonize(EXTENSIONS),
    zip_safe=False
)
