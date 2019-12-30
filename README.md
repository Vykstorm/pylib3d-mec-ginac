
## Introduction

This package is an extension of the symbolical C++ library lib3d_mec_ginac for Python.

[lib3d_mec_ginac](http://www.imem.unavarra.es/3d_mec/download/lib3d-mec-ginac/eccomas2007_paper.pdf) provides all the features of a modern symbolic kernel (matrix algebra, expressions atomization, trigonometric simplifications, ...).

But it is designed specifically to pose and solve equations in dynamical mechanical multibody systems.

pylib3d_mec_ginac brings all the features of this library to a high level interpreted language with a clean and easy to use API.



## Installation

Install it with setuptools:
```bash
git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git
cd pylib3d-mec-ginac
python setup.py install
```


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




## Examples


This library provides a few usage examples under the directory ``examples/``


You can test the ``four_bar`` example easily by typing the next line in your terminal (your working directory must be the root of this repository):
```bash
python -m lib3d_mec_ginac examples/four_bar
```




## License

This project is under [GPLv3 license](LICENSE.txt)
