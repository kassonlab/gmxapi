==============================
Full installation instructions
==============================

.. highlight:: bash

This document provides more thorough documentation about building and installing
the gmxapi Python package.

GROMACS is a high performance computational science tool that is optimized for
a variety of specialized hardware and parallel computing environments.
To make the best use of a computing environment, GROMACS is usually built from
source code.

Users of Python based molecular science tools may have various requirements and
use a variety of Python distributions,
so gmxapi extension code is most useful when built from source code for a specific
GROMACS installation and Python environment.

Read this document if the :doc:`quickstart` instructions are not sufficient for you.
If you don't need a lot of reference material, you may just jump ahead to the :ref:`installation`.

Command line examples assume the `bash <https://www.gnu.org/software/bash/>`_ shell.

.. note:: Regarding multiple GROMACS installations:
    Many GROMACS users switch between multiple GROMACS installations on the same
    computer using an HPC module system and/or a GMXRC configuration script.
    For the equivalent sort of environment switching with the ``gmx`` Python package,
    we recommend installing ``gmx`` in a different
    `Python virtual environment <https://www.google.com/search?q=python+virtual+environment>`_
    for each GROMACS installation.
    Once built, a particular copy of the ``gmx`` Python package always refers to the
    same GROMACS installation.

.. contents:: Contents
    :local:
    :depth: 2

.. note::

    The following documentation contains frequent references to the ``pip`` tool
    for installing Python packages. In some cases, an unprivileged user should
    use the ``--user`` command line flag to tell ``pip`` to install packages
    into the user site-packages directory rather than the default site-packages
    directory for the Python installation. This flag is not appropriate when
    running ``pip`` in a virtual environment (as recommended) and is omitted in
    this documentation. If you need the ``--user`` flag, you should modify the
    example commands to look something like ``pip install --upgrade somepackage --user``

Requirements
============

``gmxapi`` comes in three parts:

* GROMACS gmxapi library for C++
* This Python package
* MD restraint plugins and sample gmxapi client code

First, install `GROMACS 2019 <http://www.gromacs.org>`_ (beta 2 or more recent)
or the Kasson Lab GROMACS fork available from
`github.com/kassonlab/gromacs-gmxapi <https://github.com/kassonlab/gromacs-gmxapi/>`_

Then, install this Python package as documented below. E.g.
`github.com/kassonlab/gmxapi <https://github.com/kassonlab/gmxapi/>`_.

A `sample plugin <https://github.com/kassonlab/sample_restraint>`_ demonstrates
how to extend GROMACS with C++ code that can be controlled from the Python interface.

Build system requirements
-------------------------

The preferred installation method is via `CMake <https://cmake.org/>`_.

You will need a C++ 11 compatible compiler and a reasonably up-to-date version
of CMake.
Full gmxapi functionality may also require an MPI compiler (e.g. ``mpicc``).

The Python package requires a GROMACS installation.
Build and install `GROMACS 2019 <http://www.gromacs.org>`_ (beta 2 or more recent)
or the Kasson Lab GROMACS fork (available from
`github.com/kassonlab/gromacs-gmxapi <https://github.com/kassonlab/gromacs-gmxapi/>`_)
before proceeding.
Then, "source" the GMXRC file from the GROMACS installation as you normally would
before using GROMACS, or note its installation location so that you can pass it
to the build configuration.

Important: To build a module that can be imported by Python, you need a Python
installation that includes the Python headers. Unfortunately, it is not always
obvious whether these headers are present or where to find them. The simplest
answer is to just try to build the Python package using these instructions, and
if gmxapi is unable to find the Python tools it needs, try a different Python
installation or install the additional development packages.

On a Linux system, this may require installing packages such as ``python-dev``
and/or ``python3-dev``. Alternatively, various Python distributions provide a
sufficient build environment while only requiring installation into a user
home directory. (Some examples below.)

If you are using an HPC system with software available through modules you may
be able to just ``module load`` a different Python installation and find one
that works.

.. seealso::

    See :ref:`ubuntu14` for an example of a minimal system set up for Ubuntu 14.
    Also, the recipes in our CI testing scripts and our Dockerfiles may be informative.

Python environment requirements
-------------------------------

At a minimum, the gmxapi Python package requires the ``networkx`` Python package
to run. To build and install, you also need the packages ``cmake``,
``setuptools``, and ``scikit-build``.

For full functionality, you should also have ``mpi4py`` and ``numpy``.

The easiest way to make sure you have the requirements installed, first update
``pip``, then use the ``requirements.txt`` file provided with the repository.
::

    python -m pip install --upgrade pip
    pip install --upgrade setuptools
    pip install -r requirements.txt

