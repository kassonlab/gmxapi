#!/usr/bin/env bash
# Install a newer CMake to meet GROMACS minimum cmake version requirement on
# Travis-CI Ubuntu 14 container.
# Reference https://riptutorial.com/cmake/example/4723/configure-travis-ci-with-newest-cmake

set -ev

mkdir -p ${HOME}/install
rm -rf ${CMAKE_ROOT}

# we use wget to fetch the cmake binaries
wget -c --no-check-certificate https://github.com/Kitware/CMake/releases/download/v3.13.3/cmake-3.13.3-Linux-x86_64.tar.gz
# this is optional, but useful:
# do a quick checksum to ensure that the archive we downloaded did not get compromised
echo "78227de38d574d4d19093399fd4b40a4fb0a76cbfc4249783a969652ce515270  cmake-3.13.3-Linux-x86_64.tar.gz" > cmake_sha.txt
sha256sum -c cmake_sha.txt
# extract the binaries; the output here is quite lengthy,
# so we swallow it to not clutter up the travis console
tar -xvf cmake-3.13.3-Linux-x86_64.tar.gz > /dev/null
mv cmake-3.13.3-Linux-x86_64 ${CMAKE_ROOT}
