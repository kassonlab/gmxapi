#!/usr/bin/env python
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

"""Test data types and containers for interfaces, conversions, and flow."""

import unittest
import typing

import gmxapi as gmx
import pytest
from gmxapi import exceptions


class NDArrayTestCase(unittest.TestCase):
    """Test handling of N-dimensional array data."""

    @pytest.mark.xfail
    def test_input_checks(self):
        """Require valid inputs."""
        with pytest.raises(exceptions.ValueError):
            # No default initialization.
            gmx.ndarray()
        with pytest.raises(exceptions.TypeError):
            # data types are incompatible
            gmx.ndarray([1, 2, 'a'])
        with pytest.raises(exceptions.TypeError):
            # Data type is ambiguous
            gmx.ndarray([1, 2, 3.0])

    @pytest.mark.xfail
    def test_initialization(self):
        # Initialize from list or tuple. Either requires a copy.
        list_a = [1, 2, 3]
        array_a = gmx.ndarray(list_a)
        assert array_a.dtype == int
        # assert len(array_a) == len(list_a)
        assert not isinstance(array_a, typing.Iterable)

        list_result = gmx.operation.concatenate_lists([array_a, array_a])
        assert len(list_result.result()) == len(list_a) * 2
        assert tuple(list_result.result()) == tuple(list_a + list_a)

        # Initialize from memoryview, array.array, or numpy.ndarray without copy.
        assert False
        # Initialize by broadcasting data into the specified shape.
        assert False

    @pytest.mark.xfail
    def test_interface(self):
        # Should be iterable
        assert False
        # Should have sequence container behavior (index and slice)
        assert False

        assert True

    @pytest.mark.xfail
    def test_simple_conversions(self):
        # NDArray should be trivially convertible to list, tuple, or set.
        assert False

        # NDArray should be trivially convertible to memoryview (via the buffer interface).
        assert False

        # NDArray should be trivially convertible to numpy.ndarray,
        # but check that it can be done without copies.
        assert False

        # Test some round-trip conversions.
        assert False

        assert True


class AssociativeMapTestCase(unittest.TestCase):
    """Test Map data objects."""


class HierarchicalDataTestCase(unittest.TestCase):
    """Test aggregates of gmxapi data and proxies."""

    @pytest.mark.xfail
    def test_hierarchical_data(self):
        # Map of multiple scalar types
        assert False

        # Map containing NDArray
        assert False

        assert True

    @pytest.mark.xfail
    def test_futures(self):
        # NDArray Future
        assert False

        # Map Future
        assert False

        assert True


if __name__ == '__main__':
    unittest.main()
