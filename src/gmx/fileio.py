"""Provide the high-level interface to the file i/o behaviors the gmx package.

The submodule name may seem longer than necessary, but avoids a
namespace collision with a standard Python module on the default path.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

__all__ = ['TprFile', 'read_tpr', 'write_tpr_file']

import gmx.core
import gmx.util
from gmx.exceptions import UsageError

_current_dir = os.getcwd()

class TprFile:
    """Handle to a Gromacs simulation run input file.
    """
    def __init__(self, filename=None, mode=None):
        """Open a TPR file.

        File access mode is indicated by 'r' for read-only access.

        Args:
            filename (str): Path to a run input file (e.g. 'myfile.tpr')
            mode (str): File access mode.

        Note:
            Currently, TPR files are read-only from the Python interface.

        Example:

            >>> import gmx
            >>> filehandle = gmx.fileio.TprFile(filename, 'r')

        """
        if filename is None:
            raise UsageError("TprFile objects must be associated with a file.")
        if mode == 'r':
            self.mode = 'r'
        if mode != 'r':
            raise UsageError("TPR files only support read-only access.")
        self.filename = filename
        self._tprFileHandle = None

    def close(self):
        # self._tprFileHandle.close()
        self._tprFileHandle = None

    def __repr__(self):
        return "gmx.fileio.TprFile('{}', '{}')".format(self.filename, self.mode)

    def __enter__(self):
        self._tprFileHandle = gmx.core.read_tprfile(self.filename)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return

class _NodeOutput(object):
    """Implement the `output` attribute of a simulation input node.

    Attributes:
        parameters: Simulation parameters for (re)written TPR file.
        structure: Atomic details (not yet implemented)
        topology: Molecular force field details (not yet implemented)
        state: Simulation state information (not yet implemented)

    """
    def __init__(self, parameters=None, structure=None, topology=None, state=None):
        """Initialize getters for output ports."""
        self.__tprfile = parameters

    @property
    def parameters(self):
        with self.__tprfile as fh:
            params = fh._tprFileHandle.params()
        return params

    @property
    def structure(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")

    @property
    def topology(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")

    @property
    def state(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")


class _SimulationInput(object):
    """
    Simulation input interface for a TPR file read by gmx.fileio.read_tpr()

    Attributes:
        parameters: Simulation parameters for (re)written TPR file.
        structure: Atomic details (not yet implemented)
        topology: Molecular force field details (not yet implemented)
        state: Simulation state information (not yet implemented)

    """
    def __init__(self, tprfile):
        if not isinstance(tprfile, TprFile):
            # This class is an implementation detail of TPR file I/O...
            raise gmx.exceptions.ApiError("Must be initialized from a gmx.fileio.TprFile object.")
        self.__tprfile = tprfile
        self.__parameters = None

    @property
    def parameters(self):
        if self.__parameters is None:
            with self.__tprfile as fh:
                self.__parameters = fh._tprFileHandle.params()
        return self.__parameters

    @property
    def structure(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")

    @property
    def topology(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")

    @property
    def state(self):
        raise gmx.exceptions.FeatureNotAvailableError("property not implemented.")


def read_tpr(tprfile=None):
    """
    Get a simulation input object from a TPR run input file.

    Arguments:
        tprfile : TPR input object or filename

    Returns:
         simulation input object

    The returned object may be inspected by the user. Simulation input parameters
    may be extracted through the `parameters` attribute.

    Example:
        >>> sim_input = gmx.fileio.read_tpr(tprfile=tprfilename)
        >>> params = sim_input.parameters.extract()
        >>> print(params['init-step'])
        0

    Supports the `read_tpr` gmxapi work graph operation. (not yet implemented)
    """
    if not isinstance(tprfile, TprFile):
        try:
            tprfile = TprFile(gmx.util.to_utf8(tprfile), mode='r')
        except:
            tprfile = None
    if tprfile is None:
        raise UsageError("TPR object or file name is required.")

    return _SimulationInput(tprfile)

# In initial implementation, we extract the entire TPR file contents through the
# TPR-backed GmxMdParams implementation.
def write_tpr_file(output, input=None):
    """
    Create a new TPR file, combining user-provided input.

    .. versionadded:: 0.0.8
        Initial version of this tool does not know how to generate a valid simulation
        run input file from scratch, so it requires input derived from an already valid
        TPR file.

    The simulation input object should provide the gmx simulation_input interface,
    with output ports for `parameters`, `structure`, `topology`, and `state`, such
    as a TprFileHandle

    Arguments:
        output : TPR file name to write.
        input : simulation input data from which to write a simulation run input file.

    Use this function to write a new TPR file with data updated from an
    existing TPR file. Keyword arguments are objects that can provide gmxapi
    compatible access to the necessary simulation input data.

    In the initial version, data must originate from an existing TPR file, and
    only simulation parameters may be rewritten. See gmx.fileio.read_tpr()

    Example:
        >>> sim_input = gmx.fileio.read_tpr(tprfile=tprfilename)
        >>> sim_input.parameters.set('init-step', 1)
        >>> gmx.fileio.write_tpr_file(newfilename, input=sim_input)

    Warning:
        The interface is in flux.

    TODO:
        Be consistent about terminology for "simulation state".
        We are currently using "simulation state" to refer both to the aggregate of
        data (superset) necessary to launch or continue a simulation _and_ to the
        extra data (subset) necessary to capture full program state, beyond the
        model/method input parameters and current phase space coordinates. Maybe we
        shouldn't expose that as a separate user-accessible object and should instead
        make it an implementation detail of a wrapper object that has standard
        interfaces for the non-implementation-dependent encapsulated data.

    Returns:
        TBD : possibly a completion condition of some sort and/or handle to the new File
    """

    if not hasattr(input, 'parameters'):
        if hasattr(input, 'output'):
            if hasattr(input.output, 'parameters'):
                parameters = input.output.parameters
            else:
                raise ValueError("Need output.parameters")
        else:
            raise ValueError("Need output.parameters")
    else:
        parameters = input.parameters

    if not isinstance(parameters, gmx.core.SimulationParameters):
        raise gmx.exceptions.TypeError("You must provide a gmx.core.SimulationParameters object to `parameters` as input.")
    gmx.core.write_tprfile(output, parameters)


# Note: this has been dead since at least 0.0.3, but we should revive it...
class TrajectoryFile:
    """Provides an interface to Gromacs supported trajectory file formats.

    TrajectoryFile objects are Trajectory data sources or sinks (depending on
    access mode) that can be used in a Gromacs tool chain. If data is requested
    from an object before it has been explicitly attached to a tool chain or
    runner, these are implicitly created. If no execution context is specified,
    a local single-threaded context is created.

    Thus, stand-alone TrajectoryFile objects can serve as a rudimentary interface
    to file types supported by Gromacs.

    If the file mode is 'r', the object created supports the Python iterator
    protocol for reading one frame at a time.

    Other file modes are not yet supported.

    Example
        Sample script::

           import gmx

           # Create the Python proxy to the caching gmx::TrajectoryAnalysisModule object.
           mytraj = gmx.io.TrajectoryFile(filename, 'r')

           # Implicitly create the Runner object and get an iterator based on selection.
           frames = mytraj.select(...)

           # Iterating on the module advances the Runner.
           # Since the Python interpreter is explicitly asking for data,
           # the runner must now be initialized and begin execution.
           # mytraj.runner.initialize(context, options)
           # mytraj.runner.next()
           next(frames)

           # Subsequent iterations only need to step the runner and return a frame.
           for frame in frames:
               # do some stuff

           # The generator yielding frames has finished, so the runner has been released.
           # The module caching the frames still exists and could still be accessed or
           # given to a new runner with a new selection.
           for frame in mytraj.select(...):
               # do some other stuff

    """
    # TODO: decide how to represent file mode and how/if to reflect in the C++ API
    READ = 1

    def __init__(self, filename, mode=None):
        """Prepare filename for the requested mode of access.

        Args:
            filename (str): filesystem path to the file to be opened.
            mode (str): file access mode. 'r' for read.

        """
        if mode == 'r':
            self.mode = TrajectoryFile.READ
            self.filename = filename
            self._cpp_module = gmx.core.CachingTafModule()
        #elif mode == 'w':
        #    self.mode = TrajectoryFile.WRITE
        else:
            raise UsageError("Trajectory file access mode not supported.")

    def select(self, selection=None):
        """Generator to read atom positions frame-by-frame.

        An analysis module runner is implicitly created when the iterator
        is returned and destroyed when the iterator raises StopIteration.

        Args:
            selection: atom selection to retrieve from trajectory file

        Returns:
            iterator: :py:class:`core.Frame` objects

        """
        # Implementation details:
        #
        # 1. Python asks for first frame.
        # 2. Runner starts.
        # 3. Runner calls analyze_frame via next().
        # 4. Runner returns control to Python interpreter and yields frame.
        # 5. Python accesses the frame by interacting with the module.
        # 6. Python asks for next frame.
        # 7. Runner calls finish for the current frame and analyze for the next.
        # 8. Runner returns control to Python.
        # 9. When Runner runs out of frames, the Python generator is done.
        # 10. When Python leaves the context object or otherwise destroys the runner, it cleans up.

        #assert(isinstance(selection, gmx.core.Selection))

        # Create runner and bind module
        runner = gmx.core.TafRunner(self._cpp_module)

        # Create options object with which to initialize runner
        options = gmx.core.Options(filename=self.filename)

        # Initialize runner and module
        runner.initialize(options)
        while runner.next():
            frame = self._cpp_module.frame()
            yield frame