The above assumes you

.. _build_docs:

Documentation build requirements
--------------------------------

Documentation is built with `Sphinx <http://www.sphinx-doc.org/>`_
from a combination of static content in ``rst``
files and from embedded documentation in the Python package. To build documentation
locally, you will need a reasonably current copy of Sphinx and the RTD theme.
::

    pip install --upgrade Sphinx sphinx-rtd-theme

.. seealso:: :ref:`documentation`

.. _testing_requirements:

Testing requirements
--------------------

Testing is performed with `pytest <https://docs.pytest.org/en/latest/>`_.
Tests also require ``numpy``.
You can probably install both with ``pip``::

    pip install pytest numpy

Full functionality requires MPI to test. You will need the ``mpi4py`` Python
package and an MPI launcher
(such as ``mpiexec``, ``mpirun``, or something provided by your HPC queuing system).

.. seealso:: :ref:`testing`

.. _mpi_requirements:

MPI requirements
----------------

For the ensemble simulations features, you will need an MPI installation. On an HPC system, this means you will
probably have to use ``module load`` to load a compatible set of MPI tools and compilers. Check your HPC
documentation or try ``module avail`` to look for an ``openmpi``, ``mpich``, or ``mvapich`` module and matching compiler
module. This may be as simple as
::

    module load gcc
    module load mpicc

Note that the compilers loaded might not be the first compilers discovered automatically by the build tools we will use
below, so you may have to specify compilers on the command line for consistency. It may be necessary to require that
GROMACS, gmxapi, and the sample code are built with the same compiler(s).

Note that strange errors have been known to occur when ``mpi4py`` is built with
different a different tool set than has been used to build Python and gmxapi.
If the default compilers on your system are not sufficient for GROMACS or gmxapi,
you may need to build, e.g., OpenMPI or MPICH, and/or build ``mpi4py`` with a
specific MPI compiler wrapper. This can complicate building in environments such
as Conda.

Set the MPICC environment variable to the MPI compiler wrapper and forcibly
reinstall ``mpi4py``.
::

    export MPICC=`which mpicc`
    pip install --no-cache-dir --upgrade --no-binary \":all:\" --force-reinstall mpi4py

Installing the Python package
=============================

We recommend you install the gmxapi package in a Python virtual environment
(``virtualenv`` or ``venv``). There are several ways to do this, and it is also
possible to install without a virtual environment. If installing without a
virtual environment as an un-privileged user, you may need to set the CMake
variable ``GMXAPI_USER_INSTALL`` (``-DGMXAPI_USER_INSTALL=ON`` on the ``cmake``
command line) and / or use the ``--user`` option with ``pip install``.

Sometimes the build environment can choose a different Python interpreter than
the one you intended.
You can set the ``PYTHON_EXECUTABLE`` CMake variable to explicitly choose the
Python interpreter for your chosen installation.
For example: ``-DPYTHON_EXECUTABLE=\`which python\```

.. _installation:

Recommended installation
------------------------

Locate or install GROMACS
^^^^^^^^^^^^^^^^^^^^^^^^^

If GROMACS 2019 or higher is already installed, source the GMXRC and skip to the
next section.

Otherwise, install a supported version of GROMACS. For instance, clone one of
the two following ``git`` repositories.

Official GROMACS release branch::

    git clone https://github.com/gromacs/gromacs.git gromacs
    cd gromacs
    git checkout release-2019

The Kasson Lab GROMACS fork may have experimental features that have not yet
appeared in an official GROMACS release.
::

    git clone https://github.com/kassonlab/gromacs-gmxapi.git gromacs
    cd gromacs
    # for that absolute latest code, check out the "development branch" (optional)
    git checkout devel

Configure and build GROMACS. Install into a ``gromacs-gmxapi`` directory in your
home directory.
::

    mkdir build
    cd build
    cmake ../gromacs -DGMX_THREAD_MPI=ON \
                     -DCMAKE_CXX_COMPILER=`which g++`
                     -DCMAKE_C_COMPILER=`which gcc`
                     -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-gmxapi
    make -j8 && make install

.. note::

    ``make -j8`` uses up to ``8`` CPU threads to try to build in parallel
    (using more CPU *and memory*).
    Adjust according to your computing resources.

Set the environment variables for the GROMACS installation.
::

    source $HOME/gromacs-gmxapi/bin/GMXRC

Set up a Python virtual environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We recommend installing the Python package in a virtual environment.
If not installing in a virtual environment, you may not be able to install
necessary prerequisites (e.g. if you are not an administrator of the system you are on).

Create a Python virtual environment.
If using Python 2, use the ``virtualenv`` module. If it is initially not found, install it with
``python -m pip install virtualenv --user``. Then,
::

    python -m virtualenv $HOME/myvenv

For Python 3, use the ``venv`` module.
Depending on your computing environment, the Python 3 interpreter may be accessed
with the command ``python`` or ``python3``. Use ``python --version`` and
``python3 --version`` to figure out which you need to use. The following assumes
the Python 3 interpreter is accessed with ``python3``.

::

    python -m venv $HOME/myvenv

.. note::

    The Python 3 executable may be named ``python3`` instead of ``python``.
    E.g. run ``python3 -m venv $HOME/myvenv``

Activate the virtual environment. Your shell prompt will probably be updated with the name of the environment you
created to make it more obvious.

.. code-block:: none

    $ source $HOME/myvenv/bin/activate
    (myvenv)$

Activating the virtual environment changes your shell prompt to indicate the
environment is active. The prompt is omitted from the remainging examples, but
the remaining examples assume the virtualenv is still active.
(Don't do it now, but you can deactivate the environment by running ``deactivate``.)

Install some dependencies. For MPI, we use mpi4py. Make sure it is using the same MPI installation that we are building
GROMACS against and building with compatible compilers.
::

    python -m pip install --upgrade pip setuptools
    MPICC=`which mpicc` pip install --upgrade mpi4py

Build and install
^^^^^^^^^^^^^^^^^

Get a copy of `the source code <https://github.com/kassonlab/gmxapi/releases/latest>`_,
if you haven't already.
For a specific `release version <https://github.com/kassonlab/gmxapi/releases>`_,
you can just download a source package.
::

    wget https://github.com/kassonlab/gmxapi/archive/v0.0.7.zip
    unzip v0_0_7.zip
    cd gmxapi-v0_0_7

