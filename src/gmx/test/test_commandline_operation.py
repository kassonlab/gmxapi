# Test CLI-wrapping operation.

import unittest
import pytest

import gmx

class CommandLineOperationTestCase(unittest.TestCase):
    """Test creation and execution of command line wrapper."""
    def test_true(self):
        operation = gmx.commandline_operation(executable='true')
        assert not 'stdout' in operation.output
        assert not 'stderr' in operation.output
        assert not 'returncode' in operation.output
        # assert not hasattr(operation.output, 'stdout')
        # assert not hasattr(operation.output, 'stderr')
        # assert not hasattr(operation.output, 'returncode')
        success = operation()
        assert success
        assert not 'stdout' in operation.output
        assert not 'stderr' in operation.output
        # assert not hasattr(operation.output, 'stdout')
        # assert not hasattr(operation.output, 'stderr')
        # assert operation.output.returncode == 0
        assert operation.output['returncode'] == 0

    def test_false(self):
        operation = gmx.commandline_operation(executable='false')
        assert not 'stdout' in operation.output
        assert not 'stderr' in operation.output
        assert not 'returncode' in operation.output
        # assert not hasattr(operation.output, 'stdout')
        # assert not hasattr(operation.output, 'stderr')
        # assert not hasattr(operation.output, 'returncode')
        success = operation()
        assert not success
        assert not 'stdout' in operation.output
        assert not 'stderr' in operation.output
        # assert not hasattr(operation.output, 'stdout')
        # assert not hasattr(operation.output, 'stderr')
        # assert operation.output.returncode == 0
        assert operation.output['returncode'] == 1

    def test_echo(self):
        operation = gmx.commandline_operation(executable='echo', arguments=['hi there'])
        success = operation()
        assert success
        assert not 'stdout' in operation.output
        assert not 'stderr' in operation.output
        # assert not hasattr(operation.output, 'stdout')
        # assert not hasattr(operation.output, 'stderr')
        # assert operation.output.returncode == 0
        assert operation.output['returncode'] == 0
