gmxpy

A Python package providing the `gmx` module for interfacing with GROMACS.

A compatible version of GROMACS must either be already installed or may be installed
as part of package installation.

# Installation Options

## Python setuptools with existing or shared GROMACS installation

Download the gmxpy repository and indicate to python where to look for a local GROMACS installation.
Either first source the GMXRC as described in GROMACS documentation or provide a hint on the command line.

    $ gmxapi_DIR=/Users/eric/gromacs pip install .

## Python setuptools (or pip) with private GROMACS installation

Download the gmxpy repository. Use the command-line flag to tell setup.py to download and install a private copy of
GROMACS with the Python module.

## During or from GROMACS installation

Get a copy of GROMACS and enable simultaneous installation of the Python module.

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
Additional documentation can be build with Sphinx or browsed on readthedocs.org.

# Troubleshooting

If an attempted installation fails with CMake errors about missing "gmxapi", make
sure that Gromacs is installed and can be found during installation. For instance,

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install --verbose