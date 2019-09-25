===========
Quick start
===========

This document provides simple recipes for some specific installation scenarios.
Refer to :doc:`userguide/install` for complete documentation about prerequisites and
building from source code.

.. contents:: Quick start recipes
    :local:
    :depth: 2

Please report bugs or updates at https://redmine.gromacs.org/issues/2896

The following instructions assume the ``bash`` shell and

::

    SOURCE=$PWD/gromacs-gmxapi

Get the fork
^^^^^^^^^^^^

::

    git clone https://gerrit.gromacs.org/gromacs.git -b sandbox-gmxapi --single-branch $SOURCE

Build and install GROMACS
^^^^^^^^^^^^^^^^^^^^^^^^^

Refer to additional GROMACS instructions, but be sure to
enable the gmxapi library with the ``-DGMXAPI=ON`` argument.

::

    mkdir build
    cd build
    cmake .. -DGMXAPI=ON
    make -j10 install
    cd ..

After installing GROMACS, be sure to "source" the GMXRC. E.g. if you used
``-DCMAKE_INSTALL_PREFIX=/usr/local/gromacs`` as a CMake argument to configure
the install location, in a ``bash`` shell run ``source /usr/local/gromacs/bin/GMXRC``
before proceeding.

Build and install the gmxapi Python package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assuming ``python`` and ``pip`` are from a Python 3 installation::

    cd $SOURCE/python_packaging
    pip install -r src/requirements.txt
    (cd src && pip install .)

For more detailed instructions, refer to the ``README.md`` file in the ``python_packaging``
directory.

Refer to ``python_packaging/examples`` or run ``pydoc gmxapi`` for usage.

Build and install the sample_restraint package
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is the sample source tree for an MD restraint plug-in.

::

    cd sample_restraint
    mkdir build
    cd build
    cmake ..
    make -j10 install
    cd ..

Explore the example notebook
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Make sure a recent version of the jupyter notebook server is available::

    pip install --upgrade jupyter

::

    cd $SOURCE/python_packaging/sample_restraint/examples
    jupyter notebook

and look at ``example.ipynb``

