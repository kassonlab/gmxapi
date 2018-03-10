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

.. ``ARRAY``: work requires parallel execution to satisfy data dependencies.


Single-sim example
::
    >>> md = gmx.workflow.from_tpr(filename)
    >>> gmx.run(md)
    >>>
    >>> # The above is shorthand for
    >>> md = gmx.workflow.from_tpr(filename)
    >>> with gmx.get_context(md.workspec) as session:
    ...    session.run()
    ...
    >>> # Which is, in turn, shorthand for
    >>> md = gmx.workflow.from_tpr(filename)
    >>> with gmx.context.Context(md.workspec) as session:
    ...    session.run()

Array sim example
::
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

Single-sim with plugin
::
    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work.add_dependency(potential)
    >>> gmx.run(work)
    >>>
    >>> # The above is shorthand for
    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_mdmodule(potential)
    >>> with gmx.context.Context(work) as session:
    ...    session.run()

Array sim with plugin
::
    >>> md = gmx.workflow.from_tpr([filename1, filename2])
    >>> potential = myplugin.EnsembleRestraint([1,4], R0=2.0, k=10000.0)
    >>> gmx.add_potential(md, potential)
    >>> gmx.run(work)

The above is shorthand for
::
    >>> work = gmx.workflow.from_tpr(filename)
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0)
    >>> work['md'].add_mdmodule(potential)
    >>> global_context = gmx.context.ParallelArrayContext(work)
    >>> my_id = global_context.local_id
    >>> my_work = global_context.work_array[my_id]
    >>> with gmx.context.Context(my_work) as session:
    ...    session.run()


Array sim with plugin using global resources
::
    >>> md = gmx.workflow.from_tpr([filename1, filename2])
    >>> workdata = gmx.workflow.SharedDataElement()
    >>> numsteps = int(1e-9 / 5e-15) # every nanosecond or so...
    >>> potential = myplugin.EnsembleRestraint([1,4], R0=2.0, k=10000.0, workdata=workdata, data_update_period=numsteps)
    >>> md.add_dependency(potential)
    >>> gmx.run(md)

The above is shorthand for
::
    >>> # Create work spec and get handle to MD work unit
    >>> md = gmx.workflow.from_tpr([filename1, filename2])
    >>> workdata = gmx.workflow.SharedDataElement()
    >>> potential = myplugin.HarmonicRestraint([1,4], R0=2.0, k=10000.0, workdata=workdata)
    >>> # EnsembleRestraint is dependent on workdata, so `workdata` must be added to
    >>> # `work` before `potential` can be added to `work`. Combine specs.
    >>> md.workflow.add(workdata)
    >>> md.add_dependency(potential)
    >>> # Initialize resources for work or throw appropriate error
    >>> global_context = gmx.get_context(md.workflow)
    >>> # Global resources like SharedDataFile are now available.
    >>> my_id = global_context.local_id
    >>> with global_context as session:
    ...    # plugin and simulation are now initialized.
    ...    session.run()

Note that object representing work specification contains a recipe, not references to actual objects representing the
workflow elements. Distinctly, objects can be created as handles to representations of workflow elements, and these
objects can hold strong references to objects representing work specification. In other words, the work specification
is a serialized data structure containing the serialized representations of workflow elements.

Implementation details: When the plugin potential is instantiated, it has a WorkElement interface and can
provide enough information for the Context to call the same constructor, but we want a portal back to the
original object handle, too. If data only needs to be pulled by the handle, then it can chase references.
When it is added as a dependency to the md operation, it gains a reference to the workspec. When the
work is launched, that workspec gains a reference to the Context. We need some sort of signal that can
propagate back to the handles to the work elements.

TBD:

1.  We may decide that there is always a single active Context that can be picked up from a singleton, such that a
    workspec can always have at least a generic Context. This would imply that a workspec could exist in a Context that
    couldn't run it, which might be antithetical.
