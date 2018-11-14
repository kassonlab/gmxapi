#!/usr/bin/env bash
#
# Install the `gmx` Python package against a gmxapi-compatible
# GROMACS installation using various methods to test support of tools.
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
# Test install with pip
#
$PYTHON -m pip uninstall -y gmx
# Clean up some of the dirty built-in-source directories that could cause
# inappropriate caching.
rm -rf _skbuild dist gmx* build
$PYTHON -m pip install .

$PYTHON -m pytest src/gmx/test

#
# Test install with setup.py
#
$PYTHON -m pip uninstall -y gmx
rm -rf _skbuild dist gmx* build
$PYTHON setup.py install

$PYTHON -m pytest src/gmx/test

#
# Test CMake-driven install
#
# Inactive. Duplicate of pygmx.sh
#pip uninstall -y gmx
#rm -rf _skbuild dist gmx* build
#
#rm -rf build
#mkdir -p build
#pushd build
# cmake .. -DCMAKE_CXX_COMPILER=$CXX -DCMAKE_C_COMPILER=$CC -DPYTHON_EXECUTABLE=$PYTHON
# make -j2
#popd
