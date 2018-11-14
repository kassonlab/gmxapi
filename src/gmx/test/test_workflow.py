# Test gmx.workflow classes and functions.

import unittest
import pytest

import gmx
import json
import os
import gmx.util
from gmx.util import to_string
from gmx.util import to_utf8

# # Get a test tpr filename
# from gmx.data import tpr_filename

# These tests will need to be updated when the workspec schema changes. These features appear in
# release 0.0.4, and schema changes that break these tests warrant a bump in workspec_version.
workspec_version = "gmxapi_workspec_0_1"

try:
    from mpi4py import MPI
    withmpi_only = pytest.mark.skipif(not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() >= 2,
                                      reason="Test requires at least 2 MPI ranks, but MPI is not initialized or too small.")
except ImportError:
    withmpi_only = pytest.mark.skip(reason="Test requires at least 2 MPI ranks, but mpi4py is not available.")

# Some constants for this test module
file1 = "a.tpr"
file2 = "b.tpr"

class WorkSpecApiLevelTestCase(unittest.TestCase):
    """Make sure the tests match the module."""
    def test_version(self):
        assert gmx.workflow.workspec_version == workspec_version

class WorkElementTestCase(unittest.TestCase):
    """Tests for the gmx.workflow.WorkElement class."""
    def test_initialization(self):
        """Create a basic element and check initialization."""
        namespace = "gromacs"
        depends = ()
        workspec = None
        name = "spam"
        operation = "load_tpr"
        params = {'input': ["filename1", "filename2"]}
        element = gmx.workflow.WorkElement(namespace=namespace, operation=operation, params=params)

        assert element.name != name
        element.name = name
        assert element.name == name
        assert element.workspec == workspec
        assert element.namespace == namespace
        assert element.operation == operation
        for a, b in zip(params['input'], element.params['input']):
            assert a == b
        for a, b in zip(depends, element.depends):
            assert a == b

    def test_portability(self):
        """Serialize and deserialize."""
        namespace = "gromacs"
        depends = ()
        workspec = None
        name = "spam"
        operation = "load_tpr"
        params = {'input': ["filename1", "filename2"]}
        element = gmx.workflow.WorkElement(namespace=namespace, operation=operation, params=params)

        serialization = element.serialize()
        assert "namespace" in json.loads(to_string(serialization))

        # Two elements with the same name cannot exist in the same workspec, but this is not the case here.
        element = gmx.workflow.WorkElement.deserialize(serialization)
        assert element.name == None
        element = gmx.workflow.WorkElement.deserialize(serialization, name=name)
        assert element.name == name

        assert element.workspec == workspec
        assert element.namespace == namespace
        assert element.operation == operation
        for a, b in zip(params['input'], element.params['input']):
            assert a == b
        for a, b in zip(depends, element.depends):
            assert a == b

class WorkSpecTestCase(unittest.TestCase):
    """Tests for gmx.workflow.WorkSpec class and gmxapi workspec schema."""
    def test_creation(self):
        """Create an empty workspec and check API features."""
        workspec = gmx.workflow.WorkSpec()
        # Release 0.0.4 will mark the finalization of workspec version 0.1.
        assert gmx.version.api_is_at_least(0,0,5)
        assert workspec.version == "gmxapi_workspec_0_1"
    def test_methods(self):
        workspec = gmx.workflow.WorkSpec()
        assert str(workspec) is not None
        assert str(workspec) != ''
        assert repr(workspec) is not None
        assert repr(workspec) != ''

    def test_updates(self):
        """Create an empty workspec and add some basic elements.

        Accessors should preserve the validity of the WorkSpec. Validity basically equates to its ability
        to be processed by the context manager.
        """
        workspec = gmx.workflow.WorkSpec()
        inputelement = gmx.workflow.WorkElement(operation="load_tpr", params={})
        inputelement.name = "tpr_input"
        assert inputelement.name not in workspec.elements
        workspec.add_element(inputelement)
        assert inputelement.name in workspec.elements

    def test_iterator(self):
        """Test iteration over elements in correct sequence."""
        workspec = gmx.workflow.WorkSpec()
        element = gmx.workflow.WorkElement(operation="spam", depends=[])
        element.name = "a"
        workspec.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=[])
        element.name = "b"
        workspec.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=["b"])
        element.name = "c"
        workspec.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=["a", "c"])
        element.name = "d"
        workspec.add_element(element)

        sequence = [element.name for element in workspec]
        index = {name: i for i, name in enumerate(sequence)}
        assert index['a'] < index['d']
        assert index['c'] < index['d']
        assert index['b'] < index['c']

    def test_uniqueness(self):
        """Test that serialization/deserialization works and preserves uniqueness, correctly determined by the hash
        and uid() methods."""

        # Build a dummy workspec
        workspecA = gmx.workflow.WorkSpec()
        element = gmx.workflow.WorkElement(operation="spam", depends=[])
        element.name = "a"
        workspecA.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=[])
        element.name = "b"
        workspecA.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=["b"])
        element.name = "c"
        workspecA.add_element(element)

        element = gmx.workflow.WorkElement(operation="spam", depends=["a", "c"])
        element.name = "d"
        workspecA.add_element(element)

        # Assemble the same workspec in a different order.
        workspecB = gmx.workflow.WorkSpec()
        elements = {element.name: gmx.workflow.WorkElement.deserialize(element.serialize(), name=element.name) for element in workspecA}
        workspecB.add_element(elements['b'])
        workspecB.add_element(elements['c'])
        workspecB.add_element(elements['a'])
        workspecB.add_element(elements['d'])

        # Assemble a similar but non-equivalent workspec.
        workspecC = gmx.workflow.WorkSpec()
        elements = {element.name: gmx.workflow.WorkElement.deserialize(element.serialize(), name=element.name) for element in workspecA}
        elements['b'].depends.append('a')
        workspecC.add_element(elements['a'])
        workspecC.add_element(elements['b'])
        workspecC.add_element(elements['c'])
        workspecC.add_element(elements['d'])

        assert hash(workspecA) == hash(workspecB)
        assert hash(workspecA) != hash(workspecC)
        assert workspecA.uid() == workspecB.uid()
        assert workspecA.uid() != workspecC.uid()

