
Prerequisites & Installation
-----------------------------------

This library works under a 64-bit ubuntu operative system. ubuntu 18.04
is known to work fine. Older versions are not test but they are probably compatible as well

This next sections explains how to get all the required dependencies and build
pylib3d-mec-ginac from scratch.
You can also use the library and test its features without any installation process
by downloading a precompiled docker image from the github package registry or running `this notebook online <https://pylib3d-mec-ginac.herokuapp.com/notebooks/Untitled.ipynb>`_.
This is explained more in detail in the :ref:`guide:Quick guide & examples` section



Dependencies
=============================

You need the next packages:

:g++>=7.4.0: A C/C++ compiler. This is needed to compile the Python bindings for the
    lib3d-mec-ginac C++ library.

:git: Version control system. This tool is used to download the source code of this library
    from Github

:mesa-utils>=8.4.0: Utilities for OpenGL Mesa library. This is needed to render the 3D graphical
    environment, as the packages below

:libsm6>=1.2.2: X11 session management library

:libxrender1>=0.9.10: X rendering extension client library

:libfontconfig1>=2.12.6: Generic font configuration library


Also the next libraries are needed, but their binary files are distributed within this software.
You dont need to install any of them.

:lib_3d_mec_ginac>=1.0.0: This is the C++ framework that this library aims to extend to the Python language.
:GiNaC: C++ library for symbolic computation

:ginac>=1.7.7: Framework for symbolic computation implemented in C++

:cln>=1.3.4: Library for numeric computation also in C++



Python version 3.6 or later and pip are required. Python 3.6 and 3.7 versions were
succesfully tested with this library.

All of this dependencies can be installed with:

::

    sudo apt install -y \
        g++ git mesa-utils libsm6 libxrender1 libfontconfig1   \
        python3.7 python3.7-dev python3-pip curl               \
    && curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py \
    && sudo python3.7 get-pip.py && rm get-pip.py

.. note::
    The last two lines are used to install pip specifically for python3.7 ( also
    the package python3-pip is required )

Make sure that your default python and pip points to the 3.7 version

::

     update-alternatives --install /usr/bin/python python3.7 /usr/bin/python3.7 1 \
    && update-alternatives --install /usr/bin/pip pip3.7 /usr/bin/pip.3.7 1

.. note::

    To check their default versions, execute::

        python --version && pip --version






Installation
=============================

- First download the source code using git:

    ::

        git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git -b stable

    The ``-b stable`` option is used to select the last stable release of the library.
    The development version will be selected if this
    option is not set.

- Get all python package dependencies with pip and the requirements text file:

    ::

        cd pylib3d-mec-ginac
        pip install -r requirements.txt

- Finally install the library with setuptools:

    ::

        python setup.py install

- Verify the installation by importing the package ``lib3d_mec_ginac`` inside the interpreter:

    ::

        python -c "import lib3d_mec_ginac"
