
## Introduction

lib3d_mec_ginac is a library for multibody mechanial systems simulations (http://www.imem.unavarra.es/3d_mec/download/lib3d-mec-ginac/eccomas2007_paper.pdf)
It was developed in C++ due to its performance requirements on symbolic numeric computation tasks.

This module provides bindings to the Python language and additional features to improve interaction between the user and the library.


## Installation

First, you need to install [lib3d_mec_ginac](https://bitbucket.org/lib3d-mec-ginac/lib3d-mec-ginac/src/master/) library and its dependencies.

-Install python>=3.7 and pip3

e.g: In ubuntu 18.04 bionic, you can do:
```bash
sudo apt install python3.7 pyhthon3.7-dev python3-pip
pip install pip --upgrade
```    
For the rest of this document, it is assumed that the default version of python and pip are 3.7 and 3 respectively.


-Clone the repository of this module in the same location as the lib3d_mec_ginac library (this is important if you didn't install it in the system, so that dynamic libraries can be found).
```bash
git clone https://Vykstorm@bitbucket.org/lib3d-mec-ginac/pylib3d-mec-ginac.git
cd pylib3d-mec-ginac
```
Note: You can also tune ```LD_LIBRARY_PATH``` and ```CFLAGS``` to indicate where lib3d_mec_ginac headers and dynamic libraries are located.


-Install all library dependencies via pip:
```bash
pip install -r requirements.txt
```

-Finally build & install the module in your system via setup script:
```bash
python setup.py install
```


-Now import the module to verify the installation:
```bash
python -c "import lib3d_mec_ginac"
```

-If you wish to use lib3d-mec-ginac in your jupyter notebooks, you can install the jupyter kernel for this library:

```bash
jupyter kernelspec install src/jupyter --replace --user --name=lib3d_mec_ginac
```




## Documentation

Most of the classes and methods of this extension have docstrings. You can use the command ```help``` inside the Python interpreter to get information about them
e.g:
```python
from lib3d_mec_ginac import System
help(System)
```

Also, ```docs/``` directory contains documentation pages formatted with reStructuredText syntax. They can be rendered to html/pdf with sphinx (You need to install this library first or build the extension locally with ```python setup.py build_ext --inplace```)

Use the Makefile in ```docs/``` for that task. To build html pages, you can do:
```bash
cd docs
make html
```
The HTML index page will be in ```docs/_build/html/index.html```


If you dont want to generate documentation by hand, you can view it on [this page](http://vykstorm.pythonanywhere.com/).

## Usage

### Python interactive console + 3D viewer

To start using the library just type:

```bash
python -m lib3d_mec_ginac
```

This will open a python terminal and the 3D viewer which shows the mechanical system simulation.

In the terminal, you can use any of the classes & methods avaliable from the public API.
For example, you can draw the frame called ``abs``
```python
>>> draw_frame('abs')
```

If you wish to execute python code from a script (lets say ``foo.py``) and then open the 3D viewer and the python interactive prompt, you can type:
```bash
python -m lib3d_mec_ginac foo.py
```

### Just like a regular Python package

lib3d-mec-ginac can be imported as a package from your scripts or in a normal python terminal:

```
python
>>> from lib3d_mec_ginac import *
```
Beware that if you call ``show_viewer()`` to open the 3D viewer, your script (or the python prompt) will be blocked until the viewer is closed.



### Jupyer notebook + 3D viewer

Finally, you can run jupyter notebooks to define your mechanical system and visualize it in the 3D viewer.

First write:
```bash
python -m lib3d_mec_ginac --no-console
```

In another console type to run jupyer:
```bash
jupyter notebook
```
Create a new python notebook and change the kernel to ``lib3d_mec_ginac``




## Examples


This library provides a few usage examples under the directory ``examples/``


You can test the ``four_bar`` example easily by typing the next line in your terminal (your working directory must be the root of this repository):
```bash
python -m lib3d_mec_ginac examples/four_bar
```




## License

This project is under [GPLv3 license](LICENSE.txt)
