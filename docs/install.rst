=================
Build and install
=================

``gmxapi`` comes in three parts. A modified version of GROMACS is necessary,
available from `github.com/kassonlab/gromacs-gmxapi <https://github.com/kassonlab/gromacs-gmxapi/>`_

Download the Python package from
`github.com/kassonlab/gmxapi <https://github.com/kassonlab/gmxapi/>`_.

A `sample plugin <https://github.com/kassonlab/sample_restraint>`_ demonstrates extending GROMACS with C++ code to be controlled
from the Python interface.

We recommend installing the Python package in a virtual environment.
If not installing in a virtual environment, you may not be able to install
necessary prerequisites.
You will need a few packages installed that are hard for gmxpy to install automatically.

Build System
============

The gmxapi Python package can be installed with ``pip`` (deprecated) or with ``cmake``.

Either way there are some Python modules that you will want to have installed either on the system or in a virtual
environment (see below). These are ``numpy``, ``networkx``, and ``mpi4py``. If you are on a system with multiple compilers or
multiple MPI implementations, refer to the mpi4py documentation to make sure you install it with the same compiler you
use for GROMACS and gmxapi. Namely, set the ``MPICC`` environment variable before running ``pip``.

CMake
~~~~~

Life is simpler if you don't build in the source directory, but it isn't a problem to build in a subdirectory of the
source directory.

Assuming you are in the source directory of the gmxapi repository,
::

    $ mkdir build
    $ cd build
    $ gmxapi_DIR=/path/to/gromacs cmake .. -DPYTHON_EXECUTABLE=``which python`` -DGMXAPI_USER_INSTALL=ON
    $ make install

Explicitly setting PYTHON_EXECUTABLE helps to make sure your preferred interpreter (version 2.7 or 3.x) is detected.
``GMXAPI_USER_INSTALL=ON`` tells CMake to install the Python package in your home directory where Python knows to look
for it since you might not have write access to the system Python installation.

DO NOT set ``GMXAPI_USER_INSTALL=ON`` if you are in a virtual environment (see below) or the package will be installed in a place that
is visible to Python interpreters outside of the current virtual environment, including other virtual environments,
which can lead to really confusing errors.

See below for more detailed instructions.

Pip
~~~~

Before proceeding, install / upgrade the Python package for ``cmake``. Note that it is not
sufficient just to have the command-line CMake tools installed.
::

    python -m pip install --upgrade pip
    pip install --upgrade setuptools
    pip install --upgrade scikit-build
    pip install --upgrade cmake

If not installing in a virtual environment and not installing as a privileged
user, you will want to append ``--user`` to the ``pip`` commands.
(E.g. ``python -m install --upgrade pip --user``)

If you will be running the testing suite, you also need ``virtualenv`` and ``tox``.
::

    pip install --upgrade tox

You do not need to install the ``gmxapi`` Python package in order to use
``gromacs-gmxapi`` to build MD plugins, but you will need it to run Python-level
tests. The Python interface produced by the
`sample restraint <https://github.com/kassonlab/sample_restraint>`_ is ``gmxapi``
compatible either way.

For all installation options, instead of a using a separate GROMACS installation,
you can have gmxapi download and build its own copy of GROMACS. This will simplify
installation, but may miss optimizations and tweaks that could improve performance
in HPC environments.

Instead of setting ``gmxapi_DIR``, set ``BUILDGROMACS=TRUE`` at the beginning of the ``pip`` command line.

Python virtual environments
===========================

In the world of Python, a virtual environment is a Python installation that is self-contained
and easy to activate or deactivate to allow normal Python use without additional concerns of
software compatibility.

Several systems of managing virtual environments exist. gmxapi is tested with
Python 3's built-in virtualenv and the add-on virtualenv package for Python 2.

The following documentation assumes you have installed a compatible version of GROMACS and
installed it in the directory ``/path/to/gromacs``. Replace ``/path/to/gromacs`` with the actual
install location below.

Anaconda
~~~~~~~~

Get and install `Anaconda <https://docs.anaconda.com/anaconda/install/>`_.
Alternatively, on an HPC system
it may already be provided with a ``module`` system. For example::

    $ module load gcc
    $ module load cmake
    $ module load anaconda3
    $ module load openmpi

You don't have to follow all of the instructions for setting up your login profile if you don't want to,
but if you don't, then the ``conda`` and ``activate`` commands below will have to be prefixed by your
conda installation location. E.g. ``~/miniconda3/bin/conda info`` or ``source ~/miniconda3/bin/activate myEnv``

Create a conda virtual environment. Replace ``myEnv`` below with whatever convenient name you choose.
::

    $ conda create -n myGmxapiEnv python=3 pip setuptools cmake networkx mpi4py

Activate, or enter the environment.
::

    $ source activate myGmxapiEnv

