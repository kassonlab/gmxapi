#!/bin/bash
set -ev

rm -rf build
mkdir -p build
pushd build
 cmake .. -DCMAKE_CXX_COMPILER=$CXX -DCMAKE_C_COMPILER=$CC -DPYTHON_EXECUTABLE=$PYTHON
 make -j2 install
 make -j2 docs
popd
mpiexec -n 2 $PYTHON -m mpi4py -m pytest --log-cli-level=DEBUG --pyargs gmx -s --verbose
ccache -s