For a development branch, you should probably clone the repository. You may not already have ``git`` installed on your
system or you may need to load a module for it on an HPC system, which you will need to do before trying the following.
::

    git clone https://github.com/kassonlab/gmxapi.git
    cd gmxapi
    git checkout devel

You will need to install some additional dependencies. The :file:`requirements.txt`
file is provided for convenience. Also, note that ``pip`` must be
version 10.1 or higher.
::

    pip install -r requirements.txt

Create a ``build`` directory.
::

    mkdir build
    cd build

Use ``cmake`` to configure and ``make`` to build and install.
::

    cmake ..
    make install

Take note whether the correct python executable is found. You may need to specify
``-DPYTHON_EXECUTABLE=/path/to/python`` to cmake. E.g. ``cmake .. -DPYTHON_EXECUTABLE=\`which python\```

Get out of the build directory::

    cd ..

Alternatives
------------

* :ref:`user_install`
* :ref:`conda_install`
* :ref:`docker_container`
* :ref:`singularity_container`

CMake options
-------------

Several relevant CMake options can be specified on the command line with ``-D``.
Also consider using the ``ccmake`` interactive cmake command to browse available
options.

``GMXAPI_USER_INSTALL`` tells the installer not to use the default Python package
installation directory for the Python installation, but the user site-packages
directory. If installing as an unprivileged user outside of a virtual environment,
set ``-DGMXAPI_USER_INSTALL=ON`` in the ``cmake`` command line. Otherwise, it is
important that you leave it as the default (``OFF``). Many users have multiple
Python installations (whether they know it or not), and each has its own
``site-packages`` directory. However, often all of the Python installations will
use *the same* **user** packages directory. This can get very confusing when
packages are incompatible between Python installations.

``GMXAPI_INSTALL_PATH`` overrides the automatically detected Python package
installation path. If you configure cmake with ``-DGMXAPI_INSTALL_PATH=/some/path``
then ``/some/path`` should be included in your
`module search path <https://docs.python.org/3/tutorial/modules.html#the-module-search-path>`_
before trying to import the ``gmx`` Python module.

``gmxapi_DIR`` can be provided as an environment variable or as a CMake variable
and should reference the gmxapi-capable GROMACS installation. If unset,
``GROMACS_DIR`` is also checked. It is generally sufficient to source the GMXRC
for your GROMACS installation before running ``cmake``.

``PYTHON_EXECUTABLE`` can be provided to CMake as a hint to make sure you are
building and installing for the intended Python interpreter. This is especially
important if you have both Python 2 and Python 3 installed.

.. _documentation:

Documentation
=============

Documentation for the Python classes and functions in the gmx module can
be accessed in the usual ways, using ``pydoc`` from the command line or
``help()`` in an interactive Python session.