Install the GROMACS gmxapi fork.
::

    $ git clone https://github.com/kassonlab/gromacs-gmxapi.git gromacs
    $ mkdir build
    $ cd build
    $ cmake ../gromacs -DGMX_GPU=OFF -DGMX_THREAD_MPI=ON -DCMAKE_CXX_COMPILER=`which g++` -DCMAKE_C_COMPILER=`which gcc` -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-gmxapi
    $ make -j12 && make install
    $ source $HOME/gromacs-gmxapi/bin/GMXRC

Make sure dependencies are up to date.
::

    $ MPICC=`which mpicc` pip install --upgrade mpi4py

Install the Python module.
::

    $ git clone https://github.com/kassonlab/gmxapi.git gmxapi
    $ cd gmxapi


Pip
----

With pip you will need to install some additional dependencies. Also, note that ``pip`` version 10.0.0 did not work for a
gmxapi installation. The issue appears to have been fixed in more recent versions, but be aware.
::

    $ python -m pip install --upgrade pip
    $ pip install --upgrade setuptools
    $ pip install --upgrade scikit-build cmake networkx
    $ CC=`which gcc` CXX=`which g++` pip install .

CMake
-----

    $ mkdir build
    $ cd build
    $ CC=`which gcc` CXX=`which g++` cmake ..
    $

Take note whether the correct python executable is found. You may need to specify ``-DPYTHON_EXECUTABLE=`which python```
to cmake.

Note: we do not yet have a robust suggestion for setting up `tox` for running the test suite in a conda environment.
If you come up with a recipe, please let us know. Otherwise, don't worry if you are able to install
the package but can't get weird errors when you try to run the tests with tox. Instead, just use `pytest` or run the tests in a regular
(non-conda) Python virtualenv or no virtualenv at all.

virtualenv
~~~~~~~~~~

For the ensemble simulations features, you will need an MPI installation. On an HPC system, this means you will probably have to use ``module load`` to load a compatible set of MPI tools and compilers. Check your HPC documentation or try ``module avail`` to look for an ``openmpi``, ``mpich``, or ``mvapich`` module and matching compiler module. This may be as simple as
::

    $ module load gcc
    $ module load mpicc

Note that the compilers loaded might not be the first compilers discovered automatically by the build tools we will use below, so you may have to specify compilers on the command line for consistency. It may be necessary to require that GROMACS, gmxapi, and the sample code are built with the same compiler(s).

Create a Python virtual environment.
If using Python 2, use the ``virtualenv`` module. If it is initially not found, install it with ``python -m pip install virtualenv --user``. Then,
::

    $ python -m virtualenv $HOME/myvenv

For Python 3, use the ``venv`` module.
::

    $ python -m venv $HOME/myvenv

Activate the virtual environment. Your shell prompt will probably be updated with the name of the environment you created to make it more obvious.
::

    $ source $HOME/myvenv/bin/activate
    (myvenv)$

Don't do it now, but you can deactivate the environment by running ``deactivate``.

Install some dependencies. For MPI, we use mpi4py. Make sure it is using the same MPI installation that we are building GROMACS against and building with compatible compilers.
::

    (myvenv)$ python -m pip install --upgrade pip networkx
    (myvenv)$ MPICC=`which mpicc` pip install --upgrade mpi4py

If you will be running the testing suite, you also need ``virtualenv`` and ``tox``.
::

    (myenv)$ pip install --upgrade tox

Get a copy of this repository, if you haven't already. For a released version, you can just download a source package.
::

    (myvenv)$ wget https://github.com/kassonlab/gmxapi/archive/v0.0.4.zip
    (myvenv)$ unzip v0_0_4.zip
    (myvenv)$ cd gmxapi-v0_0_4

For a development branch, you should probably clone the repository. You may not already have ``git`` installed on your system or you may need to load a module for it on an HPC system, which you will need to do before trying the following.
::

    (myenv)$ git clone https://github.com/kassonlab/gmxapi.git
    (myenv)$ cd gmxapi

If installing with CMake, install as above.

Pip
----

Update your environment and install some dependencies.
::

    (myvenv)$ pip install --upgrade setuptools
    (myvenv)$ pip install --upgrade scikit-build cmake networkx

For simplicity, let this package build and install a local GROMACS for you by setting the BUILDGROMACS environment variable. To be on the safe side, make sure to give hints to use the compilers you intend.
For instance, if we loaded a gcc module, help make sure pip doesn't default to the system ``/bin/cc`` or some such.
::

    (myenv)$ BUILDGROMACS=TRUE CC=`which gcc` CXX=`which g++` pip install .

This will take a while because it has to download and install GROMACS as well. If you want more visual stimulation, you can add ``--verbose`` to the end of the pip command line.

Documentation
=============

