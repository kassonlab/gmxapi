"""
Execution Context
=================
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['Context', 'DefaultContext']

import os
import warnings
import networkx as nx
from networkx import DiGraph as _Graph

from gmx import exceptions
from gmx import logging
import gmx.core
from . import workflow
from .workflow import WorkSpec

# Module-level logger
logger = logging.getLogger(__name__)
logger.info('Importing gmx.context')

class Context(object):
    """ Proxy to API Context provides Python context manager.

    Binds to a workflow and manages computation resources.

    Attributes:
        workflow (:obj:`gmx.workflow.WorkSpec`): bound workflow to be executed.

    Example:
        >>> with Context(my_workflow) as session: # doctest: +SKIP
        ...    session.run()

    Things are still fluid, but what we might do is have all of the WorkSpec operations that are supported
    by a given Context to correspond to member functions in the Context, a SessionBuilder, or Session. In
    any case, the operations allow a Context implementation to transform a work specification into a
    directed acyclic graph of schedulable work.
    """
    # \todo Put the following to-do someplace more appropriate
    # \todo There should be a default Context active from the first `import gmx` or at least before the first logger call.
    # The Context is the appropriate entity to own or mediate access to an appropriate logging facility,
    # but right now we are using the module-level Python logger.
    def __init__(self, workflow=None):
        """Create new context bound to the provided workflow, if any.

        Args:
            workflow (gmx.workflow.WorkSpec) work specification object to bind.

        """
        self._session = None
        self.__workflow = workflow

    @property
    def workflow(self):
        return self.__workflow

    @workflow.setter
    def workflow(self, workflow):
        """Before accepting a workflow, the context must check whether it can interpret the work specification."""

        self.__workflow = workflow

    @classmethod
    def check_workspec(cls, workspec, raises=False):
        """Check the validity of the work specification in this Context.

        Args:
            workspec: work specification to check
            raises: Boolean (default False)

        If raises == True, raises exceptions for problems found in the work specification.

        Returns:
            True if workspec is processable in this Context, else False.
        """
        # initialize return value.
        is_valid = True
        # Check compatibility
        if workspec.version != workflow.workspec_version:
            is_valid = False
            if raises:
                raise exceptions.ApiError('Incompatible workspec version.')
        # Check that Elements are uniquely identifiable.
        elements = dict()
        for element in workspec.elements:
            if element.name is not None and element.name not in elements:
                elements[element.name] = element
            else:
                is_valid = False
                if raises:
                    raise exceptions.ApiError('WorkSpec must contain uniquely named elements.')
        # Check that the specification is complete. There must be at least one source element and all
        # dependencies must be fulfilled.
        sources = set([element.name for element in gmx.workflow.get_source_elements(workspec)])
        if len(sources) < 1:
            is_valid = False
            if raises:
                raise exceptions.ApiError('WorkSpec must contain at least one source element')
        for name in workspec.elements:
            element = gmx.workflow.WorkElement.deserialize()
        return is_valid


    def __enter__(self):
        """Implement Python context manager protocol.

        Returns:
            runnable session object.
        """
        if self._session is not None:
            raise exceptions.Error('Already running.')
        # The API runner currently has an implicit context.
        try:
            # \todo Pass the API context implementation object to launch
            self._session = self.workflow.launch()
            # \todo Let the session provide a reference to its parent context instance.
        except:
            self._session = None
            raise
        return self._session

    def __exit__(self, exception_type, exception_value, traceback):
        """Implement Python context manager protocol."""
        # Todo: handle exceptions.
        self._session.close()
        self._session = None
        return False

# In the next pass, Context can become more abstract and simplest-case behavior moved here.
# class SimpleContext(Context):
#     def __init__(self, options=None):
#         pass

class DefaultContext(Context):
    """ Produce an appropriate context for the work and compute environment."""
    def __init__(self, work):
        # There is very little context abstraction at this point...
        super(DefaultContext, self).__init__(work)

class SerialArrayContext(object):
    """ Run a series of simulations in sequence.

    Hierarchical Context manages simpler contexts for an array of work specifications.

    This example illustrates that it may not be clear what to do with the Python code executed in a context. Should it
    accumulate API operation objects and run them during __exit__()? It might be appropriate to move the usage down to
    a lower level.
    """
    def __init__(self, work):
        if not isinstance(work, list):
            raise ValueError('work specification should be a Python list.')
        self.__context_array = list([DefaultContext(work_element) for work_element in work])
        self._session = None

def shared_data_maker(element):
    """Make a shared data element for use by dependent nodes.

    This version uses mpi4py to share data and supports a single downstream node.

    The element provides a serialized argument list for numpy.empty() as two elements, args, and kwargs. Each subscriber receives such
    an array at launch along with a python function handle to call-back to at some interval (passed to
    the plugin C++ code).
    """

    # New idea: Instead of being dependent on a shared data node, let participants add a downstream node
    # that performs the reduce operation. A context can determine unsuitability for this parallelism with
    # lack of support for a reduce with a period less than the length of the specified trajectories.
    # To support reduce operations for ensembles wider than the Context, the Context could provide an
    # additional tier in the reduction for batches of co-scheduled tasks.

    import json

    class Builder(object):
        def __init__(self, element):
            logger.debug("Processing element {}".format(element.serialize()))
            context = element.workspec._context
            self.rank = context.rank
            self.subscribinging_ranks = []
            self.subscriber = None
            self.comm = context._communicator
            self.name = element.name
            params = element.params
            # First draft: params contains two elements: a serialized args and a serialized kwargs
            logger.debug("Processing parameters {}".format(params))
            assert len(params) == 2
            self.args = json.loads(params[0])
            assert isinstance(self.args, list)
            self.kwargs = json.loads(params[1])
            assert isinstance(self.kwargs, dict)
            # The builder can hold an updater to be provided to the subscriber at launch. The updater is
            # a function reference that the user provides to perform a desired periodic action. Not sure
            # how this will work in the future. Allowing arbitrary Python code to be provided during job
            # configuration would be the hardest thing. The updater could be another user-provided operation.
            # Hopefully we can provided some canned behaviors that can be selected with element parameters.
            # Maybe both.
            self.updater = None

        def add_subscriber(self, builder):
            # At this point, we could find out how this data will be used (e.g. subscribing ranks)
            if self.subscriber is None:
                self.subscriber = builder
            else:
                raise exceptions.ApiError("This element does not support multiple consumers")

        def build(self, dag):
            # Either the builder needs to get the key for the subscribed node(s) so that we can
            # create the edge now, or this builder needs to provide subscribers with the key of this
            # DAG node so that the subscriber can create the edge. I think I prefer the latter, so that
            # edge creation is tied to the binding process of a new node with its upstream nodes.
            nodename = self.name
            dag.add_node(nodename)
            self.node = dag.nodes[nodename]

            self.node['launch'] = self.__launch
            # To avoid ambiguity, let's assert that only nodes that are active at launch will have data.
            self.node['data'] = None
            self.node['comm'] = self.comm
            self.subscriber.input_nodes.append(nodename)
            self.node['launch'] = self.__launch

        def __launch(self, rank=None):
            """Create the shared data resource for subscribed builders.

            This is the place to provide subscribers with API references for interacting with
            the shared data facility.
            """
            import numpy
            data = numpy.empty(*self.args, **self.kwargs)
            self.node['data'] = data
            self.subscriber.shared_data_updater = self.updater
            self.subscribinging_ranks = list(range(self.subscriber.width))

            # Later, we can offload consumer responsibilities and the updater function to this runner,
            # but we aren't there yet.
            runner = None
            return runner

    builder = Builder(element)
    return builder

class ParallelArrayContext(object):
    """Manage an array of simulation work executing in parallel.

    This is the first implementation of a new style of Context class that has some extra abstraction
    and uses the new WorkSpec idea.

    Additional facilities are available to elements of the array members.

      * array element corresponding to work in the current sub-context
      * "global" resources managed by the ParallelArrayContext

    Attributes:
        work :obj:`gmx.workflow.WorkSpec`: specification of work to be performed when a session is launched.
        rank : numerical index of the current worker in a running session (None if not running)
        size : Minimum width needed for the parallelism required by the array of work being executed.
        elements : dictionary of references to elements of the workflow.

    `rank`, `size`, and `elements` are empty or None until the work is processed, as during session launch.


    Example: Use ``mpiexec -n 2 python -m mpi4py myscript.py`` to run two jobs at the same time.
    In this example the jobs are identical. In myscript.py:

        >>> import gmx
        >>> import gmx.core
        >>> from gmx.data import tpr_filename # Get a test tpr filename
        >>> work = gmx.workflow.from_tpr([tpr_filename, tpr_filename])
        >>> gmx.run(work)

    Example:

        >>> import gmx
        >>> import gmx.core
        >>> from gmx.data import tpr_filename # Get a test tpr filename
        >>> work = gmx.workflow.from_tpr([tpr_filename, tpr_filename])
        >>> context = gmx.context.ParallelArrayContext(work)
        >>> with context as session:
        ...    session.run()
        ...    # The session is one abstraction too low to know what rank it is. It lets the spawning context manage
        ...    # such things.
        ...    # rank = session.rank
        ...    # The local context object knows where it fits in the global array.
        ...    rank = context.rank
        ...    output_path = os.path.join(context.workdir_list[rank], 'traj.trr')
        ...    assert(os.path.exists(output_path))
        ...    print('Worker {} produced {}'.format(rank, output_path))
        ...

    Implementation notes:

    To produce a running session, the Context __enter__() method is called, according to the Python context manager
    protocol. At this time, the attached WorkSpec must be feasible on the available resources. To turn the specified
    work into an executable directed acyclic graph (DAG), handle objects for the elements in the work spec are sequenced
    in dependency-compatible order and the context creates a "builder" for each according to the element's operation.
    Each builder is subscribed to the builders of its dependency elements. The DAG is then assembled by calling each
    builder in sequence. A builder can add zero, one, or more nodes and edges to the DAG.

    The Session is then launched from the DAG. What happens next is implementation-dependent, and it may take a while for
    us to decide whether and how to standardize interfaces for the DAG nodes and edges and/or execution protocols. I
    expect each node will at least have a `launch()` method, but will also probably have typed input and output ports as well as some signalling.
    A sophisticated and abstract Session implementation could schedule work only to satisfy data dependencies of requested
    output upon request. Our immediate implementation will use the following protocol.

    Each node has a `launch()` method. When the session is entered, the `launch()` method is called for each node in
    dependency order. The launch method returns either a callable (`run()` function) or None, raising an exception in
    case of an error. The sequence of non-None callables is stored by the Session. When Session.run() is called, the
    sequence of callables is called in order. If StopIteration is raised by the callable, it is removed from the sequence.
    The sequence is processed repeatedly until there are no more callables.

    Note that this does not rigorously handle races or deadlocks, or flexibility in automatically chasing dependencies. A more
    thorough implementation could recursively call launch on dependencies (launch could be idempotent or involve some
    signalling to dependents when complete), run calls could be entirely event driven, and/or nodes could "publish"
    output (including just a completion message), blocking for acknowledgement before looking for the next set of subscribed inputs.
    """

    def __init__(self, work=None, workdir_list=None):
        """Initialize compute resources.

        Appropriate computing resources need to be knowable when the Context is created.
        """
        # self.__context_array = list([Context(work_element) for work_element in work])
        self.__work = workflow.WorkSpec()
        self.__workdir_list = workdir_list

        self._session = None
        # This may not belong here. Is it confusing for the Context to have both global and local properties?
        # Alternatively, maybe a trivial `property` that gets the rank from a bound session, if any.
        self.rank = None

        # `size` notes the required width of an array of synchronous tasks to perform the specified work.
        # As work elements are processed, self.size will be increased as appropriate.
        self.size = None

        # initialize the operations map. May be extended during the lifetime of a Context.
        # Note that there may be a difference between built-in operations provided by this module and
        # additional operations registered at run time.
        self.__operations = {}
        # The map contains a builder for each operation. The builder is created by passing the element to the function
        # in the map. The object returned must have the following methods:
        #
        #   * add_subscriber(another_builder) : allow other builders to subscribe to this one.
        #   * build(dag) : Fulfill the builder responsibilities by adding an arbitrary number of nodes and edges to a Graph.
        #
        # The gmxapi namespace of operations should be consistent with a specified universal set of functionalities
        self.__operations['gmxapi'] = {'md': lambda element : self.__md(element),
                                       'global_data' : shared_data_maker,
                                      }
        # Even if TPR file loading were to become a common and stable enough operation to be specified in
        # and API, it is unlikely to be implemented by any code outside of GROMACS, so let's not clutter
        # a potentially more universal namespace.
        self.__operations['gromacs'] = {'load_tpr': lambda element : self.__load_tpr(element),
                                       }

        # Right now we are treating workspec elements and work DAG nodes as equivalent, but they are
        # emphatically not intended to be tightly coupled. The work specification is intended to be
        # simple, user-friendly, general, and easy-to-implement. The DAG is an implementation detail
        # and may differ across context types. It is likely to have stronger typing of nodes and/or
        # edges. It is not yet specified whether we should translate the work into a graph before, after,
        # or during processing of the elements, so it is not yet known whether we will need facilities
        # to allow cross-referencing between the two graph-type structures. If we instantiate API objects
        # as we process work elements, and the DAG in a context deviates from the work specification
        # topology, we would need to use named dependencies to look up objects to bind to. Such facilities
        # could be hidden in the WorkElement class(es), too, to delegate code away from the Context as a
        # container class growing without bounds...
        # In actuality, we will have to process the entire workspec to some degree to make sure we can
        # run it on the available resources.
        self.elements = None

        # This setter must be called after the operations map has been populated.
        self.work = work

    @property
    def work(self):
        return self.__work

    @work.setter
    def work(self, work):
        if work is None:
            warnings.warn("A Context without a valid WorkSpec is iffy...")
            return

        import importlib

        if isinstance(work, WorkSpec):
            workspec = work
        elif hasattr(work, 'workspec') and isinstance(work.workspec, WorkSpec):
            workspec = work.workspec
        else:
            raise ValueError('work argument must provide a gmx.workflow.WorkSpec.')
        workspec._context = self

        # Make sure this context knows how to run the specified work.
        for e in workspec.elements:
            element = gmx.workflow.WorkElement.deserialize(workspec.elements[e])


            if element.namespace not in {'gmxapi', 'gromacs'} and element.namespace not in self.__operations:
                # Non-built-in namespaces are treated as modules to import.
                try:
                    element_module = importlib.import_module(element.namespace)
                except ImportError as e:
                    raise exceptions.UsageError('This context does not know how to invoke {} from {}. ImportError: {}'.format(element.operation, element.namespace, e.message))

                # Don't leave an empty nested dictionary if we couldn't map the operation.
                if element.namespace in self.__operations:
                    namespace_map = self.__operations[element.namespace]
                else:
                    namespace_map = dict()

                if element.operation not in namespace_map:
                    try:
                        element_operation = getattr(element_module, element.operation)
                        namespace_map[element.operation] = element_operation
                    except:
                        raise exceptions.ApiError('Operation {} not found in {}.'.format(element.operation, element.namespace))
                    # Set or update namespace map only if we have something to contribute.
                    self.__operations[element.namespace] = namespace_map
            else:
                # The requested element is a built-in operation or otherwise already configured.
                # element.namespace should be mapped, but not all operations are necessarily implemented.
                assert element.namespace in self.__operations
                if not element.operation in self.__operations[element.namespace]:
                    if self.rank < 1:
                        logger.error(self.__operations)
                    # This check should be performed when deciding if the context is appropriate for the work.
                    # If we are just going to use a try/catch block for this test, then we should differentiate
                    # this exception from those raised due to incorrect usage.
                    # \todo Consider distinguishing API misuse from API failures.
                    raise exceptions.ApiError('Specified work cannot be performed due to unimplemented operation {}.{}.'.format(element.namespace, element.operation))

        self.__work = workspec

    def add_operation(self, namespace, operation, get_builder):
        """Add a builder factory to the operation map.

        Extends the known operations of the Context by mapping an operation in a namespace to a function
        that returns a builder to process a work element referencing the operation. Must be called before
        the work specification is added, since the spec is inspected to confirm that the Context can run it.

        It may be more appropriate to add this functionality to the Context constructor or as auxiliary
        information in the workspec, or to remove it entirely; it is straight-forward to just add snippets
        of code to additional files in the working directory and to make them available as modules for the
        Context to import.

        Example:

            >>> # Import some custom extension code.
            >>> import myplugin
            >>> myelement = myplugin.new_element()
            >>> workspec = gmx.workflow.WorkSpec()
            >>> workspec.add_element(myelement)
            >>> context = gmx.context.ParallelArrayContext()
            >>> context.add_operation(myelement.namespace, myelement.operation, myplugin.element_translator)
            >>> context.work = workspec
            >>> with get_context() as session:
            ...    session.run()

        """
        if namespace not in self.__operations:
            if namespace in {'gmxapi', 'gromacs'}:
                raise exceptions.UsageError("Cannot add operations to built-in namespaces.")
            else:
                self.__operations[namespace] = dict()
        else:
            assert namespace in self.__operations

        if operation in self.__operations[namespace]:
            raise exceptions.UsageError("Operation {}.{} already defined in this context.".format(namespace, operation))
        else:
            self.__operations[namespace][operation] = get_builder

    def __load_tpr(self, element):
        """Implement the gromacs.load_tpr operation.

        Updates the minimum width of the workflow parallelism. Stores a null API object.
        """
        class Builder(object):
            def __init__(self, tpr_list):
                logger.debug("Loading tpr builder for tpr_list {}".format(tpr_list))
                self.tpr_list = tpr_list
                self.subscribers = []
                self.width = len(tpr_list)

            def add_subscriber(self, builder):
                builder.infile = self.tpr_list
                self.subscribers.append(builder)

            def build(self, dag):
                width = len(self.tpr_list)
                for builder in self.subscribers:
                    builder.width = width
                if 'width' in dag.graph:
                    width = max(width, dag.graph['width'])
                dag.graph['width'] = width

        return Builder(element.params)

    def __md(self, element):
        """Implement the gmxapi.md operation by returning a builder that can populate a data flow graph for the element.

        Inspects dependencies to set up the simulation runner.

        The graph node created will have `launch` and `run` attributes with function references, and a `width`
        attribute declaring the workflow parallelism requirement.
        """

        class Builder(object):
            """Translate md work element to a node in the session's DAG."""
            def __init__(self, element):
                assert isinstance(element, workflow.WorkElement)
                self.name = element.name
                # Note that currently the calling code is in charge of subscribing this builder to its dependencies.
                # A list of tpr files will be set when the calling code subscribes this builder to a tpr provider.
                self.infile = None
                # Other dependencies in the element may register potentials when subscribed to.
                self.potential = []
                self.input_nodes = []
            def add_subscriber(self, builder):
                """The md operation does not yet have any subscribeable facilities."""
                pass
            def build(self, dag):
                """Add a node to the graph that, when launched, will construct a simulation runner.

                Complete the definition of appropriate graph edges for dependencies.

                The launch() method of the added node creates the runner from the tpr file for the current rank and adds
                modules from the incoming edges.
                """
                assert isinstance(dag, _Graph)
                name = self.name
                dag.add_node(name)
                for neighbor in self.input_nodes:
                    dag.add_edge(neighbor, name)
                infile = self.infile
                assert not infile is None
                potential_list = self.potential
                assert dag.graph['width'] >= len(infile)

                # Provide closure with which to execute tasks for this node.
                def launch(rank=None):
                    assert not rank is None
                    tpr_file = infile[rank]
                    logger.info('Loading TPR file: {}'.format(infile))
                    system = gmx.core.from_tpr(tpr_file)
                    dag.nodes[name]['system'] = system
                    for potential in potential_list:
                        system.add_potential(potential)
                    dag.nodes[name]['session'] = system.launch()
                    dag.nodes[name]['close'] = dag.nodes[name]['session'].close
                    def runner():
                        """Currently we only support a single call to run."""
                        def done():
                            raise StopIteration()
                        dag.nodes[name]['run'] = done
                        return dag.nodes[name]['session'].run()
                    dag.nodes[name]['run'] = runner
                    return dag.nodes[name]['run']

                dag.nodes[name]['launch'] = launch

        return Builder(element)

    def __enter__(self):
        """Implement Python context manager protocol, producing a Session for the specified work in this Context.

        Returns:
            Session object the can be run and/or inspected.

        Additional API operations are possible while the Session is active. When used as a Python context manager,
        the Context will close the Session at the end of the `with` block by calling `__exit__`.

        Note: this is probably where we will have to process the work specification to determine whether we
        have appropriate resources (such as sufficiently wide parallelism). Until we have a better Session
        abstraction, this means the clean approach should take two passes to first build a DAG and then
        instantiate objects to perform the work. In the first implementation, we kind of muddle things into
        a single pass.
        """

        from mpi4py import MPI

        if self._session is not None:
            raise exceptions.Error('Already running.')
        if self.work is None:
            raise exceptions.UsageError('No work to perform!')

        # Set up the global and local context.
        # Check the global MPI configuration
        communicator = MPI.COMM_WORLD
        comm_size = communicator.Get_size()
        self.rank = communicator.Get_rank()
        self._communicator = communicator

        assert not self.rank is None

        ###
        # Process the work specification.
        ###
        logger.debug("Processing workspec:\n{}".format(str(self.work)))

        # Get a builder for DAG components for each element
        builders = {}
        builder_sequence = []
        for element in self.work:
            # dispatch builders for operation implementations
            try:
                new_builder = self.__operations[element.namespace][element.operation](element)
                assert hasattr(new_builder, 'add_subscriber')
                assert hasattr(new_builder, 'build')

                logger.info("Collected builder for {}".format(element.name))
            except LookupError as e:
                request = '.'.join([element.namespace, element.operation])
                message = 'Could not find an implementation for the specified operation: {}. '.format(request)
                message += e.message
                raise exceptions.ApiError(message)
            # Subscribing builders is the Context's responsibility because otherwise the builders
            # don't know about each other. Builders should not depend on the Context unless they
            # are a facility provided by the Context, in which case they may be member functions
            # of the Context. We will probably need to pass at least some
            # of the Session to the `launch()` method, though...
            for name in element.depends:
                logger.info("Subscribing {} to {}.".format(element.name, name))
                builders[name].add_subscriber(new_builder)
            builders[element.name] = new_builder
            builder_sequence.append(element.name)

        # Call the builders in dependency order
        graph = _Graph(width=1)
        logger.info("Building sequence {}".format(builder_sequence))
        for name in builder_sequence:
            builder = builders[name]
            logger.debug("Building {}".format(builder))
            logger.debug("Has build attribute {}.".format(builder.build))
            builder.build(graph)
        self.size = graph.graph['width']

        # Prepare working directories. This should probably be moved to some aspect of the Session and either
        # removed from here or made more explicit to the user.
        workdir_list = self.__workdir_list
        if workdir_list is None:
            workdir_list = [os.path.join('.', str(i)) for i in range(self.size)]
        self.__workdir_list = list([os.path.abspath(dir) for dir in workdir_list])
        for dir in self.__workdir_list:
            if os.path.exists(dir):
                if not os.path.isdir(dir):
                    raise exceptions.FileError('{} is not a valid working directory.'.format(dir))
            else:
                os.mkdir(dir)

        # Check the session "width" against the available parallelism
        if (self.size > comm_size):
            raise exceptions.UsageError('ParallelArrayContext requires a work array that fits in the MPI communicator: array width {} > size {}.'.format(self.size, comm_size))
        if (self.size < comm_size):
            warnings.warn('MPI context is wider than necessary to run this work: array width {} vs. size {}.'.format(self.size, comm_size))

        print(graph)
        logger.debug(("Launching graph {}.".format(graph)))

        # launch() is currently a method of gmx.core.MDSystem and returns a gmxapi::Session.
        # MDSystem objects are obtained from gmx.core.from_tpr(). They also provide add_potential().
        # gmxapi::Session objects are exposed as gmx.core.MDSession and provide run() and close() methods.
        #
        # Here, I want to find the input appropriate for this rank and get an MDSession for it.
        # \todo In the future, we should set up an object with "ports" configured and then instantiate.
        # E.g. Make a pass that allows meta-objects to bind (setting md_proxy._input_tpr and md_proxy._plugins,
        # and then call a routine implemented by each object to run whatever protocol it needs, such
        # as `system = gmx.core.from_tpr(md._input_tpr); system.add_potential(md._plugins)
        if self.rank in range(self.size):
            logger.info("Launching work on rank {}.".format(self.rank))
            # Launch the work for this rank
            self.workdir = self.__workdir_list[self.rank]
            os.chdir(self.workdir)
            logger.info('rank {} changed directory to {}'.format(self.rank, self.workdir))
            sorted_nodes = nx.topological_sort(graph)
            runners = []
            closers = []
            for name in sorted_nodes:
                launcher = graph.nodes[name]['launch']
                runner = launcher(self.rank)
                if not runner is None:
                    runners.append(runner)
                    closers.append(graph.nodes[name]['close'])
            # Get a session object to return. It must simply provide a `run()` function.
            class Session(object):
                def __init__(self, runners, closers):
                    self.runners = list(runners)
                    self.closers = list(closers)

                def run(self):
                    # Note we are not following the documented protocol of running repeatedly yet.
                    to_be_deleted = []
                    for i, runner in enumerate(self.runners):
                        try:
                            runner()
                        except StopIteration:
                            to_be_deleted.insert(0, i)
                    for i in to_be_deleted:
                        del self.runners[i]

                def close(self):
                    for close in self.closers:
                        close()

            self._session = Session(runners, closers)
        else:
            # \todo We don't really want a None session so much as a session with no work.
            # self._session = None
            class NullSession(object):
                def run(self):
                    return gmx.Status()
                def close(self):
                    return
            self._session = NullSession()

        # Make sure session has started on all ranks before continuing?

        self._session.graph = graph
        return self._session

    def __exit__(self, exception_type, exception_value, traceback):
        """Implement Python context manager protocol."""
        # Todo: handle exceptions.
        # \todo: we should not have a None session but rather an API-compliant Session that just has no work.
        if self._session is not None:
            self._session.close()

        # \todo Make sure session has ended on all ranks before continuing and handle final errors.

        self._session = None
        return False