2.  We may decide that WorkElements are always in some sort of workspec, and that there may be a lot of merging of
    work specs. This would resolve the ambiguity that a WorkElement may or may not be associated with a work spec, but
    it cannot happen right now for several reasons.
    * there is not a clear way to move elements with dependents from one work spec to another without some ugly transient states.
    * When an element is serialized and deserialized, there is not a good way of finding the original workspec object ref.
    * We make a lot of use of temporary WorkElement objects for which we don't care about the workspec.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from . import exceptions
import gmx
from gmx import logging

__all__ = ['WorkSpec', 'SharedDataElement', 'WorkElement']

# Module-level logger
logger = logging.getLogger(__name__)
logger.info('Importing gmx.workflow')

# Work specification version string.
workspec_version = "gmxapi_workspec_0_1"
logger.info("Using schema version {}.".format(workspec_version))

# module-level constant indicating a workflow implementing parallel array work.
# ARRAY = 0

class WorkSpec(object):
    """
    Container of workflow elements with data dependency
    information and requirements for execution. E.g. once Array elements are added,
    the WorkSpec can only be launched in a context that supports parallel Array
    elements. These attributes can be refined and requirements minimized in the future.

    Future functionality may allow
    WorkSpec instances can be merged with `WorkSpec.add()`.
    Reference to elements remain valid after the
    merge, but may have modified properties (such as unique identifiers or hashes
    associated with their relationship to the rest of the workflow). An element cannot
    be added to a WorkSpec if it has dependencies that are not in the WorkSpec.

    Work is added to the specification by passing a WorkElement object to WorkSpec.add_element().
    Any dependencies in the WorkElement must already be specified in the target WorkSpec.

    When iterated over, a WorkSpec object yields WorkElement objects in a valid order to
    keep dependencies satisfied, but not necessarily the same order in which add_element()
    calls were originally made.

    When iterated over, a WorkSpec object returns WorkElement objects

    In the future, for easier accounting, the API could provide each work element with a unique identifier that can be
    used to reconstruct new references from the API objects instead of making sure the Python-level accounting works well.
    TBD.

    Detail:

    The work specification schema needs to be able to represent something like the following.
    ::
        version: "gmxapi_workspec_1_0"
        elements:
            myinput:
                namespace: "gromacs"
                operation: "load_tpr"
                params: ["tpr_filename1", "tpr_filename2"]
            mydata:
                namespace: "gmxapi"
                operation: "open_global_data_with_barrier"
                params: ["data_filename"]
            mypotential:
                namespace: "myplugin"
                operation: "create_mdmodule"
                params: [...]
                depends: [mydata]
            mysim:
                namespace: "gmxapi"
                operation: "md"
                depends: [myinput, mypotential]

    todo: Params schema incomplete!
    We can say params is a list, but what are the elements? What if parameters need to be key--value pairs or vectors? We could assume that the value of params is some serialized data that the operation is required to know how to process, but for the moment, we are assuming it is just a list of positional arguments.
    """
    def __init__(self):
        self.version = workspec_version
        self.elements = dict()
        self._context = None

    def _chase_deps(self, source_set, name_list):
        """Helper to recursively generate dependencies before dependents.

        Given a set of WorkElement objects and a list of element names, generate WorkElements for
        the members of name_list plus their dependencies in an order such that dependencies are
        guaranteed to occur before their dependent elements.

        For example, to sequence an entire work specification into a reasonable order for instantiation, use

            >>> workspec._chase_deps(set(workspec.elements.keys()), list(workspec.elements.keys()))

        Note: as a member function of WorkSpec, we have access to the full WorkSpec elements data at all
        times, giving us extra flexibility in implementation and arguments.

        Args:
            source_set: a copy of a set of element names (will be consumed during execution)
            name_list: name list to be expanded with dependencies and sequenced

        Note that source_set is a reference to an object that is modified arbitrarily.
        .. todo:: Maybe this shouldn't be a member function, but a closure within WorkSpec.__iter__()

        """
        assert isinstance(source_set, set)
        for name in tuple(name_list):
            if name in source_set:
                source_set.remove(name)
                element = WorkElement.deserialize(self.elements[name], name=name, workspec=self)
                for dep in self._chase_deps(source_set, element.depends):
                    yield dep
                yield element

    def __iter__(self):
        source_set = set(self.elements.keys())
        for element in self._chase_deps(source_set, source_set):
            yield element

    def add_element(self, element):
        """Add an element to a work specification if possible.

        Adding an element to a WorkSpec must preserve the validity of the workspec, which involves several checks.
        We do not yet check for element uniqueness beyond a string name.

        If an element is added that was previously in another WorkSpec, it must first be removed from the
        other WorkSpec.
        """
        if hasattr(element, "namespace") and hasattr(element, "operation") and hasattr(element, "serialize"):
            if not hasattr(element, "name") or element.name is None or len(str(element.name)) < 1:
                raise exceptions.UsageError("Only named elements may be added to a WorkSpec.")
            if element.name in self.elements:
                raise exceptions.UsageError("Elements in WorkSpec must be uniquely identifiable.")
            if hasattr(element, "depends"):
                for dependency in element.depends:
                    if not dependency in self.elements:
                        raise exceptions.UsageError("Element dependencies must already be specified before an Element may be added.")
            # Okay, it looks like we have an element we can add
            if hasattr(element, "workspec") and element.workspec is not None and element.workspec is not self:
                raise exceptions.Error("Element must be removed from its current WorkSpec to be added to this WorkSpec, but element removal is not yet implemented.")
            self.elements[element.name] = element.serialize()
            element.workspec = self
        else:
            raise exceptions.ValueError("Provided object does not appear to be compatible with gmx.workflow.WorkElement.")
        logger.info("Added element {} to workspec.".format(element.name))

    # def remove_element(self, name):
    #     """Remove named element from work specification.
    #
    #     Does not delete references to WorkElement objects, but WorkElement objects will be moved to a None WorkSpec."""

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

        \todo consider instead a gmx.workflow.merge(workspecA, workspecB) free function that returns a new WorkSpec.
        """


    # Not sure we want to do serialization and deserialization yet, since we don't currently have a way to
    # determine the uniqueness of a work specification.
    # def serialize(self):

    # @classmethod deserialize(serialized):

    def __str__(self):
        """Generate string representation for str() or print().

        The string output should look like the abstract schema for gmxapi_workspec_1_0, but the exact
        format is unspecified.

        For json output, use WorkSpec.serialize(). For output in the form of valid Python, use repr().
        """
        output = ""

        output += 'version: "{}"\n'.format(self.version)

        output += 'elements:\n'
        for element in self.elements:
            data = WorkElement.deserialize(self.elements[element])
            output += '    {}:\n'.format(element)
            output += '        namespace: "{}"\n'.format(data.namespace)
            output += '        operation: {}\n'.format(data.operation)
            # \todo improve output formatting: don't be lazy about printing these lists.
            if data.params is not None:
                output += '        params: {}\n'.format(str(data.params))
            if data.depends is not None:
                output += '        depends: {}\n'.format(str(data.depends))

        return output

    def __repr__(self):
        """Generate Pythonic representation for repr(workspec)."""
        return 'gmx.workflow.WorkSpec()'

# A possible alternative name for WorkElement would be Operator, since there is a one-to-one
# mapping between WorkElements and applications of "operation"s. We need to keep in mind the
# sensible distinction between the WorkElement abstraction and the API objects and DAG nodes.
class WorkElement(object):
    """Encapsulate an element of a work specification."""
    def __init__(self, namespace="gmxapi", operation=None, params=(), depends=()):
        self.namespace = str(namespace)
        # We can add an operations submodule to validate these. E.g. self.operation = gmx.workflow.operations.normalize(operation)
        if operation is not None:
            self.operation = str(operation)
        else:
            raise exceptions.UsageError("Invalid argument type for operation.")

        # \todo It is currently non-sensical to update any attributes after adding to a workspec, but nothing prevents it.
        self.params = list(params)
        self.depends = list(depends)

        # The Python class for work elements keeps a strong reference to a WorkSpec object containing its description
        self.name = None
        self.workspec = None

    def add_dependency(self, element):
        """Add another element as a dependency.

        First move the provided element to the same WorkSpec, if not already here.
        Then, add to depends and update the WorkSpec.
        """
        if element.workspec is None:
            self.workspec.add_element(element)
            assert element.workspec is self.workspec
            assert element.name in self.workspec.elements
        elif element.workspec is not self.workspec:
            raise exceptions.ApiError("Element will need to be moved to the same workspec.")

        self.depends.append(element.name)
        self.workspec.elements[self.name] = self.serialize()

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
    def deserialize(cls, input_string, name=None, workspec=None):
        """Create a new WorkElement object from a serialized representation.

        \todo When subclasses become distinct, this factory function will need to do additional dispatching to create an object of the correct type.
        Alternatively, instead of subclassing, a slightly heavier single class may suffice, or more flexible duck typing might be better.
        """
        import json
        args = json.loads(input_string)
        element = cls(namespace=args['namespace'], operation=args['operation'], params=args['params'], depends=args['depends'])
        if name is not None:
            element.name = name
            # This conditional is nested because we can only add named elements to a WorkSpec.
            if workspec is not None:
                element.workspec = workspec
                if element.name not in workspec.elements:
                    workspec.add_element(element)
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
        super(MDElement, self).__init__(namespace="gmxapi", operation="md")

    def add_potential(self, potential):
        """Attach an additional MD potential to the simulator.

        Args:
            potential :

        This operation creates a dependency in a WorkSpec.
        If the MDElement is not already in a WorkSpec, one will be created.
        If the potential is not already in the same WorkSpec as the MDElement, it will be moved.
        Attempting to add a potential that has dependencies in a different WorkSpec than the MDElement is an error.
        If this appears to be a problem, consider merging the two WorkSpecs first with WorkSpec.add.
        """

class SharedDataElement(WorkElement):
    """Work element with MD-specific extensions.

    The schema may not need to be changed, but the API object may be expected to provide additional functionality.
    """
    def __init__(self, args, kwargs, name=None):
        """Create a blank SharedDataElement representation.

        It may be appropriate to insist on creating objects of this type via helpers or factories, particularly if
        creation requires additional parameters.
        """
        import json
        self.args = json.dumps(args)
        self.kwargs = json.dumps(kwargs)
        super(SharedDataElement, self).__init__(namespace="gmxapi",
                                                operation="global_data",
                                                params=[self.args, self.kwargs])
        self.name = name

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
    for name in workspec.elements:
        element_data = workspec.elements[name]
        element = WorkElement.deserialize(element_data)
        if len(element.depends) == 0:
            element.name = name
            element.workspec = workspec
            yield(element)

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
                namespace: "gmxapi"
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
        raise exceptions.UsageError(usage)

    # Check for valid filenames
    for arg in tpr_list:
        if not (os.path.exists(arg) and os.path.isfile(arg)):
            arg_path = os.path.abspath(arg)
            raise exceptions.UsageError(usage + " Got {}".format(arg_path))

    # Create an empty WorkSpec
    workspec = WorkSpec()

    # Create and add the Element for the tpr file(s)
    inputelement = WorkElement(namespace='gromacs', operation="load_tpr", params=tpr_list)
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
    workspec.add_element(mdelement)

    return mdelement

def run(work=None):
    """Run the provided work on available resources.

    Args:
        work : either a WorkSpec or an object with a `workspec` attribute containing a WorkSpec object.

    Returns:
        run status.
    """
    if isinstance(work, WorkSpec):
        workspec = work
    elif hasattr(work, "workspec") and isinstance(work.workspec, WorkSpec):
        workspec = work.workspec
    else:
        raise exceptions.UsageError("Runnable work must be provided to run.")
    # Find a Context that can run the work and hand it off.
    with gmx.get_context(workspec) as session:
        status = session.run()
    return status
