"""Test gmx.md submodule"""

# We are generally using py.test so simpler assert statements just work.

# Question: can/should pytest handle MPI jobs? How should we test features that only make sense in MPI?
# I'm increasingly thinking that the CMake-managed C++ extension module should be managed separately than the setuptools
# primary module. Then we can just do standard things like using CTest and googletest for the more complicated stuff.

import warnings
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

import unittest
import pytest

import gmx
import gmx.core
from gmx.data import tpr_filename

try:
    from mpi4py import MPI
    withmpi_only = \
        pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() < 2,
                           reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")


# Set up an API-conformant plugin.
# Usually, the Context must be able to import a module and call a function that accepts the gmx.workflow.WorkElement
# to return a builder.
# In this case, we will add a function to the operations map before adding the work to the Context.
# The builder must provide an `add_subscriber(other_builder)` method and a `build(dag)` method.
# When another builder calls `add_subscriber()`, this builder should add a potential to the calling builder.
# The `build(dag)` method optionally updates the dag with node(s) / edge(s).
def my_plugin(element):
    """Using this test module as a work element module, provide a gmx.core.TestModule for execution."""
    class Builder(object):
        def __init__(self, element):
            self.name = element.name
            self.subscribers = []
        def add_subscriber(self, builder):
            self.subscribers.append(builder)
        def build(self, dag):
            # Create and pass the object now and don't bother creating a DAG node.
            potential = gmx.core.TestModule()
            for md in self.subscribers:
                md.potential.append(potential)
            # We are not adding nodes to the graph and are not contributing any launchers
            # launcher = None

    builder = Builder(element)
    return builder

@pytest.mark.usefixtures("cleandir")
class BindingsTestCase(unittest.TestCase):
    def test_APIObjectsFromTpr(self):
        apisystem = gmx.core.from_tpr(tpr_filename)
        assert isinstance(apisystem, gmx.core.MDSystem)
        context = gmx.core.Context()
        mdargs = gmx.core.MDArgs()
        mdargs.set({'threads_per_rank': 1})
        context.setMDArgs(mdargs)
        assert hasattr(apisystem, 'launch')
        session = apisystem.launch(context)
        assert hasattr(session, 'run')
        session.run()

# Ignore deprecation warning from networkx...
@pytest.mark.usefixtures("cleandir")
@pytest.mark.filterwarnings("ignore:Using or importing the ABCs from 'collections'")
@pytest.mark.usefixtures("caplog")
def test_simpleSimulation(caplog):
    """Load a work specification with a single TPR file and run."""
    # use case 1: simple high-level
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
    gmx.run(md)

@pytest.mark.usefixtures("cleandir")
@pytest.mark.filterwarnings("ignore:Using or importing the ABCs from 'collections'")
@pytest.mark.usefixtures("caplog")
def test_idempotence1(caplog):
    """Confirm that a work graph can be run repeatedly, even after completed.

    Use gmx.run and avoid extra references held by user code.
    """
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
    gmx.run(md)
    gmx.run(md)
    gmx.run(md)
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
    gmx.run(md)
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
    gmx.run(md)

@pytest.mark.usefixtures("cleandir")
@pytest.mark.filterwarnings("ignore:Using or importing the ABCs from 'collections'")
@pytest.mark.usefixtures("caplog")
def test_idempotence2(caplog):
    """Confirm that a work graph can be run repeatedly, even after completed.

    Interact with Context more directly.
    Check that more unpredictable references held by user are still safe.
    """
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)
    with gmx.get_context(md) as session:
        session.run()

    context = gmx.get_context(md)
    with context as session:
        session.run()

    context = gmx.context.Context()
    context.work = md
    with context as session:
        session.run()

@pytest.mark.usefixtures("cleandir")
def test_modifiedInput(caplog):
    """Load a work specification with a single TPR file and updated params."""
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1, end_time='0.02')
    context = gmx.get_context(md)
    with context as session:
        session.run()
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1, end_time='0.03')
    context.work = md
    with context as session:
        session.run()
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1, end_time='0.04')
    gmx.run(md)

@pytest.mark.usefixtures("cleandir")
@pytest.mark.usefixtures("caplog")
@withmpi_only
def test_plugin_no_ensemble(caplog):
    # Test attachment of external code
    md = gmx.workflow.from_tpr(tpr_filename, threads_per_rank=1)

    # Create a WorkElement for the potential
    #potential = gmx.core.TestModule()
    potential_element = gmx.workflow.WorkElement(namespace="testing", operation="create_test")
    potential_element.name = "test_module"
    before = md.workspec.elements[md.name]
    md.add_dependency(potential_element)
    assert potential_element.name in md.workspec.elements
    assert potential_element.workspec is md.workspec
    after = md.workspec.elements[md.name]
    assert not before is after

    # Workaround for https://github.com/kassonlab/gmxapi/issues/42
    # We can't add an operation to a context that doesn't exist yet, but we can't
    # add a work graph with an operation that is not defined in a context.
    context = gmx.get_context()
    context.add_operation(potential_element.namespace, potential_element.operation, my_plugin)
    context.work = md

    with warnings.catch_warnings():
        # Swallow warning about wide MPI context
        warnings.simplefilter("ignore")
        with context as session:
            if context.rank == 0:
                print(context.work)
            session.run()


@pytest.mark.usefixtures("cleandir")
@pytest.mark.usefixtures("caplog")
@withmpi_only
def test_plugin_with_ensemble(caplog):
    # Test in ensemble.
    md = gmx.workflow.from_tpr([tpr_filename, tpr_filename], threads_per_rank=1)

    # Create a WorkElement for the potential
    #potential = gmx.core.TestModule()
    potential_element = gmx.workflow.WorkElement(namespace="testing", operation="create_test")
    potential_element.name = "test_module"
    before = md.workspec.elements[md.name]
    md.add_dependency(potential_element)
    assert potential_element.name in md.workspec.elements
    assert potential_element.workspec is md.workspec
    after = md.workspec.elements[md.name]
    assert not before is after

    # Workaround for https://github.com/kassonlab/gmxapi/issues/42
    # We can't add an operation to a context that doesn't exist yet, but we can't
    # add a work graph with an operation that is not defined in a context.
    context = gmx.get_context()
    context.add_operation(potential_element.namespace, potential_element.operation, my_plugin)
    context.work = md

    with warnings.catch_warnings():
        # Swallow warning about wide MPI context
        warnings.simplefilter("ignore")
        with context as session:
            if context.rank == 0:
                print(context.work)
            session.run()


if __name__ == '__main__':
    unittest.main()
