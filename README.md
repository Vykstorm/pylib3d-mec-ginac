
## Introduction

This package is an extension of the symbolical C++ library lib3d_mec_ginac for Python.

[lib3d_mec_ginac](http://www.imem.unavarra.es/3d_mec/download/lib3d-mec-ginac/eccomas2007_paper.pdf) provides all the features of a modern symbolic kernel (matrix algebra, expressions atomization, trigonometric simplifications, ...).

But it is designed specifically to pose and solve equations in dynamical mechanical multibody systems.

pylib3d_mec_ginac brings all the features of this library to a high level interpreted language with a clean and easy to use API.



## Installation

First you need g++, openGL, libSM and git ( to download this project source code ):
```bash
sudo apt update
sudo apt install -y g++ mesa-utils libsm6 libxrender1 libfontconfig git
```

Then install python3 & pip:
```bash
sudo apt install python3 python3-pip
```
If you are using anaconda, you can create a new virtual environment with python3
```bash
conda create -n myenv python=3.7
```


Now install this library with setuptools:
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

You can run jupyter notebooks to define your mechanical system while you simulate it in the 3D viewer.

Execute the next line:
```bash
python -m lib3d_mec_ginac.jupyter
```

### Try it online

Finally you can run a jupyter notebook and use this library. No installation needed, but features are limited ( 3D viewer is not avaliable ).

[Try it now!](https://pylib3d-mec-ginac.herokuapp.com/notebooks/Untitled.ipynb)




## Docker integration

You can build a docker image with ubuntu 18.04 + python 3.7 + this library ( and all its dependencies ) installed.

The next bash lines will pull & run the image from this repository. An interactive Python console will be open with all the functions & classes of the API already imported.

```bash
IMAGE=docker.pkg.github.com/vykstorm/pylib3d-mec-ginac/pylib3d-mec-ginac:1.0.0
sudo docker pull $IMAGE
sudo docker run -it $IMAGE
>>> ...
```

There are also other useful docker images you can try. Go to the [Github packages](https://github.com/Vykstorm/pylib3d-mec-ginac/packages) section of this repo.




## Documentation

Most of the classes and methods of this extension have docstrings. You can use the command ```help``` inside the Python interpreter to get information about them
e.g:
```python
from lib3d_mec_ginac import System
help(System)
```

Also [this page](https://pylib3d-mec-ginac-docs.herokuapp.com/) contains the reference of the API and a quick start tutorial.





## Examples


This library provides a few usage examples under the directory ``examples/``


You can test the ``four_bar`` example easily by typing the next line in your terminal (your working directory must be the root of this repository):
```bash
python -m lib3d_mec_ginac examples/four_bar
```



## License

This project is under [GPLv3 license](LICENSE.txt)
