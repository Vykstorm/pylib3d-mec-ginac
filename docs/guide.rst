

Quick guide & examples
-----------------------------------

This section describes the basic features of this library.
You should read first the :ref:`install:Prerequisites & Installation` section if you wish to install
it.

Once you've got pylib3d-mec-ginac in your system, it can be used within the python interpreter::

    python -i -c "from lib3d_mec_ginac import *"
    >>> ...


There is an alternative and easiest way that skips the installation
process which is described in the next section.


Using dockerfiles
===============================

You can download a docker image with ubuntu 18.04 and this library ( including its
dependencies ) already installed and run a python interactive prompt with the public
classes & functions in the API of pylib3d-mec-ginac already imported::

    sudo apt install -y docker.io
    IMAGE=docker.pkg.github.com/vykstorm/pylib3d-mec-ginac/pylib3d-mec-ginac:latest
    sudo docker pull $IMAGE
    sudo docker run -it $IMAGE
    >>> ...

The library installed on the docker image is the latest stable version.
Other versions are avaliable at the `Github packages <https://github.com/Vykstorm/pylib3d-mec-ginac/packages>`_


The 3D viewer
===============================

The mechanical system that you create programatically in the python interpreter, can
be shown in a interactive graphical environment.
The next line opens the Python prompt and the 3D viewer::

    python -m lib3d_mec_ginac

This code::

    >>> draw_frame('abs')
    >>> v = new_vector('v', 1, 1, 1)
    >>> p = new_point('p', v)
    >>> draw_point(p)
    >>> draw_vector('O', v)

will be shown in the viewer like this ( it draws the absolute frame reference, a point and a
vector ):

.. image:: images/3D_viewer.png
