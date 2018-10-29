#!/usr/bin/env/python
"""Providing Python access to Gromacs

The gmx Python module provides an interface suitable for scripting GROMACS
workflows, interactive use, or connectivity to external Python-based APIs. The
project is hosted at https://github.com/kassonlab/gmxapi

The API allows interaction with GROMACS that is decoupled from command-line
interfaces, terminal I/O, and filesystem access. Computation and data management
are managed by the API until/unless the user explicitly requests specific data,
such as for writing to a local file or manipulating with a tool that does not
implement the Gromacs API.

When data must be retrieved from GROMACS, efforts are made to do so as
efficiently as possible, so the user should consult documentation for the
specific GROMACS objects they are interested in regarding efficient access, if
performance is critical. For instance, exporting GROMACS data directly to a
numpy array can be much faster and require less memory than exporting to a
Python list or tuple, and using available iterators directly can save a lot of
memory versus creating an array and then iterating over it in two separate
steps.

For more efficient iterative access to GROMACS data, such as analyzing a
simulation in progress, or applying Python analysis scripts in a trajectory
analysis workflow, consider using an appropriate call-back or, better yet,
creating a C++ plugin that can be inserted directly in the tool chain.

For more advanced use, the module provides means to access or manipulate GROMACS
more granularly than the command-line tool. This allows rapid prototyping of new
methods, debugging of unexpected simulation behavior, and adaptive workflows.

Installation:
    The gmxapi library for GROMACS must be installed to build and install the gmx
    Python module. Retrieve the GROMACS fork from
    https://github.com/kassonlab/gromacs-gmxapi and do a normal CMake build and
    install.

    Then, download the repository from https://github.com/kassonlab/gmxapi and refer
    to `docs/install.rst <./install.html>`_ for details on installing this Python
    module.

Packaging:
    This Python package is built with CMake, but attempts to flexibly handle the
    user's choice of Python installation. Python virtual environments are recommended.
    If you have trouble installing this software in a Python virtual environment and
    find the accompanying documentation inadequate, please open an issue ticket at
    https://github.com/kassonlab/gmxapi/issues

Citing:

Irrgang, M. E., Hays, J. M., & Kasson, P. M.
gmxapi: a high-level interface for advanced control and extension of molecular dynamics simulations.
*Bioinformatics* 2018.
DOI: `10.1093/bioinformatics/bty484 <https://doi.org/10.1093/bioinformatics/bty484>`_
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['get_context', 'run']

# Import system facilities
import logging
logging.getLogger().addHandler(logging.NullHandler(level=logging.DEBUG))
logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger().info("Setting up logging for gmx package.")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Importing gmx.")

# Import submodules.
from gmx import exceptions
from gmx import workflow
from gmx import version

# Import top-level components
__version__ = version.__version__
from gmx.system import System
from gmx.context import get_context


def run(work=None):
    """Run the provided work on available resources.

    Args:
        work (gmx.workflow.WorkSpec): either a WorkSpec or an object with a `workspec` attribute containing a WorkSpec object.

    Returns:
        gmx.status.Status: run status.

    """
    if isinstance(work, workflow.WorkSpec):
        workspec = work
    elif hasattr(work, "workspec") and isinstance(work.workspec, workflow.WorkSpec):
        workspec = work.workspec
    else:
        raise exceptions.UsageError("Runnable work must be provided to run.")
    # Find a Context that can run the work and hand it off.
    with get_context(workspec) as session:
        status = session.run()
    return status


# if __name__ == "__main__":
#     import doctest
#     import gmx
#     from pkg_resources import Requirement, resource_filename
#     tpr_filename = resource_filename(Requirement.parse("gmx"), "topol.tpr")
#     doctest.testmod()
