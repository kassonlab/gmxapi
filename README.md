[![Build Status](https://travis-ci.org/gmxapi/gmxapi.svg?branch=dev_0_0_4)](https://travis-ci.org/gmxapi/gmxapi)

The gmxapi project provides interfaces for managing and extending molecular dynamics simulation workflows.
In this repository, a Python package provides the `gmx` module for high-level interaction with GROMACS.
`gmx.core` provides Python bindings to the `gmxapi` C++ GROMACS external API.

The project is hosted on [GitHub](https://github.com/gmxapi/gmxapi) and includes
the `gmxapi` repository along with supporting respositories.
the `gromacs-gmxapi` repository includes a modified version of GROMACS that
supports the latest `gmxapi` features not yet available through an official GROMACS distribution.

# Installation

A compatible version of GROMACS must either be already installed or may be installed
as part of package installation.
Alternatively, the Python module can be installed during a CMake-driven GROMACS installation.

You will need a few packages installed that are hard for gmxpy to install automatically.
Before proceeding, install / upgrade the Python package for `cmake`. Note that it is not
sufficient just to have the command-line CMake tools installed.

    python -m pip install --upgrade pip
    pip install --upgrade setuptools
    pip install --upgrade cmake
    
If you will be running the testing suite, you also need `virtualenv` and `tox`.

    pip install --upgrade tox

## Python setuptools with existing or shared GROMACS installation

Make sure that you have GROMACS installed with the gmxapi library.
See https://github.com/kassonlab/gromacs-gmxapi
and load the appropriate gmxrc or note the installation location
(`/Users/eric/gromacs` in the following example).

Download this repository and indicate to python where to look for a local GROMACS installation.
Either first source the GMXRC as described in GROMACS documentation or provide a hint on the command line.

    $ git clone https://github.com/gmxapi/gmxapi.git
    $ cd gmxapi

Then, if you have sourced your gmxrc or exported GROMACS environment variables, you can just

    $ python setup.py install

or

    $ pip install --upgrade .
    
Otherwise, you need to tell Python where to find GROMACS with an environment variable.
Note that in `bash`, there must not be spaces between the variable name and the equals sign (`=`).

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install

or

    $ gmxapi_DIR=/Users/eric/gromacs pip install --upgrade .

If you have not installed GROMACS already or if `gmxapi_DIR` does not contain directories like
`bin` and `share` then you will get an error along the lines of the following.

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
Otherwise, you will need to specify the `--user` flag to install to your home directory.

## Python setuptools (or pip) with private GROMACS installation

This installation option has been made available to allow automatic builds on readthedocs.org
but is not likely to be a supported use case unless a need is demonstrated. Download the repository.
Use the READTHEDOCS environment variable to tell setup.py to download and install a private copy of
GROMACS with the Python module.

# Python virtual environments

In the world of Python, a virtual environment is a Python installation that is self-contained
and easy to activate or deactivate to allow normal Python use without additional concerns of
software compatibility.

Several systems of managing virtual environments exist. gmxapi is tested with
Python 3's built-in virtualenv and the add-on virtualenv package for Python 2.

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

Note: we do not yet have a robust suggestion for setting up `tox` for running the test suite.
If you come up with a recipe, please let us know. Otherwise, don't worry if you are able to install
the package but can't get weird errors when you try to run the tests.

## virtualenv

Todo: step-by-step instructions for building and installing with native Python `virtualenv`

## virtualenvwrapper

Todo: step-by-step instructions for building and installing with helper package.

## Docker

Todo: Dockerfile and/or images for building, using, developing, or reading docs.

# Testing

Unit tests are performed individually with `pytest` or as a full installation and test
suite with `tox`.

From the root of the repository:

    $ gmxapi_DIR=/path/to/gromacs tox

For pytest, first install the package as above. Then,

    $ pytest --pyargs gmx -s --verbose

For a more thorough test that includes the parallel workflow features, make sure you have MPI set up and the `mpi4py` Python package.

    mpiexec -n 2 python -m mpi4py -m pytest --log-cli-level=DEBUG --pyargs gmx -s --verbose

Note: `tox` may get confused when it tries to create virtual environments when run from within
a virtual environment. If you get errors, try running the tests from the native Python environment
or a different virtual environment manager (i.e. not conda). And let us know
if you come up with any tips or tricks!

# Documentation

Documentation for the Python classes and functions in the gmx module can be accessed in the usual ways, using `pydoc`
from the command line or `help()` in an interactive Python session.

Additional documentation can be browsed on readthedocs.org or built with Sphinx after installation.

To build the user documentation locally, first make sure you have sphinx installed, such as by doing
a `pip install sphinx` or by using whatever package management system you are familiar with.
You may also need to install a `sphinx_rtd_theme` package.

Build *and install* the gmx module.

Then decide what directory you want to put the docs in and call `sphinx-build` to build `html` docs
from the configuration in the `docs` directory of the gmxpy repository.

Assuming you downloaded the repository to `/path/to/gmxapi` and you want to build the docs in `/path/to/docs`,
do

    sphinx-build -b html /path/to/gmxapi/docs /path/to/docs
    
or

    python -m sphinx -b html /path/to/gmxapi/docs /path/to/docs

Then open `/path/to/docs/index.html` in a browser.

Note:

If you try to run `sphinx-build` from the root directory of the repository, it will get confused
and not realize that it should use the package you just installed instead of the unbuilt source code.
Therefore, I recommend the following complete procedure to download, install, and build docs for the
`gmxapi` package:

    $ python -m pip install --upgrade pip
    $ pip install --upgrade setuptools
    $ pip install --upgrade cmake
    $ pip install --upgrade sphinx
    $ pip install --upgrade sphinx_rtd_theme
    $ git clone https://github.com/gmxapi/gmxapi.git
    $ cd gmxapi
    $ gmxapi_DIR=/path/to/gromacs pip install .
    $ cd docs
    $ python -m sphinx -b html . ../html
    $ cd ..
    $ open html/index.html

Note that the periods '.' and '..' in the above commands are important and that there
are no spaces before or after the equals sign ('=') when specifying the GROMACS path.

# Troubleshooting

If an attempted installation fails with CMake errors about missing "gmxapi", make
sure that Gromacs is installed and can be found during installation. For instance,

    $ gmxapi_DIR=/Users/eric/gromacs python setup.py install --verbose
        
Pip and related Python package management tools can be a little too flexible and ambiguous
sometimes.
If things get really messed up, try explicitly uninstalling the `gmx` module and its dependencies,
then do it again and repeat until `pip` can no longer find any version of any of the packages.

    $ pip uninstall gmx
    $ pip uninstall cmake
    ...

Successfully running the test suite is not essential to having a working `gmxapi` package.
We are working to make the testing more robust, but right now the test suite is a bit delicate
and may not work right, even though you have a successfully built `gmxapi` package. If you
want to troubleshoot, though, the main problems seem to be that automatic installation of
required python packages may not work (requiring manual installations, such as with `pip install somepackage`)
and ambiguities between python versions. The testing attempts to run under both Python 2 and
Python 3, so you may need to explicitly install packages for each Python installation.
