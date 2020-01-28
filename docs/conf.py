'''
Author: Víctor Ruiz Gómez
Description: Configuration file for the Sphinx documentation builder.

The library must be installed using ``python setup.py install`` before building
the docs.
Use the Makefile located in the same directory where this script is located to generate the docs.
'''


# Add the project root directory to sys path

from os.path import abspath, join, dirname
import sys

sys.path.insert(0, abspath(join(dirname(__file__), '../..')))
sys.path.insert(0, abspath(join(dirname(__file__), '..')))



######## PROJECT INFORMATION ########

# Load information from setup script
from setup import AUTHOR, ROOT_PACKAGE, VERSION

project = ROOT_PACKAGE
copyright = f'2019, {AUTHOR}'
author = AUTHOR
release, version = VERSION, VERSION


######## GENERAL CONFIGURATION ########

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel"
]
templates_path = ['templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


######## AUTODOC CONFIGURATION ########

if 'sphinx.ext.autodoc' in extensions:
    autodoc_typehints = 'signature'
    autodoc_docstring_signature = True
    autodoc_member_order = 'bysource'


######## INTERSPHINX CONFIGURATION ########

if 'sphinx.ext.intersphinx' in extensions:
    intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


######## OPTIONS FOR HTML OUTPUT ########

html_theme = 'classic'
html_static_path = ['static']


######## MORE OPTIONS ########

autosectionlabel_prefix_document = True
