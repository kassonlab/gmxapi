"""Test gmx.md submodule"""

# We are generally using py.test so simpler assert statements just work.

# Question: can/should pytest handle MPI jobs? How should we test features that only make sense in MPI?
# I'm increasingly thinking that the CMake-managed C++ extension module should be managed separately than the setuptools
# primary module. Then we can just do standard things like using CTest and googletest for the more complicated stuff.

import unittest
import os

import gmx
import gmx.core
from gmx.data import tpr_filename

class BindingsTestCase(unittest.TestCase):
    def test_APIObjectsFromTpr(self):
        apisystem = gmx.core.from_tpr(tpr_filename)
        assert isinstance(apisystem, gmx.core.MDSystem)
        assert hasattr(apisystem, 'launch')
        session = apisystem.launch()
        assert hasattr(session, 'run')
        session.run()
        # Test rerunability
        # system = gmx.System()
        # runner = gmx.runner.SimpleRunner()
        # runner._runner = apirunner
        # system.runner = runner
        # assert isinstance(system, gmx.System)
        # assert isinstance(system.runner, gmx.runner.Runner)
        # assert isinstance(system.runner._runner, gmx.core.SimpleRunner)
        # with gmx.context.DefaultContext(system.runner) as session:
        #     session.run()
    def test_SystemFromTpr(self):
        system = gmx.System._from_file(tpr_filename)
        system.run()
    def test_Extension(self):
        import pytest
        # Test attachment of external code
        system = gmx.System._from_file(tpr_filename)
        potential = gmx.core.TestModule()
        assert isinstance(potential, gmx.core.MDModule)
        system.add_potential(potential)

        assert hasattr(potential, "bind")
        generic_object = object()
        with pytest.raises(Exception) as exc_info:
            potential.bind(generic_object)
        assert str(exc_info).endswith("MDModule bind method requires properly named PyCapsule input.")

        with gmx.context.DefaultContext(system.workflow) as session:
            session.run()
