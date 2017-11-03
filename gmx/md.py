"""
Molecular dynamics integrators and supporting classes
=====================================================
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import gmx

class MD(object):
    """
    Computation module for running molecular dynamics routines.

    Interacts with molecular data in a System container and with the workflow
    managed by a Runner to execute Gromacs molecular dynamics calculations.
        """
    def __init__(self, md):
        self._api_object = md


    @property
    def _api_object(self):
        return self.__api_object

    @_api_object.setter
    def _api_object(self, md):
        """
        Private attribute to hold reference to C++ API object.

        :param md: gmx.core.MD object
        :type md: gmx.core.MD
        """
        if not isinstance(md, gmx.core.MD):
            raise gmx.TypeError(md, gmx.core.MD)
        self.__api_object = md

class ExtendedMD(MD):
    """
    Computation module for running molecular dynamics routines.

    Interacts with molecular data in a System container and with the workflow
    managed by a Runner to execute Gromacs molecular dynamics calculations.

    Manages additional potentials provided by external extension code.
    """
    def __init__(self, md):
        super(ExtendedMD, self).__init__(md)
        self.__potential = None

    @property
    def potential(self):
        return self.__potential

    @potential.setter
    def potential(self, potential):
        # if not hasattr(potential, 'module'):
        #     raise gmx.UsageError("Object does not have a register() method")
        self.__potential = potential
        self._api_object.add_potential(potential)

    def add_potential(self, potential=None):
        """
        Add an element to the Hamiltonian not specified in the System topology.

        The argument should be a subclass of :obj:`gmx.core.MDModule` to provide the
        necessary high-level interface, and should be implemented as a C++ extension
        providing the appropriate library interfaces. (See developer docs.)

        Args:
            potential: instance of a class that will participate in energy and force evaluation.

        Note:
            Currently only one external potential can be managed.
        """
        self.potential = potential

def from_tpr(inputrecord=None):
    """Get a Molecular Dynamics handle from a TPR file.

    Args:
        inputrecord (str): path to input record on disk

    Returns:
        gmx.md.MD object
    """
    import gmx.core
    if not isinstance(inputrecord, str):
        raise gmx.exceptions.UsageError("Need a file name as a string.")
    md = MD(gmx.core.md_from_tpr(inputrecord))
    return md