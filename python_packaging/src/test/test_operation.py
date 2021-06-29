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

"""Tests the interfaces defined in operation.py and behavior of simple operations.

See also test_commandline.py for integration tests.
"""

import os
import shutil
import stat
import tempfile
import unittest

import pytest

import gmxapi as gmx
from gmxapi import commandline_operation
import gmxapi.exceptions as gmx_exceptions


class ImmediateResultTestCase(unittest.TestCase):
    """Test data model and data flow for basic operations."""

    def test_scalar(self):
        operation = gmx.make_constant(42)
        assert isinstance(operation.dtype, type)
        assert operation.dtype == int
        assert operation.result() == 42

    def test_list(self):
        list_a = [1, 2, 3]

        list_result = gmx.concatenate_lists(sublists=[list_a])
        assert list_result.dtype == gmx.datamodel.NDArray
        # Note: this is specifically for the built-in tuple type.
        # Equality comparison may work differently for different sequence types.
        assert tuple(list_result.result()) == tuple(list_a)
        assert len(list_result.result()) == len(list_a)

        list_result = gmx.concatenate_lists([list_a, list_a])
        assert len(list_result.result()) == len(list_a) * 2
        assert tuple(list_result.result()) == tuple(list_a + list_a)

        list_b = gmx.ndarray([42])

        list_result = gmx.concatenate_lists(sublists=[list_b])
        assert list_result.result()[0] == 42

        if gmx.version.has_feature('implicit_ndarray_from_iterable'):
            expected_exceptions = ()
        else:
            expected_exceptions = gmx_exceptions.TypeError
        with pytest.raises(expected_exception=expected_exceptions):
            list_result = gmx.join_arrays(front=list_a, back=list_b)
            assert len(list_result.result()) == len(list_a) + 1
            assert tuple(list_result.result()) == tuple(list(list_a) + [42])


class OperationPipelineTestCase(unittest.TestCase):
    """Test dependent sequence of operations."""

    def test_data_dependence(self):
        """Confirm that data dependencies correctly establish resolvable execution dependencies.

        In a sequence of two operations, write a two-line file one line at a time.
        Use the output of one operation as the input of another.
        """
        with tempfile.TemporaryDirectory() as directory:
            file1 = os.path.join(directory, 'input')
            file2 = os.path.join(directory, 'output')

            # Make a shell script that acts like the type of tool we are wrapping.
            scriptname = os.path.join(directory, 'clicommand.sh')
            with open(scriptname, 'w') as fh:
                fh.write('\n'.join(['#!' + shutil.which('bash'),
                                    '# Concatenate an input file and a string argument to an output file.',
                                    '# Mock a utility with the tested syntax.',
                                    '#     clicommand.sh "some words" -i inputfile -o outputfile',
                                    'echo $1 | cat $3 - > $5\n']))
            os.chmod(scriptname, stat.S_IRWXU)

            line1 = 'first line'
            filewriter1 = gmx.commandline_operation(scriptname,
                                                arguments=[line1],
                                                input_files={'-i': os.devnull},
                                                output_files={'-o': file1})

            line2 = 'second line'
            filewriter2 = gmx.commandline_operation(scriptname,
                                                arguments=[line2],
                                                input_files={'-i': filewriter1.output.file['-o']},
                                                output_files={'-o': file2})

            filewriter2.run()
            # Check that the files have the expected lines
            with open(file1, 'r') as fh:
                lines = [text.rstrip() for text in fh]
            assert len(lines) == 1
            assert lines[0] == line1
            with open(file2, 'r') as fh:
                lines = [text.rstrip() for text in fh]
            assert len(lines) == 2
            assert lines[0] == line1
            assert lines[1] == line2


# Define some simple operations to use with the following tests.
@gmx.function_wrapper(output={'data': int})
def _add_int(a: int, b: int):
    return a + b


@gmx.function_wrapper(output={'data': int})
def _sum_int_array(a: gmx.datamodel.NDArray):
    return sum(a.to_list())


