# Update an ubuntu image with dependencies needed to build GROMACS and dependent packages.
# This version of the Dockerfile installs mpich.

# docker build -t gmxapi/gromacs-dependencies-mpich -f gromacs-dependencies.dockerfile .

# This image serves as a base for integration with the gmxapi Python tools and sample code.

FROM ubuntu:bionic

# Basic packages
RUN apt-get update && \
    apt-get -yq --no-install-suggests --no-install-recommends install software-properties-common && \
    apt-get -yq --no-install-suggests --no-install-recommends install \
        git \
        libblas-dev \
        libcr-dev \
        libfftw3-dev \
        liblapack-dev \
        libxml2-dev \
        make \
        vim \
        wget \
        zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# mpich installation layer
RUN apt-get update && \
    apt-get -yq --no-install-suggests --no-install-recommends install \
        libmpich-dev \
        mpich && \
    rm -rf /var/lib/apt/lists/*

# CMake installation layer
RUN mkdir cmake_install && \
    cd cmake_install && \
    wget https://github.com/Kitware/CMake/releases/download/v3.15.2/cmake-3.15.2.tar.gz && \
    tar -zxvf cmake-3.15.2.tar.gz && \
    cd cmake-3.15.2 && \
    ./bootstrap && \
    make && \
    make install && \
    cd .. && \
    rm -rf cmake_install
