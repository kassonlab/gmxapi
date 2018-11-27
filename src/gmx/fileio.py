"""Provide the high-level interface to the file i/o behaviors the gmx package.

The submodule name may seem longer than necessary, but avoids a
namespace collision with a standard Python module on the default path.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

__all__ = ['TprFile']

import gmx.core
from gmx.exceptions import UsageError

_current_dir = os.getcwd()

class TprFile:
    """Handle to a Gromacs simulation run input file.

    See :doc:`filetypes`
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
