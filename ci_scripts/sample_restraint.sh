#!/bin/bash
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
   make -j2 test
  popd
  pushd tests
   $PYTHON -m pytest
   mpiexec -n 2 $PYTHON -m mpi4py -m pytest --log-cli-level=DEBUG -s --verbose
  popd
 popd
popd
