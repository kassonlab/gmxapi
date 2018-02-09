"""
Provide workflow-level utilities and classes
============================================

`class gmx.workflow.WorkSpec`:
Container of workflow elements with data dependency
information and requirements for execution. E.g. once Array elements are added,
the WorkSpec can only be launched in a context that supports parallel Array
elements. These attributes can be refined and requirements minimized in the future.
WorkSpec instances can be merged with `WorkSpec.add()`. Reference to elements remain valid after the
merge, but may have modified properties (such as unique identifiers or hashes
associated with their relationship to the rest of the workflow). An element cannot
be added to a WorkSpec if it has dependencies that are not in the WorkSpec.

Properties
----------

Various symbols are defined in the gmx.workflow namespace to indicate requirements of workflows. Context implementations
inspect the properties of a WorkSpec to determine if the work can be launched on the available resources.

``ARRAY``: work requires parallel execution to satisfy data dependencies.


Single-sim example

    >>> work = gmx.workflow.from_tpr(filename)
    >>> gmx.run(work)
    >>>
    >>> # The above is shorthand for
    >>> work = gmx.workflow.from_tpr(filename)
    >>> with gmx.get_context(work) as session:
    ...    session.run()
    ...
    >>> # Which is, in turn, shorthand for
    >>> work = gmx.workflow.from_tpr(filename)
    >>> with gmx.context.Context(work) as session:
    ...    session.run()
    ...

Array sim example

    >>> work = gmx.workflow.from_tpr([filename1, filename2])
    >>> gmx.run(work)
    >>>
    >>> # The above is shorthand for
    >>> work = gmx.workflow.from_tpr([filename1, filename2])
    >>> with gmx.get_context(work) as session:
    ...    session.run()
    ...
    >>> # Which is, in turn, shorthand for
    >>> work = gmx.workflow.from_tpr([filename1, filename2])
    >>> global_context = gmx.context.ParallelArrayContext(work)
    >>> my_id = global_context.local_id
    >>> my_work = global_context.work_array[my_id]
    >>> with gmx.context.Context(my_work) as session:
    ...    session.run()
    ...

Single-sim with plugin

    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_potential(potential)
    >>> gmx.run(work)
    >>>
    >>> # The above is shorthand for
    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_potential(potential)
    >>> with gmx.context.Context(work) as session:
    ...    session.run()

Array sim with plugin

    >>> work = gmx.workflow.from_tpr([filename1, filename2])
    >>> potential = myplugin.EnsembleRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_potential(potential)
    >>> gmx.run(work)

    >>> # The above is shorthand for
    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_potential(potential)
    >>> global_context = gmx.context.ParallelArrayContext(work)
    >>> my_id = global_context.local_id
    >>> my_work = global_context.work_array[my_id]
    >>> with gmx.context.Context(my_work) as session:
    ...    session.run()


Array sim with plugin using global resources

    >>> md = gmx.create_md_unit([filename1, filename2])
    >>> workfile = gmx.SharedDataFile(workfilename)
    >>> potential = myplugin.EnsembleRestraint([1,4], R0=2.0, k=10000.0, workfile=workfile)
    >>> md.add_potential(potential)
    >>> gmx.run(md)

    >>> # The above is shorthand for
    >>> # Create work spec and get handle to MD work unit
    >>> md = gmx.workflow.from_tpr([filename1, filename2])
    >>> # Implicitly, the new SharedDataFile has its own otherwise-empty workspec now.
    >>> workfile = gmx.SharedDataFile(workfilename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0, workfile=workfile)
    >>> # EnsembleRestraint is dependent on workfile, so `workfile` must be added to
    >>> # `work` before `potential` can be added to `work`. Combine specs.
    >>> md.workflow.add(workfile.workflow)
    >>> md.add_potential(potential)
    >>> # Initialize resources for work or throw appropriate error
    >>> global_context = gmx.get_context(md.workflow)
    >>> # Global resources like SharedDataFile are now available.
    >>> my_id = global_context.local_id
    >>> my_work = global_context.work_array[my_id]
    >>> with gmx.context.Context(my_work) as session:
    ...    # plugin and simulation are now initialized.
    ...    session.run()

Note that object representing work specification contains a recipe, not references to actual objects representing the
workflow elements. Distinctly, objects can be created as handles to representations of workflow elements, and these
objects can hold strong references to objects representing work specification. In other words, the work specification
is a serialized data structure containing the serialized representations of workflow elements.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .exceptions import UsageError

__all__ = ['WorkSpec', 'SharedDataElement']

# module-level constant indicating a workflow implementing parallel array work.
ARRAY = 0

class WorkSpec(object):
    """
    Container of workflow elements with data dependency
    information and requirements for execution. E.g. once Array elements are added,
    the WorkSpec can only be launched in a context that supports parallel Array
    elements. These attributes can be refined and requirements minimized in the future.
    WorkSpec instances can be merged with `WorkSpec.add()`. Reference to elements remain valid after the
    merge, but may have modified properties (such as unique identifiers or hashes
    associated with their relationship to the rest of the workflow). An element cannot
    be added to a WorkSpec if it has dependencies that are not in the WorkSpec.

    In the future, for easier accounting, the API could provide each work element with a unique identifier that can be
    used to reconstruct new references from the API objects instead of making sure the Python-level accounting works well.
    TBD.

    Attributes:
        properties: List of required features that not all Context implementations can provide (default empty list)

    Detail:

    The work specification schema needs to be able to represent something like the following.

        version: "gmxapi_workspec_1_0"
        attributes: [requires_synchronous]
        elements:
            myinput:
                namespace: "gromacs"
                operation: load_tpr
                params: ["tpr_filename1", "tpr_filename2"]
            mydata:
                namespace: "gromacs"
                operation: open_global_data_with_barrier
                params: "data_filename"
            mypotential:
                namespace: "myplugin"
                operation: create_mdmodule
                params: [...]
                depends: mydata
            mysim:
                namespace: "gromacs"
                operation: md
                depends: [myinput, mypotential]

    """
    def __init__(self):
        self.version = "gmxapi_workspec_1_0"
        self.elements = dict()

    def add(self, spec):
        """
        Merge the provided spec into this one.

        We can't easily replace references to ``spec`` with references to the WorkSpec we are merging into, but we can
        steal the work elements out of ``spec`` and leave it empty. We could also set an ``alias`` attribute in it or
        something, but that seems unnecessary. Alternatively, we can set the new and old spec to be equal, but we would
        need an additional abstraction layer to keep them from diverging again. Since client code will retain references
        to the elements in the work spec, we need to be clear about when we are duplicating a WorkSpec versus obtaining
        different references to the same.

        This is an implementation detail that can be unresolved and hidden for now. The high-level interface only
        requires that client code can bind different workflow elements together in a sensible way and get expected
        results.

        :param spec: WorkSpec to be merged into this one.
        :return:
        """

    # def serialize(self):

    # @classmethod deserialize(serialized):

class WorkElement(object):
    """Encapsulate an element of a work specification."""
    def __init__(self, namespace="gromacs", operation=None, params=(), depends=()):
        self.namespace = str(namespace)
        # We can add an operations submodule to validate these. E.g. self.operation = gmx.workflow.operations.normalize(operation)
        if operation is not None:
            self.operation = str(operation)
        else:
            raise UsageError("Invalid argument type for operation.")
        self.params = params
        self.depends = depends

        # The Python class for work elements keeps a strong reference to a WorkSpec object containing its description
        self.name = ""
        self.workspec = None

    def serialize(self):
        """Create a string representation of the work element.

        The WorkElement class exists just to provide convenient handles in Python. The WorkSpec is not actually a
        container of WorkElement objects.
        """
        import json
        output_dict = {"namespace": self.namespace,
                       "operation": self.operation,
                       "params": self.params,
                       "depends": self.depends
                       }
        return json.dumps(output_dict)

    @classmethod
    def deserialize(cls, input_string):
        """Create a new WorkElement object from a serialized representation.

        \todo When subclasses become distinct, this factory function will need to do additional dispatching to create an object of the correct type.
        Alternatively, instead of subclassing, a slightly heavier single class may suffice, or more flexible duck typing might be better.
        """
        import json
        args = json.loads(input_string)
        element = cls(namespace=args['namespace'], operation=args['operation'], params=args['params'], depends=args['depends'])
        return element


class MDElement(WorkElement):
    """Work element with MD-specific extensions.

    The schema may not need to be changed, but the API object may be expected to provide additional functionality.
    """
    def __init__(self):
        """Create a blank MDElement representation.

        It may be appropriate to insist on creating objects of this type via helpers or factories, particularly if
        creation requires additional parameters.
        """
        super(MDElement, self).__init__(namespace="gromacs", operation="md")

    def add_potential(self, potential):
        """Attach an additional MD potential to the simulator.

        Args:
            potential :

        This operation creates a dependency in a WorkSpec.
        If the MDElement is not already in a WorkSpec, one will be created.
        If the potential is not already in the same WorkSpec as the MDElement, it will be moved.
        Attempting to add a potential that has dependencies in a different WorkSpec than the MDElement is an error.
        If this appears to be a problem, consider merging the two WorkSpecs first with WorkSpec.add.
        \todo consider instead a gmx.workflow.merge(workspecA, workspecB) free function that returns a new WorkSpec.
        """

class SharedDataElement(WorkElement):
    """Work element with MD-specific extensions.

    The schema may not need to be changed, but the API object may be expected to provide additional functionality.
    """
    def __init__(self):
        """Create a blank SharedDataElement representation.

        It may be appropriate to insist on creating objects of this type via helpers or factories, particularly if
        creation requires additional parameters.
        """
        super(SharedDataElement, self).__init__(namespace="gromacs", operation="open_global_data_with_barrier")

def get_source_elements(workspec):
    """Get an iterator of the starting nodes in the work spec.

    Source elements have no dependencies and can be processed immediately. Elements with dependencies
    cannot be processed, instantiated, or added to a work spec until after their dependencies have been.

    Args:
        workspec : an existing work specification to analyze, such as by a Context implementation preparing to schedule work.

    Returns:
        iterator of gmx.workflow.WorkElement objects that may be processed without dependencies.

    This function is provided in the API to allow flexibility in how source elements are determined.
    """

def from_tpr(input=None):
    """Create a WorkSpec from a (list of) tpr file(s).

    :param input: string or list of strings giving the filename(s) of simulation input
    :return: simulation member of a gmx.workflow.WorkSpec object

    Produces a WorkSpec with the following data.

        version: "gmxapi_workspec_1_0"
        elements:
            tpr_input:
                namespace: "gromacs"
                operation: load_tpr
                params: ["tpr_filename1", "tpr_filename2"]
            md_sim:
                namespace: "gromacs"
                operation: md
                depends: [myinput]

    """
    import os

    usage = "argument to from_tpr() should be a valid filename or list of filenames."

    # Normalize to tuple input type.
    if isinstance(input, str):
        tpr_list = (input,)
    elif hasattr(input, "__iter__"):
        # Assume list-like input
        tpr_list = tuple(input)
    else:
        raise UsageError(usage)

    # Check for valid filenames
    for arg in tpr_list:
        if not (os.path.exists(arg) and os.path.isfile(arg)):
            arg_path = os.path.abspath(arg)
            raise UsageError(usage + " Got {}".format(arg_path))

    # Create an empty WorkSpec
    workspec = WorkSpec()

    # Create and add the Element for the tpr file(s)
    inputelement = WorkElement(operation="load_tpr", params=tpr_list)
    inputelement.name = "tpr_input"
    if inputelement.name not in workspec.elements:
        # Operations such as this need to be replaced with accessors or properties that can check the validity of the WorkSpec
        workspec.elements[inputelement.name] = inputelement.serialize()
        inputelement.workspec = workspec

    # Create and add the simulation element
    # We can add smarter handling of the `depends` argument, but it is only critical to check when adding the element
    # to a WorkSpec.
    mdelement = WorkElement(operation="md", depends=[inputelement.name])
    mdelement.name = "md_sim"
    # Check that the element has not already been added, but that its dependency has.
    if mdelement.name not in workspec.elements and inputelement.name in workspec.elements:
        workspec.elements[mdelement.name] = mdelement.serialize()
        mdelement.workspec = workspec

    return mdelement



