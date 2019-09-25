This is a fork of the [main Gromacs project](http://www.gromacs.org/) that demonstrates
gmxapi functionality targeting the 2020 official release.
It exists primarily to support the migration of the [`gmxapi`](https://github.com/kassonlab/gmxapi) 
Python package to the GROMACS repository.
The forked project lives on GitHub at 
[https://github.com/kassonlab/gromacs-gmxapi](https://github.com/kassonlab/gromacs-gmxapi/)
and is based on the "sandbox-gmxapi" branch of the upstream repository.

[![Build Status](https://travis-ci.org/kassonlab/gromacs-gmxapi.svg?branch=master)](https://travis-ci.org/kassonlab/gromacs-gmxapi)

This README.md file supplants the main README file to avoid merge conflicts while 
providing convenient documentation to the repository browser.

See the file `README` in this directory for more information on GROMACS and this fork.

See the file `python_packaging/README.md` for more on the organization of this fork.

Refer to Redmine issue [2045](https://redmine.gromacs.org/issues/2045) for issue
tracking.

# Installing GROMACS

Note that unless you need the most experimental gmxapi features,
you should probably be building and installing either GROMACS 2019
or the (upstream) GROMACS master branch.

Install as you would a regular copy of GROMACS. The following example downloads the source into a directory named `gromacs`,
creates a parallel (out-of-source) `build` directory, configures, builds, and installs. Use e.g. `make -j10 install` to build in parallel with 10 processes.

    $ git clone https://github.com/kassonlab/gromacs-gmxapi.git gromacs
    $ mkdir build
    $ cd build
    $ cmake ../gromacs-gmxapi \
      -DCMAKE_INSTALL_PREFIX=/path/to/where/i/want/gromacs \
      -DGMX_THREAD_MPI=ON \
      -DGMX_GPU=OFF \
      -DGMX_ENABLE_CCACHE=ON \
      -DGMXAPI=ON
    $ make install

You may then either source the GMXRC file (as usual for GROMACS use) or export 
the environment variable `gmxapi_DIR=/path/to/where/i/want/gromacs` to help 
`gmxapi` clients such as the Python package or your own CMake project to find
what it needs to build against the gmxapi library.

# Installing Python components

Change to the `python_packaging` directory and refer to 
[README.md](python_packaging/README.md)
for details.
