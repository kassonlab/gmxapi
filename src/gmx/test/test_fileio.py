"""Test gmx.fileio submodule"""
import os
import tempfile
import unittest

import gmx.core
from gmx.fileio import TprFile
from gmx.fileio import read_tpr
from gmx.exceptions import UsageError

from gmx.data import tpr_filename

class TprTestCase(unittest.TestCase):
    def test_tprfile_read(self):
        self.assertRaises(UsageError, TprFile)
        self.assertRaises(UsageError, TprFile, tpr_filename, 'x')
        # TprFile does not yet check whether file exists and is readable...
        #self.assertRaises(UsageError, TprFile, 1, 'r')
        tprfile = TprFile(tpr_filename, 'r')
        with tprfile as fh:
            cpp_object = fh._tprFileHandle
            assert not cpp_object is None
            params = cpp_object.params().extract()
            assert "nsteps" in params
            assert not "foo" in params

    def test_core_tprcopy_alt(self):
        """Test gmx.core.copy_tprfile() for update of end_time.

        Set a new end time that is 5000 steps later than the original. Read dt
        from file to avoid floating point round-off errors.

        Transitively test gmx.fileio.read_tpr()
        """
        additional_steps = 5000
        sim_input = read_tpr(tpr_filename)
        params = sim_input.parameters.extract()
        dt = params['dt']
        nsteps = params['nsteps']
        init_step = params['init-step']
        initial_endtime = (init_step + nsteps) * dt
        new_endtime = initial_endtime + additional_steps*dt
        _, temp_filename = tempfile.mkstemp(suffix='.tpr')
        gmx.core.copy_tprfile(source=tpr_filename, destination=temp_filename, end_time=new_endtime)
        tprfile = TprFile(temp_filename, 'r')
        with tprfile as fh:
            params = read_tpr(fh).parameters.extract()
            dt = params['dt']
            nsteps = params['nsteps']
            init_step = params['init-step']
            assert (init_step + nsteps) * dt == new_endtime

        os.unlink(temp_filename)

    def test_write_tpr_file(self):
        """Test gmx.fileio.write_tpr_file() using gmx.core API.
        """
        additional_steps = 5000
        sim_input = read_tpr(tpr_filename)
        params = sim_input.parameters.extract()
        nsteps = params['nsteps']
        init_step = params['init-step']
        new_nsteps = init_step + additional_steps

        sim_input.parameters.set('nsteps', new_nsteps)

        _, temp_filename = tempfile.mkstemp(suffix='.tpr')
        gmx.fileio.write_tpr_file(temp_filename, input=sim_input)
        tprfile = TprFile(temp_filename, 'r')
        with tprfile as fh:
            params = read_tpr(fh).parameters.extract()
            dt = params['dt']
            assert params['nsteps'] != nsteps
            assert params['nsteps'] == new_nsteps

        os.unlink(temp_filename)

if __name__ == '__main__':
    unittest.main()
