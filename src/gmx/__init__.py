#!/usr/bin/env/python
"""
Providing Python access to Gromacs
==================================

The gmx Python module provides an interface suitable for scripting GROMACS
workflows, interactive use, or connectivity to external Python-based APIs.
The project is hosted at https://github.com/kassonlab/gmxapi

The API allows interaction with GROMACS that is decoupled from command-line
interfaces, terminal I/O, and filesystem access. Computation and data management
are managed by the API until/unless the user explicitly requests specific data,
such as for writing to a local file or manipulating with a tool that does not
implement the Gromacs API.

When data must be retrieved from GROMACS, efforts are made to do so as efficiently
as possible, so the user should consult documentation for the specific GROMACS
objects they are interested in regarding efficient access, if performance is
critical. For instance, exporting GROMACS data directly to a numpy array can be
much faster and require less memory than exporting to a Python list or tuple,
and using available iterators directly can save a lot of memory versus creating
an array and then iterating over it in two separate steps.

For more efficient iterative access to GROMACS data, such as analyzing a simulation
in progress, or applying Python analysis scripts in a trajectory analysis workflow,
consider using an appropriate call-back or, better yet, creating a C++ plugin
that can be inserted directly in the tool chain.

For more advanced use, the module provides means to access or manipulate GROMACS
more granularly than the command-line tool. This allows rapid prototyping of
new methods, debugging of unexpected simulation behavior, and adaptive workflows.

Installation
------------

Download the ``gmxpy`` repository from https://github.com/kassonlab/gmxapi and refer
to the README.md file for details on installing this Python module.

The gmxapi library must be installed to build and install the gmx module.
Retrieve the GROMACS fork from https://github.com/kassonlab/gromacs-gmxapi and
do a normal CMake build and install.

Packaging
---------

There are a lot of open questions about packaging gmxpy. Many users will find it handy or essential to be able to
install with distutils (setup.py), pip, or conda, in order to use arbitrary third-party Python tools in their workflow,
so we need to be able to build the C++ extension against an already-installed GROMACS for an arbitrary Python interpreter.
But it seems likely that system administrators might install the package for at least one or two Python installations to
be managed with a modules system on an HPC cluster, and we would encourage this as a good time for testing and building
docs, but after that the full distribution and CMake process may be unnecessary.

I'm leaning towards separating the C++ and pure Python aspects of gmxpy (currently gmx and gmx.core) such that the full
distribution of gmx.core is entirely CMake-based with testing and doxygen builds. It could be installed into a GROMACS
installation path instead of the site-packages directory for a given interpreter and installation could include sufficient
source code from which to rebuild for a different interpreter, though I'm not sure if it should be installed into a
site-packages directory. The pure Python gmx package can then just regard gmxCore as an external package (maybe not even
a hard dependency) and freely installed into site-packages directories. It may require some non-standard facilities to
inform the user of its dependency or to find and build gmxCore in non-confusing, non-error-prone way.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# TODO: what should happen when ``from gmx import *``?
__all__ = ['Status', 'System', 'get_context', 'run']

# Import system facilities
import logging
logging.getLogger().addHandler(logging.NullHandler(level=logging.DEBUG))
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().info("Setting up logging for gmx package.")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Importing gmx.")

# Import submodules.
from . import exceptions
from . exceptions import *
__all__.extend(exceptions.__all__)

from . import context
from . import workflow
from . status import Status
from . import util

# Import top-level components
from .version import __version__
from .system import System
from .workflow import run
from .context import get_context

# if __name__ == "__main__":
#     import doctest
#     import gmx
#     from pkg_resources import Requirement, resource_filename
#     tpr_filename = resource_filename(Requirement.parse("gmx"), "topol.tpr")
#     doctest.testmod()
