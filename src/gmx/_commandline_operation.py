"""
Provide command line operation for the basic Context.

:func:`commandline` Helper function adds an operation to the work graph
and returns a proxy to the Python interpreter. Imported by :module:`gmx`.

:func:`_commandline` utility function provides callable function object to execute
a command line tool in a subprocess. Imported by :module:`gmx.util` for standalone
operation and by the session runner for work graph execution.

:module:`gmx.context` maps the `gmxapi.commandline` operation to
:func:`_gmxapi_graph_director` in this module to get a Director that can be used
during Session launch.

TODO: I am testing a possible convention for helper function, factory function, and implementation.
For the ``gmxapi`` work graph operation name space, `gmx.context` looks for
operations in ``gmx._<name>``, where *<name>* is the operation name. We will
probably adopt a slightly different convention for the ``gromacs`` name space.
For all other name spaces, the package attempts to import the namespace as a
module and to look for operation implementations as a module attribute matching
the name of the operation. The attribute may be a callable or an object implementing
the Operation interface. Such an object may itself be a module.
(Note this would also provide a gateway to mixing Python and C++ in plugins,
since the namespace module may contain other code or import additional modules.)

The work graph node ``output`` contains a ``file`` port that is
a gmxapiMap output of command line arguments to filenames.

.. versionadded:: 0.0.8

    Graph node structure::
    'elements': {
        'cli_op_aaaaaa': {
            'label': 'exe1',
            'namespace': 'gmxapi',
            'operation': 'commandline',
            'params': {
                'executable': [],
                'arguments': [[]],
            },
            'depends': []
        },
        'cli_op_bbbbbb': {
            'label': 'exe2',
            'namespace': 'gmxapi',
            'operation': 'commandline',
            'params': {
                'executable': [],
                'arguments': [[], []],
            },
            'depends': ['cli_op_aaaaaa']
        },
    }

.. versionchanged:: 0.1

    Output ports are determined by querying the operation.

    Graph node structure::
    'elements': {
        'filemap_aaaaaa': {
            operation: 'make_map',
            'input': {
                '-f': ['some_filename'],
                '-t': ['filename1', 'filename2']
            },
            # 'output': {
            #     'file': 'gmxapi.Map'
            # }
        },
        'cli_op_aaaaaa': {
            'label': 'exe1',
            'namespace': 'gmxapi',
            'operation': 'commandline',
            'input': {
                'executable': [],
                'arguments': [[]],
                # this indirection avoids naming complications. Alternatively,
                # we could make parsing recursive and allow arbitrary nesting
                # with special semantics for dictionaries (as well as lists)
                'input_file_arguments': 'filemap_aaaaaa',
            },
            # 'output': {
            #     'file': 'gmxapi.Map'
            # }
        },
        'filemap_bbbbbb: {
            'label': 'exe1_output_files',
            'namespace': 'gmxapi',
            'operation': 'make_map',
            'input': {
                '-in1': 'cli_op_aaaaaa.output.file.-o',
                '-in2': ['static_fileB'],
                '-in3': ['arrayfile1', 'arrayfile2'] # matches dimensionality of inputs
            }
        },
        'cli_op_bbbbbb': {
            'label': 'exe2',
            'namespace': 'gmxapi',
            'operation': 'commandline',
            'input': {
                'executable': [],
                'arguments': [],
                'input_file_arguments': 'filemap_bbbbbb'
            },
        },

    }

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = []

import importlib
import os
import warnings
import tempfile

from gmx import exceptions
from gmx import logging
from gmx import get_context
from gmx import status
import gmx.version


# Module-level logger
logger = logging.getLogger(__name__)
logger.info('Importing gmx._commandline_operation')

# TODO: don't rely on module globals to keep logger alive!
# We want to use logger during shutdown, so keep references in objects

class CommandLineOperation(object):
    """Proxy returned by commandline helper function.


    """
    @property
    def output(self):
        return None

    @classmethod
    def from_node(cls, node):
        """Translate graph node."""
        return CommandLineOperation()

class Director(object):
    """Provide Director interface for session launch."""
    def construct(self, graph):
        """Interact with the work graph."""
    def add_subscriber(self, subscriber):
        """Bind with other Directors to set up data flow."""

def make_commandline_operation(*args, context=None, **kwargs):
    """Generate a graph node in the current graph in the provided or current context."""
    if context is None:
        context = get_context()
    if gmx.version.api_is_at_least(0, 1):
        # Don't use WorkElement, use graph node view.
        pass
    else:
        # Use WorkElement. New schema and semantics not yet implemented.
        executable = ''
        arguments = ''
        element = gmx.workflow.WorkElement(namespace='gmxapi', operation='commandline',
                                           params={'executable': executable,
                                                   'arguments': arguments})
        element.name = ''
    operation = context.make_operation()
    return operation

def commandline(*args, context=None, **kwargs):
    """Factory function to produce an Operation.

    If not provided, context is retrieved with gmx.get_context().

    If there are no other keyword arguments and *args contains a single object,
    check if that object is a work graph node. If so, dispatch directly. Otherwise,
    dispatch arguments to make_commandline_operation.

    """
    if context is None:
        context = get_context()

    operation = None
    if len(kwargs) == 0 and len(args) == 1 and hasattr(args[0], '_gmxapi_graph_node'):
        # read input from arg[0]
        operation = CommandLineOperation.from_node(args[0])
    else:
        # build graph node from arguments
        operation = make_commandline_operation(*args, context=context, **kwargs)
    return operation

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
            output_ports = {}
            if 'stdout' in self.__output:
                output_ports['stdout'] = self.__output['stdout']
            if 'stderr' in self.__output:
                output_ports['stderr'] = self.__output['stderr']
            if 'returncode' in self.__output:
                output_ports['returncode'] = self.__output['returncode']
            return output_ports

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
