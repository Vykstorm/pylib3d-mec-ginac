'''
Author: Víctor Ruiz Gómez
Description: Configuration file for the Sphinx documentation builder.

The extension of this library must be built locally before generating the docs with:
python setup.py build_ext --inplace
'''


# Add the project root directory to sys path
from os.path import abspath, join
import sys
sys.path.insert(0, abspath('..'))

import src
sys.modules['lib3d_mec_ginac'] = src


######## PROJECT INFORMATION ########

# Load information from setup script
from setup import AUTHOR, PACKAGE, VERSION

project = PACKAGE
copyright = f'2019, {AUTHOR}'
author = AUTHOR
release, version = VERSION, VERSION


######## GENERAL CONFIGURATION ########

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx"
]
templates_path = ['templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


######## AUTODOC CONFIGURATION ########

if 'sphinx.ext.autodoc' in extensions:
    autodoc_typehints = 'signature'
    autodoc_docstring_signature = True


######## INTERSPHINX CONFIGURATION ########

if 'sphinx.ext.intersphinx' in extensions:
    intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


######## OPTIONS FOR HTML OUTPUT ########

html_theme = 'alabaster'
html_static_path = ['static']
