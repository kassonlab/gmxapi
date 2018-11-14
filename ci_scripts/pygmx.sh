#!/bin/bash
#
# Build, install, and test the `gmx` Python package against a gmxapi-compatible
# GROMACS installation.
#
# Requirements:
#
# The script assumes the following environment has been set.
# - PYTHON holds the full path to the Python interpreter for a (virtual) environment
#   in which pip, pytest, and the various dependency modules are installed.
# - CC holds the compiler that is also associated with the `mpicc` used to build
#   the mpi4py Python package.
# - CXX holds the C++ compiler used to build GROMACS.
# - GMXRC for a thread-MPI GROMACS installation has been sourced.
#
set -ev

#
# Test CMake-driven install
#
pip uninstall -y gmx
rm -rf _skbuild dist gmx* build

rm -rf build
mkdir -p build
pushd build
 cmake .. -DCMAKE_CXX_COMPILER=$CXX -DCMAKE_C_COMPILER=$CC -DPYTHON_EXECUTABLE=$PYTHON
 make -j2 install
 make -j2 docs
popd

mpiexec -n 2 $PYTHON -m mpi4py -m pytest src/gmx/test

# Check how well our compiler cache is working.
`which ccache` && ccache -s

# Generate the list of Python packages present in the current environment.
# Helpful, but not necessarily sufficient, for reproducibility.
$PYTHON -m pip freeze
