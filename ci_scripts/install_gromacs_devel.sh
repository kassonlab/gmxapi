#!/bin/bash
set -ev

export GMX_DOUBLE=OFF
export GMX_MPI=OFF
export GMX_THREAD_MPI=ON

pushd $HOME
 [ -d gromacs-gmxapi ] || git clone --depth=1 --no-single-branch https://github.com/eirrgang/gromacs-gmxapi.git gromacs-kassonlab
 pushd gromacs-kassonlab
  git branch -a
# TODO: change back to devel after gromacs-gmxapi fork is updated.
  git checkout port_master
  pwd
  rm -rf build
  mkdir build
  pushd build
   cmake -DGMX_BUILD_HELP=OFF \
         -DCMAKE_CXX_COMPILER=$CXX \
         -DCMAKE_C_COMPILER=$CC \
         -DGMX_DOUBLE=$GMX_DOUBLE \
         -DGMX_MPI=$GMX_MPI \
         -DGMX_THREAD_MPI=$GMX_THREAD_MPI \
         -DCMAKE_INSTALL_PREFIX=$HOME/install/gromacs_devel \
         ..
   make -j2 install
  popd
 popd
popd
ccache -s