Additional documentation can be browsed on
`readthedocs.org <http://gmxapi.readthedocs.io/en/readthedocs/>`__ or
built with Sphinx after installation.

.. seealso:: :ref:`build_docs`

Install the ``gmx`` module so that its built-in documentation can be extracted
for the API reference. Then build all of the documentation with Sphinx using
the ``docs`` build target.

Assuming you are in the build directory::

    make install
    make docs

Then open :file:`docs/index.html`

.. note:: The ``docs`` build target puts the built documentation in your build directory.

Custom docs install
-------------------

If you have already installed the package, you can build the docs to any destination folder you want from the repository
directory.
Decide what directory you want to put the docs in and call
``sphinx-build`` to build ``html`` docs from the configuration in the
``docs`` directory of the gmxpy repository.

Assuming you downloaded the repository to ``/path/to/gmxapi`` and you
want to build the docs in ``/path/to/docs``, do
::

    sphinx-build -b html /path/to/gmxapi/docs /path/to/docs

or, if the sphinx-build tool is not installed,
::

    python -m sphinx -b html /path/to/gmxapi/docs /path/to/docs

Then open ``/path/to/docs/index.html`` in a browser.

.. _testing:

Testing
=======

Unit tests are performed individually with ``pytest``.
You will also need ``numpy``.

Install the gmx package first. Then run the tests either from the source code
repository or from the installed package.

.. code-block:: bash

    # From the root of the source code repository
    pytest src/gmx/test/
    # or
    python -m pytest src/gmx/test/
    # or, for more output
    pytest src/gmx/test -s --verbose

or,

.. code-block:: bash

    # From somewhere other than a build directory
    pytest --pyargs gmx

For a more thorough test that includes the parallel workflow features,
make sure you have MPI set up and the ``mpi4py`` Python package.
::

    mpiexec -n 2 python -m mpi4py -m pytest --log-cli-level=DEBUG --pyargs gmx -s --verbose

..  ``tox`` may get confused when it tries to create virtual
    environments when run from within a virtual environment. If you get
    errors, try running the tests from the native Python environment or a
    different virtual environment manager (i.e. not conda). And let us know
    if you come up with any tips or tricks!

.. seealso:: :ref:`testing_requirements`

Troubleshooting
===============

Couldn't find ``gmxapi``? If you don't want to "source" your ``GMXRC`` file, you
can tell ``cmake`` where to find a gmxapi compatible GROMACS installation with
``gmxapi_DIR``. E.g. ``gmxapi_DIR=/path/to/gromacs cmake``...

Before updating the ``gmx`` package it is generally a good idea to remove the
previous installation and to start with a fresh build directory. You should be
able to just ``pip uninstall gmx``.

Do you see something like the following?

.. code-block:: none

   CMake Error at gmx/core/CMakeLists.txt:45 (find_package):
      Could not find a package configuration file provided by "gmxapi" with any
      of the following names:

        gmxapiConfig.cmake
        gmxapi-config.cmake

      Add the installation prefix of "gmxapi" to CMAKE_PREFIX_PATH or set
      "gmxapi_DIR" to a directory containing one of the above files.  If "gmxapi"
      provides a separate development package or SDK, be sure it has been
      installed.

This could be because

* GROMACS is not already installed
* GROMACS was built without the CMake variable ``GMXAPI=ON``
* or if ``gmxapi_DIR`` (or ``GROMACS_DIR``) is not a path containing directories
  like ``bin`` and ``share``.

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

    gmxapi_DIR=/Users/eric/gromacs python setup.py install --verbose

Pip and related Python package management tools can be a little too
flexible and ambiguous sometimes. If things get really messed up, try
explicitly uninstalling the ``gmx`` module and its dependencies, then do
it again and repeat until ``pip`` can no longer find any version of any
of the packages.

::

    pip uninstall gmx
    pip uninstall cmake
    # ...

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

If you are working in the ``devel`` branch of the repository, note that
the upstream branch may be reset to ``master`` after a new release is
tagged. In general, but particularly on the ``devel`` branch, when you
do a ``git pull``, you should use the ``--rebase`` flag.

If you fetch this repository and then see a git status like this::

    $ git status
    On branch devel
    Your branch and 'origin/devel' have diverged,
    and have 31 and 29 different commits each, respectively.

then ``gmxapi`` has probably entered a new development cycle. You can
do ``git pull --rebase`` to update to the latest development branch.

If you do a ``git pull`` while in ``devel`` and get a bunch of unexpected
merge conflicts, do ``git merge --abort; git pull --rebase`` and you should
be back on track.

If you are developing code for gmxapi, this should be an indication to
rebase your feature branches for the new development cycle.
