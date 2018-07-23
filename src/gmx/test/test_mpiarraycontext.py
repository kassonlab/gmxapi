# Test 2-element work array. Run with ``mpiexec -n 2 python -m mpi4py thisfile.py``
# mpiexec -n 2 python -m mpi4py -m pytest -v -rs --pyargs gmx.test.test_mpiarraycontext

import unittest
import pytest

import logging
logging.getLogger().setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logging.getLogger().addHandler(ch)

import gmx
import gmx.core
import os
# Get a test tpr filename
from gmx.data import tpr_filename

try:
    from mpi4py import MPI
    withmpi_only =\
        pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() < 2,
                           reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")

# Unused.
# Reference https://github.com/kassonlab/gmxapi/issues/36
# class ConsumerElement(gmx.workflow.WorkElement):
#     """Simple workflow element to test the shared data resource."""
#     def __init__(self, name):
#         gmx.workflow.WorkElement.__init__(self, namespace="testing",
#                                         operation="test_data")
#         self.name = name
#
# def translate_test_consumer(element):
#     """Translate the ConsumerElement into Session resources."""
#     width = element.params['width']
#     logging.debug("Translating test_consumer of width {}".format(width))
#     builder = ConsumerBuilder(element.name, width)
#     return builder
#
# class ConsumerBuilder(object):
#     """Implement the DAG builder interface for TestConsumer."""
#     def __init__(self, name, width):
#         self.input_nodes = []
#         self.shared_data_updater = None
#         self.name = name
#         self.width = width
#         logging.info("Created ConsumerBuilder named {}".format(self.name))
#
#     def add_subscriber(self, builder):
#         """We don't accept any subscribers."""
#         pass
#
#     def build(self, dag):
#         """Configure the work graph.
#
#         When this build() is called, the shared data has already been built, which means we have received
#         the data node into self.input_nodes[], but no actualy numpy array yet.
#         """
#         import numpy
#
#         assert len(self.input_nodes) > 0
#         nodename = self.name
#         self.node = dag.add_node(nodename)
#         for name in self.input_nodes:
#             dag.add_edge(name, nodename)
#
#         width = self.width
#         if 'width' in dag.graph:
#             width = max(width, dag.graph['width'])
#         dag.graph['width'] = width
#
#         logging.info("Added node {} with width {}".format(nodename, width))
#
#         def launch_test_consumer(rank=None):
#             """Implement the DAG session interface for TestConsumer.
#
#             The data node has already been launched, so we have been provided with a numpy array into self.shared_data,
#             and a handle to the preconfigured update method into self.shared_data_updater.
#             """
#             assert len(self.input_nodes) == 1
#             # Get resources from shared data node
#             single_input_edge = list(dag.in_edges(nodename))[0]
#             assert isinstance(single_input_edge, tuple)
#             data_node_name = single_input_edge[0]
#             data_node = dag.nodes[data_node_name]
#
#             data = data_node['data']
#
#             logging.info("Launching {} on rank {}.".format(self.name, rank))
#             # This is just a hack for testing. We should discourage this sort of direct manipulation of resources.
#             if rank < self.width:
#                 data[...] = rank + 1
#
#                 comm = data_node['comm']
#                 size = self.width
#                 assert rank == comm.Get_rank()
#
#                 # Let's do this simply first.
#
#                 # Gather remote array copies
#                 sendbuf = data
#                 recvbuf = None
#                 # Dimensions have an additional first dimension that is the width of the ensemble
#                 recv_dims = [size] + list(data.shape)
#                 if rank == 0:
#                     recvbuf = numpy.empty(recv_dims, dtype=data.dtype)
#                 if rank == 0:
#                     logging.info("Gathering data of shape {}".format(recv_dims))
#                 else:
#                     logging.info("Receiving broadcast data of shape {}.".format(data.shape))
#                 comm.Gather(sendbuf, recvbuf, root=0)
#                 if rank == 0:
#                     data[...] = recvbuf.sum(axis=0)
#
#                 # Broadcast results of reduction
#                 if rank == 0:
#                     logging.info("Broadcasting data of shape {}.".format(data.shape))
#                 else:
#                     logging.info("Receiving broadcast of shape {}.".format(data.shape))
#
#                 comm.Bcast(data, root=0)
#
#                 # Test the distributed array update.
#                 dag.nodes[nodename]['check'] = numpy.all(data == numpy.arange(1, size+1).sum())
#                 assert numpy.all(dag.nodes[nodename]['check'])
#
#             # Do we need to run after this?
#             return None
#
#         dag.nodes[nodename]['launch'] = launch_test_consumer

@withmpi_only
@pytest.mark.usefixtures("cleandir")
class ArrayContextTestCase(unittest.TestCase):
    def test_basic(self):
        md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
        context = gmx.context.ParallelArrayContext(md)
        with context as session:
            session.run()

        md = gmx.workflow.from_tpr([tpr_filename, tpr_filename], threads_per_rank=1)
        context = gmx.context.ParallelArrayContext(md)
        with context as session:
            session.run()
            # This is a sloppy way to see if the current rank had work to do.
            if hasattr(context, "workdir"):
                rank = context.rank
                output_path = os.path.join(context.workdir, 'traj.trr')
                assert(os.path.exists(output_path))
                print("Worker {} produced {}".format(rank, output_path))

    # Unused.
    # Reference https://github.com/kassonlab/gmxapi/issues/36
    # def test_shared_data(self):
    #     """Test that a shared data facility can be used across an ensemble."""
    #
    #     # constructor arguments for numpy.empty()
    #     args = [(10,3)]
    #     kwargs = {'dtype': 'int'}
    #
    #     data = gmx.workflow.SharedDataElement({'args': args, 'kwargs': kwargs}, name='mydata')
    #
    #     # Make a consumer of width 3, which we expect to be too big since we typically test on 2 ranks.
    #     width = 3
    #     consumer = ConsumerElement('mytester')
    #     consumer.depends = [data.name]
    #     consumer.params['width'] = width
    #
    #     workspec = gmx.workflow.WorkSpec()
    #     workspec.add_element(data)
    #     workspec.add_element(consumer)
    #
    #     context = gmx.context.ParallelArrayContext()
    #     context.add_operation(consumer.namespace, consumer.operation, translate_test_consumer)
    #     context.work = workspec
    #
    #     # Confirm that oversized width is caught
    #     import mpi4py
    #     size = mpi4py.MPI.COMM_WORLD.Get_size()
    #     if size < width:
    #         with pytest.raises(gmx.exceptions.UsageError):
    #             context.__enter__()
    #
    #     # Create a workspec that we expect to be runnable.
    #     consumer.workspec = None
    #     data.workspec = None
    #     width = size
    #     consumer.params['width'] = width
    #     workspec = gmx.workflow.WorkSpec()
    #     workspec.add_element(data)
    #     workspec.add_element(consumer)
    #     context = gmx.context.ParallelArrayContext()
    #     context.add_operation(consumer.namespace, consumer.operation, translate_test_consumer)
    #     context.work = workspec
    #
    #     with context as session:
    #         session.run()
    #         assert session.graph.nodes[consumer.name]['check'] == True