def get_context(work=None):
    """Get a concrete Context object.

    Args:
        work: runnable work as a valid gmx.workflow.WorkSpec object

    Returns:
        An object implementing the gmx.context.Context interface, if possible.

    Raises:
        gmx.exceptions.Error if an appropriate context for `work` could not be loaded.

    If work is provided, return a Context object capable of running the provided work or produce an error.

    The semantics for finding Context implementations needs more consideration, and a more informative exception
    is likely possible.

    A Context can run the provided work if

      * the Context supports can resolve all operations specified in the elements
      * the Context supports DAG topologies implied by the network of dependencies
      * the Context supports features required by the elements with the specified parameters, such as synchronous array jobs.
      * anything else?

    """
    from . import workflow
    import gmx.core

    context = None
    if work is None:
        # Create a new empty Context.
        # TBD: should there be a global "current context" or default? We'll have to see how this gets used.
        context = Context()
    elif isinstance(work, workflow.WorkSpec):
        # Assume simple simulation for now.

        # Get MD simulation elements.
        sims = [element for element in work if element.operation == 'md']
        if len(sims) != 1:
            raise exceptions.UsageError('gmx currently requires exactly one MD element in the work specification.')
        sim = sims[0]

        # Confirm the availability of dependencies.
        # Note we are not performing a full recursive check here because we are just preparing the sim.
        # A valid work specification requires dependencies to be defined.
        for dependency in sim.depends:
            assert dependency in work.elements

        # If all is well, bind the work to a Context object and prepare the Context to be able to launch a session.
        tpr_input = None
        for dependency in sim.depends:
            element = workflow.WorkElement.deserialize(work.elements[dependency])
            if element.operation == 'load_tpr':
                if tpr_input is None:
                    tpr_input = list(element.params)
                else:
                    raise exceptions.ApiError('This Context can only handle work specifications with a single load_tpr operation.')
        if tpr_input is None:
            raise exceptions.UsageError('Work specification does not provide any input for MD simulation.')
        if len(tpr_input) != 1:
            raise exceptions.UsageError('This Context does not support arrays of simulations.')


        # Use old-style constructor that takes gmx.core.MDSystem
        newsystem = gmx.core.from_tpr(tpr_input[0])
        context = Context(newsystem)
    else:
        raise exceptions.UsageError('Argument to get_context must be a runnable gmx.workflow.WorkSpec object.')
    return context