Documentation for the Python classes and functions in the gmx module can
be accessed in the usual ways, using ``pydoc`` from the command line or
``help()`` in an interactive Python session.

Additional documentation can be browsed on
`readthedocs.org <http://gmxapi.readthedocs.io/en/readthedocs/>`__ or
built with Sphinx after installation.

To build the user documentation locally, first make sure you have sphinx
installed, such as by doing a ``pip install sphinx`` or by using
whatever package management system you are familiar with. You may also
need to install a ``sphinx_rtd_theme`` package.

Build the gmx module, then use the ``docs`` make target. Assuming you are in the build directory::

    $ make
    $ make docs

Then open ``docs/index.html``

Note that this only puts the built documentation in your build directory.

Custom docs install location
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have already installed the package, you can build the docs to any destination folder you want from the repository directory.
Decide what directory you want to put the docs in and call
``sphinx-build`` to build ``html`` docs from the configuration in the
``docs`` directory of the gmxpy repository.

Assuming you downloaded the repository to ``/path/to/gmxapi`` and you
want to build the docs in ``/path/to/docs``, do

::

    sphinx-build -b html /path/to/gmxapi/docs /path/to/docs

or

::

    python -m sphinx -b html /path/to/gmxapi/docs /path/to/docs

Then open ``/path/to/docs/index.html`` in a browser.

Testing
=======

Unit tests are performed individually with ``pytest`` or as a full
installation and test suite with ``tox``.

From the root of the repository::

    $ gmxapi_DIR=/path/to/gromacs tox

For pytest, first install the package as above. Then,

::

    $ pytest --pyargs gmx -s --verbose

For a more thorough test that includes the parallel workflow features,
make sure you have MPI set up and the ``mpi4py`` Python package.

::

    mpiexec -n 2 python -m mpi4py -m pytest --log-cli-level=DEBUG --pyargs gmx -s --verbose

Note: ``tox`` may get confused when it tries to create virtual
environments when run from within a virtual environment. If you get
errors, try running the tests from the native Python environment or a
different virtual environment manager (i.e. not conda). And let us know
if you come up with any tips or tricks!

Troubleshooting
===============

Before updating the ``gmx`` package it is generally a good idea to remove the
previous installation and to start with a fresh build directory.

If you have not installed GROMACS already or if ``gmxapi_DIR`` does not contain directories like
``bin`` and ``share`` then you will get an error along the lines of the following.
::

   CMake Error at gmx/core/CMakeLists.txt:45 (find_package):
      Could not find a package configuration file provided by "gmxapi" with any
      of the following names:

        gmxapiConfig.cmake
        gmxapi-config.cmake

      Add the installation prefix of "gmxapi" to CMAKE_PREFIX_PATH or set
      "gmxapi_DIR" to a directory containing one of the above files.  If "gmxapi"
      provides a separate development package or SDK, be sure it has been
      installed.

If you are not a system administrator you are encouraged to install in a Python virtual environment,
created with virtualenv or Conda.
Otherwise, you will need to specify the ``--user`` flag to ``pip`` or ``-DGMXAPI_USER_INSTALL=ON`` to CMake to
install to your home directory.

Two of the easiest problems to run into are incompatible compilers and
incompatible Python. Try to make sure that you use the same C and C++
compilers for GROMACS, for the Python package, and for the sample
plugin. These compilers should also correspond to the ``mpicc`` compiler
wrapper used to compile ``mpi4py``. In order to build the Python
package, you will need the Python headers or development installation,
which might not already be installed on the machine you are using. (If
not, then you will get an error about missing ``Python.h`` at some
point.) If you have multiple Python installations (or modules available
on an HPC system), you could try one of the other Python installations,
or you or a system administrator could install an appropriate Python dev
package. Alternatively, you might try installing your own Anaconda or
MiniConda in your home directory.

If an attempted installation fails with CMake errors about missing
“gmxapi”, make sure that Gromacs is installed and can be found during
installation. For instance,

::

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install --verbose

Pip and related Python package management tools can be a little too
flexible and ambiguous sometimes. If things get really messed up, try
explicitly uninstalling the ``gmx`` module and its dependencies, then do
it again and repeat until ``pip`` can no longer find any version of any
of the packages.

::

    $ pip uninstall gmx
    $ pip uninstall cmake
    ...

Successfully running the test suite is not essential to having a working
``gmxapi`` package. We are working to make the testing more robust, but
right now the test suite is a bit delicate and may not work right, even
though you have a successfully built ``gmxapi`` package. If you want to
troubleshoot, though, the main problems seem to be that automatic
installation of required python packages may not work (requiring manual
installations, such as with ``pip install somepackage``) and ambiguities
between python versions. The testing attempts to run under both Python 2
and Python 3, so you may need to explicitly install packages for each
Python installation.
