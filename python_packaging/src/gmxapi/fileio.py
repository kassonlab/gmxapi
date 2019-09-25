"""Provide the high-level interface to the file i/o behaviors in the package.

The submodule name may seem longer than necessary, but avoids a
namespace collision with a standard Python module on the default path.
"""

__all__ = ['TprFile', 'read_tpr', 'write_tpr_file']

import os

from gmxapi import exceptions
from gmxapi import _gmxapi

_current_dir = os.getcwd()


class TprFile:
    """Handle to a Gromacs simulation run input file.
    """

    def __init__(self, filename: str = None, mode: str = 'r'):
        """Open a TPR file.

        File access mode is indicated by 'r' for read-only access.

        Args:
            filename (str): Path to a run input file (e.g. 'myfile.tpr')
            mode (str): File access mode.

        Note:
            Currently, TPR files are read-only from the Python interface.

        Example:

            >>> import gmxapi as gmx
            >>> filehandle = gmx.TprFile(filename, 'r')

        """
        if filename is None:
            raise exceptions.UsageError("TprFile objects must be associated with a file.")
        if mode == 'r':
            self.mode = 'r'
        if mode != 'r':
            raise exceptions.UsageError("TPR files only support read-only access.")
        self.filename = filename
        self._tprFileHandle = None

    def close(self):
        # self._tprFileHandle.close()
        self._tprFileHandle = None

    def __repr__(self):
        return "gmx.fileio.TprFile('{}', '{}')".format(self.filename, self.mode)

    def __enter__(self):
        self._tprFileHandle = _gmxapi.read_tprfile(self.filename)
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
        raise exceptions.ApiError("property not implemented.")

    @property
    def topology(self):
        raise exceptions.ApiError("property not implemented.")

    @property
    def state(self):
        raise exceptions.ApiError("property not implemented.")


class _SimulationInput(object):
    """
    Simulation input interface for a TPR file read by gmx.fileio.read_tpr()

    Attributes:
        parameters: Simulation parameters for (re)written TPR file.
        structure: Atomic details (not yet implemented)
        topology: Molecular force field details (not yet implemented)
        state: Simulation state information (not yet implemented)

    """

    def __init__(self, tprfile: str = None):
        if not isinstance(tprfile, TprFile):
            try:
                tprfile = TprFile(tprfile)
            except Exception:
                # This class is an implementation detail of TPR file I/O...
                raise exceptions.ApiError("Must be initialized from a gmx.fileio.TprFile object.")
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
        raise exceptions.ApiError("property not implemented.")

    @property
    def topology(self):
        raise exceptions.ApiError("property not implemented.")

    @property
    def state(self):
        raise exceptions.ApiError("property not implemented.")


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
            tprfile = TprFile(os.fsencode(tprfile), mode='r')
        except Exception:
            tprfile = None
    if tprfile is None:
        raise exceptions.UsageError("TPR object or file name is required.")

    return _SimulationInput(tprfile)


# In initial implementation, we extract the entire TPR file contents through the
# TPR-backed GmxMdParams implementation.
# Note: this function is not consistent with a gmxapi operation.
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

    if not isinstance(parameters, _gmxapi.SimulationParameters):
        raise exceptions.TypeError(
            "You must provide a gmx.core.SimulationParameters object to `parameters` as input.")
    _gmxapi.write_tprfile(output, parameters)
