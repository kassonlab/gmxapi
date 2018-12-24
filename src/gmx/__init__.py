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
import json
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


def commandline_operation(executable=None, arguments=None, input=None, output=None, shell=False):
    """Execute a command line program in a subprocess.

    Configure an executable in a subprocess. Executes when run in an execution
    Context, as part of a work graph or via gmx.run(). Runs in the current
    working directory.

    Shell processing is not enabled, but can be considered for a future version.
    This means that shell expansions such as environment variables, globbing (`*`),
    and other special symbols (like `~` for home directory) are not available.
    This allows a simpler and more robust implementation, as well as a better
    ability to uniquely identify the effects of a command line operation. If you
    think this disallows important use cases, please let us know.

    Arguments:
         arguments : a single tuple (or list) to be the first arguments to `executable`
         input : mapping of command line flags to input filename arguments
         output : mapping of command line flags to output filename arguments

    Arguments are iteratively added to the command line with standard Python
    iteration, so you should use a tuple or list even if you have only one parameter.
    I.e. If you provide a string with `arguments="asdf"` then it will be passed as
    `... "a" "s" "d" "f"`. To pass a single string argument, `arguments=("asdf")`
    or `arguments=["asdf"]`.

    `input` and `output` should be a dictionary with string keys, where the keys
    name command line "flags" or options.

    Example:
        Execute a command named `exe` that takes a flagged option for file name
        (stored in a local Python variable `my_filename`) and an `origin` flag
        that uses the next three arguments to define a vector.

            >>> import gmx
            >>> from gmx import commandline_operation as cli
            >>> my_filename = "somefilename"
            >>> my_op = cli('exe', arguments=['--origin', 1.0, 2.0, 3.0], input={'-f': my_filename})
            >>> gmx.run(my_op)

    Returns:
        Proxy to an operation in a work graph.

    """
    import hashlib
    from gmx import util
    if shell != False:
        raise exceptions.UsageError("Operation does not support shell processing.")
    params = {}
    command = util.to_string(executable)
    if command is None or command == '':
        raise exceptions.UsageError("Need an executable command.")
    else:
        params['executable'] = command
        # If we can confirm that we are handling iterables well, we can update
        # the documentation, revising the warning about single string arguments
        # and noting the automatic conversion of single scalars.
        #
        # Strings are iterable, but we want to treat them as scalars.
        if isinstance(arguments, (str, bytes)):
            arguments = [arguments]
        # Python 2 compatibility:
        try:
            if isinstance(arguments, unicode):
                arguments = [arguments]
        except NameError as e:
            # Python 3 does not have unicode type
            pass
        if arguments is not None:
            params['arguments'] = list([util.to_string(arg) for arg in arguments])

        if input is not None:
            params['input'] = []
            for kwarg in input:
                # the flag
                params['input'].append(util.to_string(kwarg))
                # the filename argument
                # TODO: this needs to trigger scatter when appropriate
                params['input'].append(util.to_string(input[kwarg]))

        if output is not None:
            params['output'] = []
            for kwarg in input:
                # the flag
                params['output'].append(util.to_utf8(kwarg))
                # the filename argument
                # TODO: this needs to trigger scatter when appropriate
                params['output'].append(util.to_utf8(input[kwarg]))

    namespace = 'gmxapi'
    operation = 'commandline_operation'
    element = workflow.WorkElement(namespace=namespace,
                                   operation=operation,
                                   params=params)
    # Uniquely identify the input and output of this operation for placement in
    # a work graph.
    identifying_string = util.to_utf8(json.dumps([namespace, operation, params]))
    digest = hashlib.sha256(identifying_string).hexdigest()
    element.name = 'cli_{}'.format(digest)
    return element

# if __name__ == "__main__":
#     import doctest
#     import gmx
#     from pkg_resources import Requirement, resource_filename
#     tpr_filename = resource_filename(Requirement.parse("gmx"), "topol.tpr")
#     doctest.testmod()
