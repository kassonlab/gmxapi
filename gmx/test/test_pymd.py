"""Test gmx.md submodule"""

import unittest
import os

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
        session = runner._runner.start()
        assert isinstance(session, gmx.core.SimpleRunner)
        assert isinstance(session.run(), gmx.core.Status)
        assert isinstance(session.run(4), gmx.core.Status)
