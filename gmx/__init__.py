#!/usr/bin/env/python
#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2017, by the GROMACS development team, led by
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

"""
Provide Python access to Gromacs
================================

The gmx Python module provides an interface suitable for scripting Gromacs
workflows, interactive use, or connectivity to external Python-based APIs.

The API allows interaction with Gromacs that is decoupled from command-line
interfaces, terminal I/O, and filesystem access. Computation and data management
are managed by the API until/unless the user explicitly requests specific data,
such as for writing to a local file or manipulating with a tool that does not
implement the Gromacs API.

When data must be retrieved from Gromacs, efforts are made to do so as efficiently
as possible, so the user should consult documentation for the specific Gromacs
objects they are interested in regarding efficient access, if performance is
critical. For instance, exporting Gromacs data directly to a numpy array can be
much faster and require less memory than exporting to a Python list or tuple,
and using available iterators directly can save a lot of memory versus creating
an array and then iterating over it in two separate steps.

For more efficient iterative access to Gromacs data, such as analyzing a simulation
in progress, or applying Python analysis scripts in a trajectory analysis workflow,
consider using an appropriate call-back or, better yet, creating a C++ plugin
that can be inserted directly in the tool chain.

For more advanced use, the module provides means to access or manipulate Gromacs
more granularly than the command-line tool. This allows rapid prototyping of
new methods, debugging of unexpected simulation behavior, and adaptive workflows.

Installation
------------

The gmxapi library must be installed to build and install the gmx module. Do a normal CMake build and install.

Then,
using the install location of Gromacs, do `pip install /path/to/gromacs/include` to use the `setup.py` file that was
generated and installed with libgmxapi.

Then, from the top level directory of the repository, gmx is built and installed with
setuptools, using either `setup.py` classically or by using `pip` (recommended) with

    $ pip install .

If you are not using a virtual environment, the `--user` flag tells pip to only install in the
home directory for the user, but then this conflicts with subsequent installations in virtual
environments for Python installations of the same version. So it's kind of an either/or thing.

After installation, tests can be run with your favorite python test driver. E.g.
``nosetests gmx`` or
``pytest --pyargs gmx``

"""
# currently broken because full git repo is necessary to build bundled gromacs due to pybind inclusion
#From the repository, testing in Python virtual environments via `tox` is performed by `setup.py test`.


from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# TODO: what should happen when ``from gmx import *``?
__all__ = ['Status', 'System', 'context', 'md', 'runner']

from . system import System

from . import exceptions
from . exceptions import *
__all__.extend(exceptions.__all__)

from . import context
from . import md
from . import runner
from . status import Status
from . import util

from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed
    pass

# if __name__ == "__main__":
#     import doctest
#     import gmx
#     from pkg_resources import Requirement, resource_filename
#     tpr_filename = resource_filename(Requirement.parse("gmx"), "topol.tpr")
#     doctest.testmod()
