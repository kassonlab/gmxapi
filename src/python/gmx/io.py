# provide the high-level interface to the trajectory module in the gmx package.

# TODO: fix namespace polution
import gmx.core

class TrajectoryFile:
    """
    Provides an interface to Gromacs supported trajectory file formats.

    If the file mode is 'r', the object created supports the Python iterator
    protocol for reading one frame at a time.

    Other file modes are not yet supported.
    """

    READ = 1

    def __init__(self, filename, mode=None):
        """ Prepare filename for the requested mode of access.
        """
        if mode == 'r':
            self.mode = TrajectoryFile.READ
            self.filename = filename
            self._cpp_module = gmx.core.CachingTafModule()
        #elif mode == 'w':
        #    self.mode = TrajectoryFile.WRITE
        else:
            raise ValueError("Trajectory file access mode not supported.")

    def select(self, selection=None):
        """ Generator to read atom positions frame-by-frame.

        An analysis module runner is implicitly created when the iterator
        is returned and destroyed when the iterator raises StopIteration.

        Args:
            selection: atom selection to retrieve from trajectory file

        Returns:
            iterator to frames
        """
        #assert(isinstance(selection, gmx.core.Selection))

        # Create runner and bind module
        runner = gmx.core.TafRunner(self._cpp_module)

        # Create options object with which to initialize runner
        #options = gmx.core.Options(filename=self.filename)
        options = gmx.core.Options()

        # Initialize runner and module
        runner.initialize(options)
        while runner.next():
            frame = self._cpp_module.frame()
            yield frame
