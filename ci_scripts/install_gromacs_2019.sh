#!/bin/bash
set -ev

export GMX_DOUBLE=OFF
export GMX_MPI=OFF
export GMX_THREAD_MPI=ON

export CCACHE_DIR=$HOME/.ccache_gmxapi
ccache -s

pushd $HOME
 [ -d gromacs-gmxapi ] || git clone --depth=1 --no-single-branch https://github.com/gromacs/gromacs.git gromacs
 pushd gromacs
  git branch -a
  git checkout release-2019
  pwd
  rm -rf build
  mkdir build
  pushd build
   cmake -DCMAKE_CXX_COMPILER=$CXX \
         -DCMAKE_C_COMPILER=$CC \
         -DGMX_DOUBLE=$GMX_DOUBLE \
         -DGMX_MPI=$GMX_MPI \
         -DGMX_THREAD_MPI=$GMX_THREAD_MPI \
         -DCMAKE_INSTALL_PREFIX=$HOME/install/gromacs_2019 \
         ..
   make -j2 install
  popd
 popd
popd
ccache -s
