# Test 2-element work array. Run with ``mpiexec -n 2 python -m mpi4py thisfile.py``
import unittest
import pytest

import gmx
import gmx.core
import os
# Get a test tpr filename
from gmx.data import tpr_filename

try:
    from mpi4py import MPI
    withmpi_only = pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() >= 2,
                                      reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")

# \todo disable test if not run with MPI.
@withmpi_only
class MpiArrayContextTestCase(unittest.TestCase):
    def test_basic(self):
        from mpi4py import MPI
        if not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() != 2:
            return
        work = gmx.core.from_tpr(tpr_filename)
        context = gmx.context.MpiArrayContext([work, work])
        with context as session:
            session.run()
            rank = context.rank
            output_path = os.path.join(context.workdir_list[rank], 'traj.trr')
            assert(os.path.exists(output_path))
            print("Worker {} produced {}".format(rank, output_path))
