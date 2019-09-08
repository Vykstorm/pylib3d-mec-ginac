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

# This list holds all the extensions defined by this library
EXTENSIONS = [
    # Class System
    #Extension(f"{PACKAGE}.system", ["src/system.pyx"])

    # TODO
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
    ext_modules=cythonize(EXTENSIONS)
)
