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


__all__ = ['WorkSpec']

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

    """
    def __init__(self):
        pass

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
