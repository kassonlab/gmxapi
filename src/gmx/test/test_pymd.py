"""Test gmx.md submodule"""

# We are generally using py.test so simpler assert statements just work.

# Question: can/should pytest handle MPI jobs? How should we test features that only make sense in MPI?
# I'm increasingly thinking that the CMake-managed C++ extension module should be managed separately than the setuptools
# primary module. Then we can just do standard things like using CTest and googletest for the more complicated stuff.

import unittest
import pytest
import os

import gmx
import gmx.core
from gmx.data import tpr_filename

try:
    from mpi4py import MPI
    withmpi_only = pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() < 2,
                                      reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")

@pytest.mark.skip(reason="updating Context handling...")
@pytest.mark.usefixtures("cleandir")
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

@pytest.mark.usefixtures("cleandir")
class WorkSpecTestCase(unittest.TestCase):
    def test_simpleSimulation(self):
        """Load a work specification with a single TPR file and run."""
        # use case 1: simple high-level
        md = gmx.workflow.from_tpr(tpr_filename)
        gmx.run(md)

    @withmpi_only
    def test_array_context(self):
        md = gmx.workflow.from_tpr(tpr_filename)
        context = gmx.context.ParallelArrayContext(md)
        with context as session:
            session.run()

