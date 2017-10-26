gmxpy is
a Python package providing the `gmx` module for interfacing with GROMACS.

The project is hosted on [BitBucket](https://bitbucket.org/kassonlab/gmxpy).
Documentation for released versions can be viewed on readthedocs or can be built locally.

A compatible version of GROMACS must either be already installed or may be installed
as part of package installation.
Alternatively, the Python module can be installed during a CMake-driven GROMACS installation.

# Installation Options

## Python setuptools with existing or shared GROMACS installation

Make sure that you have GROMACS installed with the gmxapi library.
See https://bitbucket.org/kassonlab/gromacs
and load the appropriate gmxrc or note the installation location
(`/Users/eric/gromacs` in the following example).

Download the gmxpy repository and indicate to python where to look for a local GROMACS installation.
Either first source the GMXRC as described in GROMACS documentation or provide a hint on the command line.

    $ git clone git clone https://bitbucket.org:kassonlab/gmxpy.git
    $ cd gmxpy

Then,

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install

or

    $ gmxapi_DIR=/Users/eric/gromacs pip install .

If you are not a system administrator you are encouraged to install in a virtual environment,
such as is created with Anaconda or virtualenv.
Otherwise, you will need to specify the `--user` flag to install to your home directory.

## During or from GROMACS installation

Instead of building directly from the gmxpy repository,
get a copy of GROMACS and enable simultaneous installation of the Python module
via CMake, using the instructions at the
[gmxapi repository](https://bitbucket.org/kassonlab/gromacs).

## Python setuptools (or pip) with private GROMACS installation

This installation option has been made available to allow automatic builds on readthedocs.org
but is not likely to be a supported use case unless a need is demonstrated. Download the gmxpy repository.
Use the READTHEDOCS environment variable to tell setup.py to download and install a private copy of
GROMACS with the Python module.

# Python virtual environments

In the world of Python, a virtual environment is a Python installation that is self-contained
and easy to activate or deactivate to allow normal Python use without additional concerns of
software compatibility.

Several systems of managing virtual environments exist. Pygmx is tested with Anaconda and with
Python 3's built-in virtualenv.

The following documentation assumes you have installed a compatible version of GROMACS and
installed it in the directory `/path/to/gromacs`. Replace `/path/to/gromacs` with the actual
install location below.

## Anaconda

Get and install Anaconda https://docs.anaconda.com/anaconda/install/

You don't have to follow all of the instructions for setting up your login profile if you don't want to,
but if you don't, then the `conda` and `activate` commands below will have to be prefixed by your
conda installation location. E.g. `~/miniconda3/bin/conda info` or `source ~/miniconda3/bin/activate myEnv`

Create a conda virtual environment. Replace `myEnv` below with whatever convenient name you choose.

    conda create -n myEnv python=3

Activate, or enter the environment.

    source activate myEnv

Install the Python module. At some point, this will be simplified, but for right now please use the instructions above.

## virtualenv

## virtualenvwrapper

## Docker

# Testing

Unit tests are performed individually with `pytest` or as a full installation and test
suite with `tox`. Tests can be invoked from the root of the repository in the standard way.

    $ python setup.py test

Note: `tox` may get confused when it tries to create virtual environments when run from within
a virtual environment. If you get errors, try running the tests from the native Python environment
or a different virtual environment manager (i.e. conda versus virtualenvwrapper). And let us know
if you come up with any tips or tricks!

# Documentation

Documentation for the Python classes and functions in the gmx module can be accessed in the usual ways, using `pydoc`
from the command line or `help()` in an interactive Python session.

Additional documentation can be browsed on readthedocs.org or built with Sphinx after installation.

# Troubleshooting

If an attempted installation fails with CMake errors about missing "gmxapi", make
sure that Gromacs is installed and can be found during installation. For instance,

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install --verbose