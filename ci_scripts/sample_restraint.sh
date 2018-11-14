#!/bin/bash
#
# Build, install, and test the MD plugin code from the kassonlab/sample_restraint
# repository on GitHub.
#
# This script uses an argument (${1}) to specify the branch to check out and build.
#
# Requirements:
#
# The script assumes the following environment has been set.
# - PYTHON holds the full path to the Python interpreter for a (virtual) environment
#   in which pip, pytest, and the various dependency modules are installed.
# - the `gmx` Python package has been installed before tests are run.
# - GMXRC for a thread-MPI GROMACS installation has been sourced.
# - mpiexec is available on the PATH and able to launch a 2-rank environment.
#

#Be verbose and exit quickly.
set -ev

pushd $HOME
 [ -d sample_restraint ] || git clone --depth=1 --no-single-branch https://github.com/kassonlab/sample_restraint.git
 pushd sample_restraint
  git checkout $1
  rm -rf build
  mkdir build
  pushd build
   cmake .. -DPYTHON_EXECUTABLE=$PYTHON
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
popd
