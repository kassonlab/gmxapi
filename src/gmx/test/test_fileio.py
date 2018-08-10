"""Test gmx.fileio submodule"""
import os
import tempfile
import unittest

import gmx.core
from gmx.fileio import TprFile
from gmx.exceptions import UsageError

from gmx.data import tpr_filename

class TprTestCase(unittest.TestCase):
    def test_tprfile_read(self):
        self.assertRaises(UsageError, TprFile)
        self.assertRaises(UsageError, TprFile, tpr_filename, 'x')
        # TprFile does not yet check whether file exists and is readable...
        #self.assertRaises(UsageError, TprFile, 1, 'r')
        tprfile = TprFile(tpr_filename, 'r')
        with tprfile.extract() as fh:
            pass

class TprCoreTestCase(unittest.TestCase):
    def test_gmxapiTprFile(self):
        import gmx.core
        api_object = gmx.core.TprFile(self.filename, mode='r')
        with api_object as handle:
            pass

    def test_tprcopy(self):
        _, temp_filename = tempfile.mkstemp(suffix='.tpr')
        # When we have some more inspection tools we can do more than just check for success.
        assert gmx.core.copy_tprfile(source=tpr_filename, destination=temp_filename, end_time=1.0)
        os.unlink(temp_filename)


    def test_tprcopy(self):
        _, temp_filename = tempfile.mkstemp(suffix='.tpr')
        # When we have some more inspection tools we can do more than just check for success.
        assert gmx.core.copy_tprfile(source=tpr_filename, destination=temp_filename, end_time=1.0)
        os.unlink(temp_filename)


if __name__ == '__main__':
    unittest.main()
