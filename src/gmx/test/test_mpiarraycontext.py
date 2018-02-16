# Test 2-element work array. Run with ``mpiexec -n 2 python -m mpi4py thisfile.py``
# mpiexec -n 2 python -m mpi4py -m pytest -v -rs --pyargs gmx.test.test_mpiarraycontext

import unittest
import pytest

import gmx
import gmx.core
import os
# Get a test tpr filename
from gmx.data import tpr_filename

try:
    from mpi4py import MPI
    withmpi_only = pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() < 2,
                                      reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")

@withmpi_only
@pytest.mark.usefixtures("cleandir")
class ArrayContextTestCase(unittest.TestCase):
    def test_basic(self):
        md = gmx.workflow.from_tpr(tpr_filename)
        context = gmx.context.ParallelArrayContext(md)
        with context as session:
            session.run()

        md = gmx.workflow.from_tpr([tpr_filename, tpr_filename])
        context = gmx.context.ParallelArrayContext(md)
        with context as session:
            session.run()
            # This is a sloppy way to see if the current rank had work to do.
            if hasattr(context, "workdir"):
                rank = context.rank
                output_path = os.path.join(context.workdir, 'traj.trr')
                assert(os.path.exists(output_path))
                print("Worker {} produced {}".format(rank, output_path))