@pytest.mark.usefixtures("cleandir")
class WorkflowFreeFunctions(unittest.TestCase):
    """Test helpers and other free functions in gmx.workflow submodule."""
    def setUp(self):
        # check that we actually got an empty directory form "cleandir"
        assert len(os.listdir(os.getcwd())) == 0
        # Make sure that we have some "input files".
        # Expectations for sanity-checking input are open to discussion...
        with open(file1, 'wb'):
            # an empty file suffices for now
            pass
        with open(file2, 'wb'):
            pass

    def test_from_tpr(self):
        """from_tpr() should return a reference to a WorkElement with an attached WorkSpec.
        It should properly handle single files or arrays of files.
        """

        # Test single file input
        md = gmx.workflow.from_tpr(file1)
        assert isinstance(md, gmx.workflow.WorkElement)
        assert hasattr(md, "workspec")
        assert isinstance(md.workspec, gmx.workflow.WorkSpec)
        assert md.name in md.workspec.elements
        for dependency in md.depends:
            assert dependency in md.workspec.elements

        # Test array file input
        md = gmx.workflow.from_tpr([file1, file2])
        assert isinstance(md, gmx.workflow.WorkElement)
        assert hasattr(md, "workspec")
        assert isinstance(md.workspec, gmx.workflow.WorkSpec)
        assert md.name in md.workspec.elements
        for dependency in md.depends:
            assert dependency in md.workspec.elements

    def test_get_source_elements(self):
        """get_source_elements should find elements with no dependencies and ignore the rest."""
        file1 = "a.tpr"
        file2 = "b.tpr"

        md = gmx.workflow.from_tpr([file1, file2])
        workspec = md.workspec
        elements = set(workspec.elements)
        sources = set([element.name for element in gmx.workflow.get_source_elements(workspec)])
        # workspec should have 'tpr_input' and 'md_sim' elements. 'tpr_input' is the only source.
        assert "tpr_input" in sources
        assert "md_sim" not in sources
        # confirm sources is a subset of elements and sources does not equal elements
        assert len(sources) < len(elements)
    #
    # def test_add_dependency(self):
    #     """Check updating of WorkSpec and WorkElements."""

# @withmpi_only
# class MpiArrayContextTestCase(unittest.TestCase):
#     def test_basic(self):
#         from mpi4py import MPI
#         if not MPI.Is_initialized() or MPI.COMM_WORLD.Get_size() != 2:
#             return
#         work = gmx.core.from_tpr(tpr_filename)
#         context = gmx.context.MpiArrayContext([work, work])
#         with context as session:
#             session.run()
#             rank = context.rank
#             output_path = os.path.join(context.workdir_list[rank], 'traj.trr')
#             assert(os.path.exists(output_path))
#             print("Worker {} produced {}".format(rank, output_path))


if __name__ == '__main__':
    unittest.main()
