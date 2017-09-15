"""Test gmx.md submodule"""

import unittest
import os

import gmx
import gmx.md
import gmx.core
from gmx.data import tpr_filename

class BindingsTestCase(unittest.TestCase):
    def test_MDProxy(self):
        pymd = gmx.core.md_from_tpr(tpr_filename)
        assert isinstance(pymd, gmx.core.MD)
        pymd = gmx.md.from_tpr(tpr_filename)
        assert isinstance(pymd._api_object, gmx.core.MD)
        assert isinstance(pymd._api_object, gmx.core.Module)
    def test_RunnerProxy(self):
        md = gmx.md.from_tpr(tpr_filename)
        runner = gmx.runner.SimpleRunner(md)
        assert str(md._api_object).startswith('MDStatePlaceholder')
        assert str(md._api_object).rstrip().endswith('topol.tpr"')
        assert str(runner.module._api_object) == str(md._api_object)
        # session = runner._runner.start()
        # assert isinstance(session, gmx.core.SimpleRunner)
        # assert isinstance(session.run(), gmx.core.Status)
        #assert isinstance(session.run(4), gmx.core.Status)
    def test_APIObjectsFromTpr(self):
        apisystem = gmx.core.from_tpr(tpr_filename)
        assert isinstance(apisystem, gmx.core.MDSystem)
        assert hasattr(apisystem, 'runner')
        apirunner = apisystem.runner
        assert isinstance(apirunner, gmx.core.SimpleRunner)
        assert hasattr(apirunner, 'start')
        assert hasattr(apirunner, 'run')
        session = apirunner.start()
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