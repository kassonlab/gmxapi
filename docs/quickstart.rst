===========
Quick start
===========

This document provides simple recipes for some specific installation scenarios.
Refer to :doc:`install` for complete documentation about prerequisites and
building from source code.

.. contents:: Quick start recipes
    :local:
    :depth: 2

Please report bugs or updates at https://github.com/kassonlab/gmxapi/issues

.. _docker_container:

Docker
======

Check out our pre-built `Docker images <https://hub.docker.com/u/gmxapi/>`_
for a quick look at gmxapi or as a starting point for simulations in containers.

The Dockerfile recipes may also be useful references when building the software.

* `GROMACS base image <https://github.com/kassonlab/gromacs-gmxapi/blob/devel/docker/Dockerfile>`_
* `gmxapi Python package installation <https://github.com/kassonlab/gmxapi/blob/devel/docker/Dockerfile>`_
* `sample code and examples <https://github.com/kassonlab/sample_restraint/blob/devel/Dockerfile>`_

Docker images are based on the
`Jupyter Docker Stacks <https://jupyter-docker-stacks.readthedocs.io/en/latest/index.html>`_.

For a Jupyter notebook, launch ``docker run --rm -ti -p 8888:8888 gmxapi/sample_restraint``
and point your browser at the URL that is displayed.
Then navigate to `sample_restraint <http://localhost:8888/tree/sample_restraint>`_
-> `examples <http://localhost:8888/tree/sample_restraint/examples>`_

For a ``bash`` shell, just run ``docker run --rm -ti gmxapi/sample_restraint bash``

.. seealso:: https://github.com/kassonlab/sample_restraint/tree/devel#docker-quick-start

.. _singularity_container:

Singularity
===========

Thanks to `jmhays <https://github.com/jmhays>`_ for contributing `Singularity <http://singularity.lbl.gov>`_ recipes.
::

    singularity pull --name customname.img shub://jmhays/singularity-restrained-ensemble

See https://www.singularity-hub.org/collections/1825/usage for variants.

.. _user_install:

"User" installation
===================

In the simplest case, if dependencies are already installed and you have an
appropriate Python installation on your default PATH, something like the
following should just work. This will install the ``gmx`` Python package into
the default "user site-packages" directory for the Python installation you are
using so that you can just run Python normally and ``import gmx``.
::

    wget https://github.com/gromacs/gromacs/archive/release-2019.zip
    unzip release-2019.zip

    mkdir gromacs-build
    pushd gromacs-build
    cmake ../gromacs-release-2019 -DGMXAPI=ON -DCMAKE_INSTALL_PREFIX=$HOME/gromacs
    make install
    popd

    source $HOME/gromacs/bin/GMXRC

    wget https://github.com/kassonlab/gmxapi/archive/release-0_0_7.zip
    unzip release_0_0_7.zip

    mkdir gmxapi-build
    pushd gmxapi-build
    cmake ../gmxapi-release-0_0_7 -DGMXAPI_USER_INSTALL=ON
    make install
    popd

.. note::

    If your computer has more resources available, you can try to speed up the
    build by telling ``make`` to run in parallel. To use 8 threads, for instance,
    do ``make -j8 install``.

.. .._pyenv_install:

.. pyenv installation
    ==================

    *documentation coming soon...*

.. _conda_install:

Conda installation
==================

gmxapi does not provide a Conda binary package, but the following documentation
may work to prepare a Conda environment for gmxapi.

Get and install `Anaconda <https://docs.anaconda.com/anaconda/install/>`_.
Alternatively, on an HPC system
an Anaconda installation may already be provided with a ``module`` system. For example::

    module load gcc
    module load cmake
    module load anaconda3
    module load openmpi

You don't have to follow all of the instructions for setting up your login profile if you don't want to,
but if you don't, then the ``conda`` and ``activate`` commands below will have to be prefixed by your
conda installation location. E.g. ``~/miniconda3/bin/conda info`` or ``source ~/miniconda3/bin/activate myEnv``

Create a conda virtual environment. Replace ``myEnv`` below with whatever convenient name you choose.
::

    conda create -n myGmxapiEnv python=3 pip setuptools cmake networkx mpi4py

Activate, or enter the environment.
::

    source activate myGmxapiEnv

Install the GROMACS gmxapi fork.
::

    git clone https://github.com/kassonlab/gromacs-gmxapi.git gromacs
    mkdir build
    cd build
    cmake ../gromacs -DGMX_GPU=OFF -DGMX_THREAD_MPI=ON -DCMAKE_CXX_COMPILER=`which g++` -DCMAKE_C_COMPILER=`which gcc` -DCMAKE_INSTALL_PREFIX=$HOME/gromacs-gmxapi
    make -j12 && make install
    source $HOME/gromacs-gmxapi/bin/GMXRC

Make sure dependencies are up to date.
::

    MPICC=`which mpicc` pip install --upgrade mpi4py

Install the Python module.
::

    git clone https://github.com/kassonlab/gmxapi.git gmxapi
    cd gmxapi
    mkdir build
    cd build
    cmake ..
    make install

.. _ubuntu14:

Minimal Ubuntu system set up example
====================================

This section attempts to document installation in a constrained and minimal
environment, such as might be encountered in a container or testing system.

Before proceeding, consider whether an existing :ref:`docker_container` or
:ref:`singularity_container` recipe may be sufficient for you.

The following is tested for Ubuntu 14 using the ``ubuntu/trusty`` image from `Docker Hub <hub.docker.com>`

As root::

    apt-get update
    apt-get install software-properties-common
    apt-add-repository -y "ppa:ubuntu-toolchain-r/test"
    apt-get update

    apt-get -yq --no-install-suggests --no-install-recommends install \
        cmake \
        cmake-data \
        libblas-dev \
        libcr-dev \
        libfftw3-dev \
        liblapack-dev \
        libmpich-dev \
        libxml2-dev \
        make \
        mpich \
        zlib1g-dev

    # You probably want one or two more packages for convenience. For example:
    apt-get -yq --no-install-suggests --no-install-recommends install \
        git vim wget git

To manage Python installations, you could either use the native package manager,
or something like ``pyenv`` (see below). In Ubuntu 14, the following packages
should be sufficient.
::

    apt-get install python python-dev python3 python3-dev

For additional ideas, take a look at our :ref:`docker_container` recipes or our
:file:`.travis.yml` Travis-CI configuration.
