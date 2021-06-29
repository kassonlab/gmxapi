#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019,2020, by the GROMACS development team, led by
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

"""gmxapi data types and interfaces.

The data types defined here are Abstract Base Classes (ABCs) in the styles of
the collections.abc and typing modules. They can be used to validate interfaces
or data compatibility with isinstance() and issubclass() checks, even for types
that don't explicitly inherit from the ABCs.

The ABCs can be used as base classes for concrete types, but
code should not assume that gmxapi data objects actually derive from these
base classes. In fact, gmxapi data objects will generally be C (or C++) objects
accompanied by C struct descriptors. ABI compatibility relies on these C structs
and the accompanying Python Capsule schema.

Note: In the senses above, Python "abstract base class" has a different meaning than in C++.

TODO: Placeholders
Input Placeholders.
An operation factory can advertise allowed inputs by name, shape, and type, as
well as advertising flexibility. Named inputs may be optional. Number of dimensions
is fixed, but the size in a given dimension may be fixed or flexible. A named
input may have flexible type. Once a data edge and terminal operation are
instantiated, though, the output of the Operation is well defined.

Need a way to represent Type placeholders for Operation inputs in InputCollectionDescription
and factory declarations.

Need a way to express input data shape with magic integer placeholders.

File placeholder: Input and output files have constraints on their filename suffixes,
but should otherwise be left abstract until data connections are made. This is a
special case of a string Future when we are dealing with files by name only.
"""

__all__ = ['ndarray', 'NDArray']

import collections

import gmxapi.abc
from gmxapi import exceptions


class NDArray(gmxapi.abc.NDArray):
    """N-Dimensional array type.
    """

    def __init__(self, data=None):
        self._values = []
        self.dtype = None
        self.shape = ()
        if data is not None:
            if hasattr(data, 'result') or (
                    isinstance(data, collections.abc.Iterable) and any([hasattr(item, 'result') for item in data])):
                raise exceptions.ValueError(
                    'Make a Future of type NDArray instead of NDArray of type Future, or call result() first.')
            if isinstance(data, (str, bytes)):
                data = [str(data)]
                self.dtype = str
                length = 1
            else:
                try:
                    length = len(data)
                except TypeError:
                    # data is a scalar
                    length = 1
                    self.dtype = type(data)
                    data = [data]
            assert isinstance(data, collections.abc.Iterable) and isinstance(data, collections.abc.Sized)
            for element in data:
                if self.dtype is None:
                    dtype = type(element)
                    if dtype is type(None):
                        raise exceptions.TypeError('NDArray cannot hold NoneType.')
                    self.dtype = dtype
                else:
                    if not isinstance(element, self.dtype):
                        raise exceptions.ValueError('Array elements must be of the same type.')
            self._values = [self.dtype(value) for value in data]
            if length > 0:
                self.shape = (length,)
            # TODO: stronger typing.
            #  Since we are deducing type, we don't know the type of a zero-length input.
            # assert self.dtype is not None
            # assert self.dtype is not type(None)
            # if not issubclass(self.dtype, valid_source_types):
            #     raise exceptions.TypeError('NDArray dtype must be one of {}'.format(valid_source_types))
        if isinstance(self._values, NDArray) or isinstance(self.dtype, type) and issubclass(self.dtype, NDArray):
            # TODO: Migrate to a proper C++ based shaped-data structure.
            raise exceptions.NotImplementedError(
                'Implicit conversion to higher dimensional arrays not yet supported.')

    def to_list(self):
        return self._values

    def __getitem__(self, i: int):
        return self._values[i]

    def __len__(self) -> int:
        return len(self._values)


def ndarray(data=None, shape=None, dtype=None):
    """Create an NDArray object from the provided iterable.

    Arguments:
        data: object supporting sequence, buffer, or Array Interface protocol

    ..  versionadded:: 0.1
        *shape* and *dtype* parameters

    If ``data`` is provided, ``shape`` and ``dtype`` are optional. If ``data`` is not
    provided, both ``shape`` and ``dtype`` are required.

    If ``data`` is provided and shape is provided, ``data`` must be compatible with
    or convertible to ``shape``. See Broadcast Rules in `datamodel` documentation.

    If ``data`` is provided and ``dtype`` is not provided, data type is inferred
    as the narrowest scalar type necessary to hold any element in ``data``.
    ``dtype``, whether inferred or explicit, must be compatible with all elements
    of ``data``.

    The returned object implements the gmxapi N-dimensional Array Interface.
    """
    if data is None:
        array = NDArray()
    else:
        if isinstance(data, NDArray):
            return data
        if isinstance(data, (str, bytes)):
            data = (data,)
        # data is not None, but may still be an empty sequence.
        length = 0
        try:
            length = len(data)
        except TypeError:
            # data is a scalar
            length = 1
            data = [data]
        array = NDArray(data)
    return array
