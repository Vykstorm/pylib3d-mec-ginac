
How to add new features to this library ?
-----------------------------------

In this section we will cover how to integrate or modify the features that this
library provides.
The first thing you need to know is what kind of functionality you are going to
implement. Here is a list of possible things you may want:

- You need to include a new algorithm added to the C++ library lib3d_mec_ginac into Python
- You need to update or optimize an existing method of the C++ lib3d_mec_ginac without touching the Python interface

On the second case, you only need to compile lib3d_mec_ginac and ship the new header
files and the dynamic libraries into this library.
Suppose that you have a folder called 'lib_3d_mec_ginac' in your current working
directory containing the source code of the C++ library.


.. _build:

Create a temporal directory build that will be the folder where lib_3d_mec_ginac
will be installed.
Now configure & compile it::


    cd lib_3d_mec_ginac
    ./configure=$(pwd)/../build/
    make && make install


Go the build directory and download pylib3d-mec-ginac::

    cd ../build
    git clone https://github.com/Vykstorm/pylib3d-mec-ginac.git -b stable


The next step is to copy the header files & binaries of lib_3d_mec_ginac to the library::

    cp -r include/lib_3d_mec_ginac/*.h pylib3d-mec-ginac/include/
    cp -L lib/lib_3d_mec_ginac-2.0.so pylib3d-mec-ginac/lib/linux/x86_64/lib_3d_mec_ginac.so


Finally install the Python package::

    cd pylib3d-mec-ginac
    python setup.py install || cat setup.log.txt


Verify the installation with::


    python -c "import lib3d_mec_ginac"



Add a new C++ algorithm to the Python interface
=============================

Now suppose we are in the first scenario where we need to include a new
C++ lib_3d_mec_ginac feature into the interface.

First, you need to know where your algorithm should be inyected in the library`s

All source code that manages the communication between Python and lib_3d_mec_ginac
are located under the src/core/pyx and src/core/pxd:

- Files inside src/core/pyx have the extension .pyx and they provide
  the implementation of all python methods that requires the use of any C++ routine.
  They are written in Cython language. Its syntax its closed to Python but also adds
  aditional features in order to use C++ classes & functions.

- Files under src/core/pxd have only one purpose: Declare all C++ items
  that are going to be accesed by any .pyx module.


As an example, suppose we added a new function to the class System::

    int System::foo(int a) {
        return a * a * a;
    }

First, we need to declare the method foo in src/core/pxd/csystem.pxd.
It should look like this::

    ...
    cdef extern from "System.h":

        cdef cppclass System:
            ...

            int foo(int)



And now we define foo function ( Python side ) in the file src/core/pyx/classes/system.pyx::

    ...
    cdef class System:
        ...
        cpdef foo(self, a):
            return self._c_handler.foo(a)
        ...


In the code above, ``self._c_handler`` is a C++ instance of the class System and
``self._c_handler.foo`` represents the function ``foo`` at the C++ side.

.. note::

    Cython converts automatically the value of the input variable from a Python integer to
    a C integer ( the same is applied for the return value ).
    This is a very simple example. For more complex operations and data conversions, refer to
    the `Cython documentation <https://cython.readthedocs.io/en/latest/>`_ )


Finally we follow the steps specified at the beginning of this section to install the library
again ( `How to add new features to this library ?`_ ) and test our method::

    python
    >>> from lib3d_mec_ginac import *
    >>> sys = System()
    >>> sys.foo(2)
    8


The next section describes the previous steps more in detail needed in order to port the function ``matrix_list_optimize``
to Python.

Porting matrix_list_optimize function to Python
=============================

What we want is to use matrix_list_optimize with Python. This routine is defined in the
header file Globals.h, takes three arguments by reference ( a Matrix and two GiNaC::lst objects ) and has
no return value.

First we declare it in a .pxd file, in this case we add it to src/core/pxd/cglobals.pxd::

    from src.core.pxd.cmatrix cimport Matrix
    from src.core.pxd.ginac.clst cimport lst
    ...
    cdef extern from "Globals.h":
        ...
        void matrix_list_optimize(Matrix&, lst&, lst&)
        ...

.. note::

    The first two lines imports the declarations for the lst and Matrix classes.


The next step is to define the function in Python ( We will include its implementation in
the script src/core/pyx/globals.pyx )::

    ...
    cpdef matrix_list_optimize(matrix):
        ...
    ...

Our method must satisfy the next conditions:

- It will take only 1 argument ( the matrix object to optimize )
- Return two values: The matrix itself and a dictionary where keys are atom names
  and their corresponding values, their expressions.

Example ( Matrix Phi extracted from four bar example ) ::

    >>> Phi
    [ atom217*atom10+atom216*atom11-l4  atom10*atom216-atom217*atom11 ]
    >>> Phi_2, atoms = matrix_list_optimize(Phi)
    >>> atoms
    {'atom209': '-sin(theta3)*l3',
     'atom21': 'sin(theta2)',
     'atom20': 'cos(theta2)',
     'atom210': 'l2+l3*cos(theta3)',
     'atom217': 'atom209*atom21+atom20*atom210+l1',
     'atom10': 'cos(theta1)',
     'atom216': '-atom21*atom210+atom209*atom20',
     'atom11': 'sin(theta1)'}

Now we write the body of the function. First, C++ matrix_list_optimize must be invoked,
passing the matrix object as reference and two GiNaC::lst objects::

    ...
    cpdef matrix_list_optimize(matrix):
        cdef c_lst atom_lst
        cdef c_lst expr_lst
        cdef c_Matrix* c_matrix

        c_matrix = matrix._get_c_handler()

        c_matrix_list_optimize(c_deref(c_matrix), atom_lst, expr_lst)
    ...


.. note::

    - All methods from C++ are prefixed with ``c_``, including classes::

        GiNaC::lst -> c_lst
        lib_3d_mec_ginac::Matrix -> c_Matrix

    - Variables with C++ static types must be declared using the ``cdef`` word followed
      by the type identifier.

    - ``c_deref`` is a special function which implements the derreference operation
      ( matrix is taken by value by the method matrix_list_optimize ).

    - ``matrix._get_c_handler()`` gets a pointer to the matrix C++ instance


Now atoms & exprs are lists of GinaC::ex objects. With them, we need to build a dictionary
mapping the atoms list to their expressions::

    # This will store the ith atom on the loop below ( GiNaC::symbol instance )
    cdef c_symbol atom
    # This will store the ith expression on the loop below ( GiNaC::ex instance )
    cdef c_ex expr

    # This will be our dictionary
    output = {}
    for i in range(0, atom_lst.nops()):
        atom = c_ex_to[c_symbol](atom_lst.op(i))
        expr = expr_lst.op(i)

        atom_name = (<bytes>atom.get_name()).decode()
        output[atom_name] = _expr_from_c(expr)


.. note::

    - To access the ith-atom & ith-expression in both lists, we are going to use the
      method ``GiNaC::ex::op``, and ``GiNaC::ex::nops`` to fetch the number of items::

    - ``c_ex_to`` is the Cython version of the ``GiNaC::ex_to`` C++ template function.
      c_ex_to[c_symbol] converts the input ``GiNaC::ex`` into a ``GiNaC::symbol``

    - ``GiNaC::symbol::get_name`` returns the name of the atom as a std::string

    - Given a std::string instance ``x``, it can be converted to an standard Python
      string with ``(<bytes>x).decode()``

    - Finally, ``_expr_from_c`` turns a C++ ``GiNaC::ex`` instance into a Python
      symbolic expression ( Expr class )

The complete implementation can be found `here <https://github.com/Vykstorm/pylib3d-mec-ginac/blob/master/src/core/pyx/globals.pyx#L163>`_

.. note::

    Make sure that the input matrix is a valid Matrix class instance. You need to
    add a previous check before executing any code. Otherwise it can result in unexpected
    behaviours or even a segmentation fault error::

        cpdef matrix_list_optimize(matrix):
            if not isinstance(matrix, Matrix):
                raise TypeError
            ...




Porting the method Base.angular_velocity to Python
=============================

Now we need to expose the C++ class method ``angular_velocity`` defined in the
class ``Base``

First, add the ``angular_velocity`` method definition to ``src/core/pxd/cbase.pxd``::

    ...
    from src.core.pxd.cvector3D cimport Vector3D
    ...
    cdef extern from "Base.h":
        cdef cppclass Base:
            ...
            Vector3D angular_velocity()
            ...

.. note::

    We need to include the definition of ``Vector3D`` class with the import directive


Now we define the method ``get_angular_velocity`` in the Python Base class
( defined in ``src/core/pyx/classes/base.pyx`` )::

    ...
    cdef class Base:
        ...
        cpdef get_angular_velocity(self):
            return _vector_from_c_value(self._c_handler.angular_velocity())
        ...


.. note::

    - ``self._c_handler`` its a pointer to the lib_3d_mec_ginac::Base instance.
    - ``_vector_from_c_value`` converts a C++ Vector3D object into a Python Vector3D instance.


Install again the library and test the new feature::

    python
    >>> b = new_base('b', 'xyz')
    >>> b.get_angular_velocity()
    [
    0,
    0,
    0
    ] base "xyz"

But we need to fix a problem: calling to ``get_angular_velocity`` on the default base will lead to a segmentation fault
error because it dont have a preceding base. We could add an aditional check so that an error
is raised in that case::

    cpdef get_angular_velocity(self):
        cdef c_Base* c_prev_base = self._c_handler.get_Previous_Base()
        if c_prev_base == NULL:
            raise RuntimeError('Cant compute the angular velocity for this base')
        ...

Now::

    python
    >>> get_base('xyz').get_angular_velocity()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "src/core/pyx/main.pyx", line 4301, in lib3d_mec_ginac_ext.Base.get_angular_velocity
        cpdef get_angular_velocity(self):
      File "src/core/pyx/main.pyx", line 4309, in lib3d_mec_ginac_ext.Base.get_angular_velocity
        raise RuntimeError('Cant compute the angular velocity for this base')
    RuntimeError: Cant compute the angular velocity for this base



The complete implementation of this method can be found `here <https://github.com/Vykstorm/pylib3d-mec-ginac/blob/master/src/core/pyx/classes/base.pyx#L91>`_