class OperationTopologyTestCase(unittest.TestCase):
    """Test implicit and explicit data flow topology behaviors.

    Cases:
        Source may be scalar or NDArray, and may be constant, Future,
        or explicit EnsembleDataSource (the result of scatter()).
        Sink may be scalar or NDArray, may or may not already be an ensemble
        (having width > 1), or may require conversion to an ensemble (widening).
    """

    def test_scalar_to_scalar(self):
        # trivial
        one = 1
        two = 2
        three = 3
        op = _add_int(a=one, b=two)  # type: gmx.operation.AbstractOperation
        assert op.output.data.result() == three
        one = gmx.make_constant(1)
        two = gmx.make_constant(2)
        op = _add_int(a=one, b=two)  # type: gmx.operation.AbstractOperation
        assert op.output.data.result() == three

    def test_ensemble_scalar_to_scalar(self):
        # implicit broadcast: sink is already an ensemble
        ensemble_width = 2
        one = 1
        one_list = [one] * ensemble_width
        one_array = gmx.ndarray(one_list)
        one_ensemble = gmx.scatter(one_array)
        two = 2
        two_list = [two] * ensemble_width
        two_array = gmx.ndarray(two_list)
        two_ensemble = gmx.scatter(two_array)
        three = 3
        i = None

        # Iterable inputs
        if not gmx.version.has_feature('iterable_input_as_implicit_ensemble'):
            expected_exceptions = (gmx.exceptions.TypeError,)
        else:
            expected_exceptions = ()
        with pytest.raises(expected_exception=expected_exceptions):

            # Scatter from list
            op = _add_int(a=one_list, b=two)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one, b=two_list)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one_list, b=two_list)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1

            # Scatter from array
            op = _add_int(a=one_array, b=two)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one, b=two_array)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one_array, b=two_array)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1

        op = _add_int(a=one_ensemble, b=two)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual
        assert i == ensemble_width - 1
        op = _add_int(a=one, b=two_ensemble)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual
        assert i == ensemble_width - 1
        op = _add_int(a=one_ensemble, b=two_ensemble)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual
        assert i == ensemble_width - 1

        # Repeat the preceding test with future inputs constructed differently
        if not gmx.version.has_feature('dynamic_ensemble_topology'):
            expected_exceptions = (gmx.exceptions.ValueError,)
        else:
            expected_exceptions = ()
        with pytest.raises(expected_exception=expected_exceptions):
            one_array = gmx.operation.as_gmx_ndarray([1] * ensemble_width)
            one_ensemble = gmx.scatter(one_array)
            two_array = gmx.operation.as_gmx_ndarray([2] * ensemble_width)
            two_ensemble = gmx.scatter(two_array)

            op = _add_int(a=one_ensemble, b=two)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one, b=two_ensemble)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1
            op = _add_int(a=one_ensemble, b=two_ensemble)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1

    def test_scalar_to_NDArray(self):
        ensemble_width = 2
        one = gmx.make_constant(1)
        one_array = gmx.ndarray([1] * ensemble_width)

        # Implicit conversion.
        op = _sum_int_array(a=1)
        assert op.output.data.result() == 1

        # Also test Future[NDArray]
        # Implicit conversion.
        op = _sum_int_array(a=one)
        assert op.output.data.result() == 1
        # Explicit conversion.
        op = _sum_int_array(gmx.operation.as_gmx_ndarray(one))
        assert op.output.data.result() == 1

        # TODO: correct conversion in ensemble. E.g.:
        #op = _sum_int_array(gmx.scatter(one_array))

        # TODO: Clarify desired behavior.
        list_input = [1, 2]
        if gmx.version.has_feature('iterable_input_as_implicit_ensemble'):
            # List should be interpreted as ensemble input unless annotated as NDArray.
            op = _sum_int_array(a=list_input)  # type: gmx.operation.AbstractOperation
            assert op.output.ensemble_width == len(list_input)
            for expected, actual in zip(list_input, op.output.data.result()):
                assert expected == actual
        elif gmx.version.has_feature('implicit_ndarray_from_iterable'):
            # NDArray input binds to list input.
            op = _sum_int_array(a=list_input)  # type: gmx.operation.AbstractOperation
            assert op.output.ensemble_width == 1
            assert op.output.data.result() == sum(list_input)
        else:
            with pytest.raises(expected_exception=gmx_exceptions.TypeError):
                op = _sum_int_array(a=list_input)

    def test_NDArray_to_scalar(self):
        # Implicit scatter: requires widening
        ensemble_width = 2
        one_array = gmx.ndarray([1] * ensemble_width)
        two = 2
        three = 3
        i = None

        op = _add_int(a=one_array, b=two)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual
        assert i == ensemble_width - 1
        op = _add_int(a=two, b=one_array)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual
        assert i == ensemble_width - 1

        # Implicit scatter: Should map to an existing ensemble topology
        if not gmx.version.has_feature('iterable_input_as_implicit_ensemble'):
            expected_exceptions = (gmx.exceptions.TypeError,)
        else:
            expected_exceptions = ()
        with pytest.raises(expected_exception=expected_exceptions):
            ensemble_width = 2
            one_array = gmx.ndarray([1] * ensemble_width)
            two_array = [2] * ensemble_width
            three = 3
            i = None

            op = _add_int(a=one_array, b=two_array)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1

            op = _add_int(a=two_array, b=one_array)  # type: gmx.operation.AbstractOperation
            for i, check in enumerate(zip([three] * ensemble_width, op.output.data.result())):
                expected, actual = check
                assert expected == actual
            assert i == ensemble_width - 1

    def test_ensemble_NDArray_to_scalar(self):
        # Implies unsupported multidimensional ensemble
        ensemble_width = 2
        one_array = gmx.ndarray([1] * ensemble_width)
        two = 2

        with pytest.raises(expected_exception=gmx_exceptions.TypeError):
            _add_int(a=gmx.scatter([one_array, one_array]), b=two)

        ensemble_width = 2
        one_array = gmx.ndarray([1] * ensemble_width)
        two_array = [2] * ensemble_width

        with pytest.raises(expected_exception=gmx_exceptions.TypeError):
            _add_int(a=gmx.scatter([one_array, one_array]), b=two_array)

    def test_NDArray_to_NDArray(self):
        # trivial, but should be checked for logic errors.
        assert _sum_int_array(gmx.ndarray([1, 2])).output.data.result() == 3
        # Also test Future[NDArray]
        assert _sum_int_array(gmx.operation.as_gmx_ndarray([1,2])).output.data.result() == 3

    # TODO: Roadmap for this functionality.
    @pytest.mark.xfail(reason='Feature not implemented.')
    def test_ensemble_NDArray_to_NDArray(self):
        # existing ensemble or explicit scatter: requires widening
        ensemble_width = 2

        # implicit ensemble
        array_input = [gmx.ndarray([1, 2])] * ensemble_width
        op = _sum_int_array(array_input)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([3] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual

        # explicit scatter
        array_input = gmx.scatter(gmx.ndarray([1, 2]))
        op = _sum_int_array(array_input)  # type: gmx.operation.AbstractOperation
        for i, check in enumerate(zip([3] * ensemble_width, op.output.data.result())):
            expected, actual = check
            assert expected == actual

    def test_gather(self):
        # gather() should produce a non-ensemble NDArray Future of ensemble width 1
        # in all cases.
        # Cases: non-ensemble source from scalar or array
        # Cases: existing ensemble or explicit scatter
        ...
