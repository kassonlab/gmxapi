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


def commandline_operation(executable=None, arguments=None, input=None, output=None, shell=False):
    """Execute in a subprocess.

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
        An Operation to invoke local subprocess(es)

    Note:
        STDOUT is available if a consuming operation is bound to `output.stdout`.
        STDERR is available if a consuming operation is bound to `output.stderr`.
        Otherwise, STDOUT and/or STDERR is(are) closed when command is called.

    Warning:
        Commands using STDIN cannot be used and is closed when command is called.

    Todo:
        We can be more helpful about managing the work graph for operations, but
        we need to resolve issue #90 and others first.

    """
    import subprocess
    import os
    from gmx import util
    if hasattr(os, 'devnull'):
        devnull = os.devnull
    elif os.path.exists('/dev/null'):
        devnull = '/dev/null'
    else:
        devnull = None
    if shell != False:
        raise exceptions.UsageError("Operation does not support shell processing.")
    command = ""
    try:
        command = util.which(executable)
    except:
        # We could handle specific errors, but right now we only care
        # whether we have something we can run.
        pass
    command_args = []
    if command is None or command == "":
        raise exceptions.UsageError("Need an executable command.")
    else:
        command_args = [util.to_utf8(command)]
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
            for arg in arguments:
                command_args.append(util.to_utf8(arg))

        if input is not None:
            for kwarg in input:
                # the flag
                command_args.append(util.to_utf8(kwarg))
                # the filename argument
                command_args.append(util.to_utf8(input[kwarg]))

        if output is not None:
            for kwarg in input:
                # the flag
                command_args.append(util.to_utf8(kwarg))
                # the filename argument
                command_args.append(util.to_utf8(input[kwarg]))

    class CommandlineOperation(object):
        def __init__(self, command):
            self.command = command

            self.__input = {}
            self.__output = {}

        @property
        def input(self):
            """Operation graph input(s) not implemented.

            See issue #203
            """
            # value = object()
            # value.stdin = self.__input['stdin']
            # return value
            raise exceptions.FeatureNotAvailableError("command_line operation input ports not implemented (yet).")

        # Provide an `output` attribute that is an object with properties for
        # each output port.
        @property
        def output(self):
            """Graph output(s) for the operation, if bound to subscribers.

            The subprocess is executed with STDOUT and STDERR closed, by default.
            But if a consuming operation is bound to one of the output ports,
            output.stdout or output.stderr, then the output of the command is
            captured and stored.

            To do: we should take precautions to handle buffering and memory
            tidiness. The session manager could make sure that the output buffers
            for the subprocess are read frequently and published to subscribers,
            but it might make sense to require that stdout and stderr are at
            least intermediately sent directly to files until the operation is
            completed and the output filehandles closed, such that a command
            line operation produces a single clear data event when it completes.
            """
            # This will need to be a class instance with more sophisticated
            # property attributes in the future...
            _output = {}
            if 'stdout' in self.__output:
                _output['stdout'] = self.__output['stdout']
            if 'stderr' in self.__output:
                _output['stderr'] = self.__output['stderr']
            if 'returncode' in self.__output:
                _output['returncode'] = self.__output['returncode']
            return _output

        def __call__(self):
            # File descriptors 0, 1, and 2 are inherited from parent and we don't
            # want to close them for the parent, so we need to redirect or close
            # them in the subprocess. Setting to the null device is probably
            # sufficient, but it might not be easy to find on all systems.
            # Python 3.3+ has better support.
            # To do: Handle input and output flow.
            null_filehandle = open(devnull, 'w')
            try:
                returncode = subprocess.check_call(self.command,
                                                   shell=shell,
                                                   stdin=null_filehandle,
                                                   stdout=null_filehandle,
                                                   stderr=null_filehandle)
            except subprocess.CalledProcessError as e:
                returncode = e.returncode
                # What should we do with error (non-zero) exit codes?
                logger.info("commandline operation had non-zero return status when calling {}".format(e.cmd))
                self.__output['erroroutput'] = e.output
            self.__output['returncode'] = returncode
            # return self.output.returncode == 0
            return self.output['returncode'] == 0

    operation = None
    if len(command_args) > 0:
        operation = CommandlineOperation(command_args)
    else:
        raise exceptions.UsageError("No command line could be constructed.")
    return operation

# if __name__ == "__main__":
#     import doctest
#     import gmx
#     from pkg_resources import Requirement, resource_filename
#     tpr_filename = resource_filename(Requirement.parse("gmx"), "topol.tpr")
#     doctest.testmod()
