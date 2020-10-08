#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2020, by the GROMACS development team, led by
# Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# and including many others, as listed in the AUTHORS file in the
# top-level source directory and at http://www.gromacs.org.
#
# GROMACS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# GROMACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GROMACS; if not, see
# http://www.gnu.org/licenses, or write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
#
# If you want to redistribute modifications to GROMACS, please
# consider that scientific software is very special. Version
# control is crucial - bugs must be traceable. We will be happy to
# consider code for inclusion in the official distribution, but
# derived work must not be called official GROMACS. Details are found
# in the README & COPYING files - if they are missing, get the
# official version at http://www.gromacs.org.
#
# To help us fund GROMACS development, we humbly ask that you cite
# the research papers on the package. Check out http://www.gromacs.org.

"""A `utility` module helps manage the matrix of configurations for CI testing and build containers.

Provides importable argument parser.

Authors:
    * Paul Bauer <paul.bauer.q@gmail.com>
    * Eric Irrgang <ericirrgang@gmail.com>
    * Joe Jordan <e.jjordan12@gmail.com>
    * Mark Abraham <mark.j.abraham@gmail.com>

"""

import argparse


parser = argparse.ArgumentParser(description='GROMACS CI image slug options.', add_help=False)
"""A parent parser for tools referencing image parameters.

This argparse parser is defined for convenience and may be used to partially initialize
parsers for tools.

.. warning:: Do not modify this parser.

    Instead, inherit from it with the *parents* argument to :py:class:`argparse.ArgumentParser`
"""

parser.add_argument('--cmake', type=str, default='3.13.0',
                    help='Selection of CMake version to provide to base image')
compiler_group = parser.add_mutually_exclusive_group()
compiler_group.add_argument('--gcc', type=int, nargs='?', const=7, default=7,
                            help='Select GNU compiler tool chain. (Default) '
                                 'Some checking is implemented to avoid incompatible combinations')
compiler_group.add_argument('--llvm', type=str, nargs='?', const='7', default=None,
                            help='Select LLVM compiler tool chain. '
                                 'Some checking is implemented to avoid incompatible combinations')
compiler_group.add_argument('--icc', type=int, nargs='?', const=19, default=None,
                            help='Select Intel compiler tool chain. '
                                 'Some checking is implemented to avoid incompatible combinations')
# TODO currently the installation merely gets the latest beta version of oneAPI,
# not a specific version. GROMACS probably doesn't need to address that until
# oneAPI makes an official release. Also, the resulting container is a mix
# of packages with different betaXY version numbers, which hopefully works and
# is what Intel intends...
compiler_group.add_argument('--oneapi', type=str, nargs='?', const="2021.1-beta09", default=None,
                            help='Select Intel oneAPI package version.')

linux_group = parser.add_mutually_exclusive_group()
# Ubuntu 20+ is not yet tested. See issue #3680
linux_group.add_argument('--ubuntu', type=str, nargs='?', const='18.04', default='18.04',
                         help='Select Ubuntu Linux base image. (default: ubuntu 18.04)')
linux_group.add_argument('--centos', type=str, nargs='?', const='7', default=None,
                         help='Select Centos Linux base image.')

parser.add_argument('--cuda', type=str, nargs='?', const='10.2', default=None,
                    help='Select a CUDA version for a base Linux image from NVIDIA.')

parser.add_argument('--mpi', type=str, nargs='?', const='openmpi', default=None,
                    help='Enable MPI (default disabled) and optionally select distribution (default: openmpi)')

parser.add_argument('--tsan', type=str, nargs='?', const='llvm', default=None,
                    help='Build special compiler versions with TSAN OpenMP support')

parser.add_argument('--opencl', type=str, nargs='?', const='nvidia', default=None,
                    help='Provide environment for OpenCL builds')

parser.add_argument('--clfft', type=str, nargs='?', const='master', default=None,
                    help='Add external clFFT libraries to the build image')

parser.add_argument('--doxygen', type=str, nargs='?', const='1.8.5', default=None,
                    help='Add doxygen environment for documentation builds. Also adds other requirements needed for final docs images.')
