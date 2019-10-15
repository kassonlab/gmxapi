#!/bin/bash
#
# Build, install, and test the MD plugin code from the kassonlab/sample_restraint
# repository on GitHub.
#
# Requirements:
#
# The script assumes the following environment has been set.
# - PYTHON holds the full path to the Python interpreter for a (virtual) environment
#   in which pip, pytest, and the various dependency modules are installed.
# - the `gmxapi` Python package has been installed before tests are run.
# - GMXRC for a thread-MPI GROMACS installation has been sourced.
# - mpiexec is available on the PATH and able to launch a 2-rank environment.
#

#Be verbose and exit quickly.
set -ev

pushd python_packaging/sample_restraint
  rm -rf build
  mkdir build
  pushd build
   cmake .. -DPYTHON_EXECUTABLE=$PYTHON \
            -DDOWNLOAD_GOOGLETEST=ON \
            -DGMXAPI_EXTENSION_DOWNLOAD_PYBIND=ON
   make -j2 install
   # Run C++ unit tests.
   make -j2 test
  popd
  pushd tests
   # Run basic integration tests
   $PYTHON -m pytest
   # Run integration tests for full parallelism, such as ensemble operations.
   mpiexec -n 2 $PYTHON -m mpi4py -m pytest # --log-cli-level=DEBUG -s --verbose
  popd
popd
