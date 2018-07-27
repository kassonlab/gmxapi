#!/bin/bash
set -ev

# Test install with pip
$PYTHON -m pip uninstall -y gmx
rm -rf _skbuild dist gmx* build
$PYTHON -m pip install .

$PYTHON -m pytest src/gmx/test

# Test install with setup.py
$PYTHON -m pip uninstall -y gmx
rm -rf _skbuild dist gmx* build
$PYTHON setup.py install

$PYTHON -m pytest src/gmx/test

# Test CMake-driven install
pip uninstall -y gmx

rm -rf build
mkdir -p build
pushd build
 cmake .. -DCMAKE_CXX_COMPILER=$CXX -DCMAKE_C_COMPILER=$CC -DPYTHON_EXECUTABLE=$PYTHON
 make -j2 install
 make -j2 docs
popd

mpiexec -n 2 $PYTHON -m mpi4py -m pytest src/gmx/test

$PYTHON -m pip freeze
ccache -s
