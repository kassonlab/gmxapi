#!/bin/bash
set -ev

export GMX_DOUBLE=OFF
export GMX_MPI=OFF
export GMX_THREAD_MPI=ON

CCACHE=`which ccache`
if [ "${CCACHE}" ] ; then
    export CCACHE_DIR=$HOME/.ccache_gmxapi
    ccache -s
    export ENABLE_CCACHE=ON
else
    export ENABLE_CCACHE=OFF
fi

pushd $HOME
 [ -d gromacs-gmxapi ] || \
     git clone \
         --depth=1 \
         --no-single-branch \
         https://github.com/kassonlab/gromacs-gmxapi.git \
         gromacs-kassonlab
 pushd gromacs-kassonlab
  git branch -a
  git checkout devel
  pwd
  rm -rf build
  mkdir build
  pushd build
   cmake -DGMX_BUILD_HELP=OFF \
         -DGMX_ENABLE_CCACHE=$ENABLE_CCACHE \
         -DCMAKE_CXX_COMPILER=$CXX \
         -DCMAKE_C_COMPILER=$CC \
         -DGMX_DOUBLE=$GMX_DOUBLE \
         -DGMX_MPI=$GMX_MPI \
         -DGMX_THREAD_MPI=$GMX_THREAD_MPI \
         -DGMXAPI=ON \
         -DCMAKE_INSTALL_PREFIX=$HOME/install/gromacs_devel \
         ..
   make -j2 install
  popd
 popd
popd
[ "$ENABLE_CCACHE" ] && ccache -s
