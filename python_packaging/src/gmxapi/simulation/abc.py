#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019, by the GROMACS development team, led by
# Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# and including many others, as listed in the AUTHORS file in the
# top-level source directory and at http://www.gromacs.org.
#
# GROMACS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# GROMACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GROMACS; if not, see
# http://www.gnu.org/licenses, or write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
#
# If you want to redistribute modifications to GROMACS, please
# consider that scientific software is very special. Version
# control is crucial - bugs must be traceable. We will be happy to
# consider code for inclusion in the official distribution, but
# derived work must not be called official GROMACS. Details are found
# in the README & COPYING files - if they are missing, get the
# official version at http://www.gromacs.org.
#
# To help us fund GROMACS development, we humbly ask that you cite
# the research papers on the package. Check out http://www.gromacs.org.

"""
Abstract base classes for gmxapi.simulation module
==================================================

These classes allow static and dynamic type checking for gmxapi Python
interfaces. Some may be used as bases to inherit behaviors, but users should
not assume that a gmxapi object actually inherits from classes in this module.

For more information on the concept of abstract base classes in Python, refer
to https://docs.python.org/3/library/abc.html

For more on type hinting, see https://docs.python.org/3/library/typing.html
"""

import abc
from typing import Mapping

from gmxapi.typing import SourceTypeVar


class SimulationInput(abc.ABC):
    """Abstract class for acceptable input to operations in gmxapi.simulation.

    Acceptable simulation input includes:
        * TPR filename.
        * Output from read_tpr or modify_input.
        *
        * TODO: an acceptable collection of data sources.

    This class is intended for static and dynamic type checking, and to provide
    a documentation entry point for what is considered to be valid simulation
    input.

    No code should assume that input objects actually derive from this class.

    The output of ReadTpr and ModifyInput are examples of objects implementing
    SimulationInput compatible interfaces.
    """

    @property
    @abc.abstractmethod
    def parameters(self) -> Mapping[str, SourceTypeVar]:
        ...

    @classmethod
    def __subclasshook__(cls, subclass):
        if cls is SimulationInput:
            # TODO: We can do a better job of checking the basic type as well as the schema.
            has_parameters = any([hasattr(base, 'parameters')
                                  and getattr(base.parameters, '_dtype', None) is dict
                                  for base in subclass.__mro__])
            if all([has_parameters]):
                return True
            else:
                return False
        else:
            return NotImplemented


class ModuleObject(abc.ABC):
    """Extended interface for objects in the gmaxpi.simulation module.

    Implies availability of additional binding details.
    """
