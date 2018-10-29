"""
Execution Context
=================
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['Context', 'DefaultContext']

import importlib
import os
import warnings
import networkx as nx
from networkx import DiGraph as _Graph
import tempfile

from gmx import exceptions
from gmx import logging
from gmx import status

# Module-level logger
logger = logging.getLogger(__name__)
logger.info('Importing gmx.context')


def _load_tpr(self, element):
    """Implement the gromacs.load_tpr operation.

    Updates the minimum width of the workflow parallelism. Does not add any API object to the graph.

    Arguments:
        self: The Context in which this operation is being loaded.
        element: WorkElement specifying the operation.

    Returns:
        A Director that the Context can use in launching the Session.
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

    return Builder(element.params['input'])

def _md(context, element):
    """Implement the gmxapi.md operation by returning a builder that can populate a data flow graph for the element.

    Inspects dependencies to set up the simulation runner.

    The graph node created will have `launch` and `run` attributes with function references, and a `width`
    attribute declaring the workflow parallelism requirement.

    Arguments:
        context: The Context in which this operation is being loaded.
        element: WorkElement specifying the operation.

    Returns:
        A Director that the Context can use in launching the Session.
    """
    import gmx.core
    class Builder(object):
        """Translate md work element to a node in the session's DAG."""
        def __init__(self, element):
            try:
                self.name = element.name
                # Note that currently the calling code is in charge of subscribing this builder to its dependencies.
                # A list of tpr files will be set when the calling code subscribes this builder to a tpr provider.
                self.infile = None
                # Other dependencies in the element may register potentials when subscribed to.
                self.potential = []
                self.input_nodes = []
                self.runtime_params = element.params
            except AttributeError:
                raise exceptions.ValueError("object provided does not seem to be a WorkElement.")
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

                # Copy and update, if required by `end_time` parameter.
                temp_filename = None
                if 'end_time' in self.runtime_params:
                    # Note that mkstemp returns a file descriptor as the first part of the tuple.
                    # We can make this cleaner in 0.0.7 with a separate node that manages the
                    # altered input.
                    _, temp_filename = tempfile.mkstemp(suffix='.tpr')
                    logger.debug('Updating input. Using temp file {}'.format(temp_filename))
                    gmx.core.copy_tprfile(source=infile[rank],
                                          destination=temp_filename,
                                          end_time=self.runtime_params['end_time'])
                    tpr_file = temp_filename
                else:
                    tpr_file = infile[rank]

                logger.info('Loading TPR file: {}'.format(tpr_file))
                system = gmx.core.from_tpr(tpr_file)
                dag.nodes[name]['system'] = system
                for potential in potential_list:
                    system.add_mdmodule(potential)
                pycontext = element.workspec._context
                pycontext.potentials = potential_list
                mdargs = gmx.core.MDArgs()
                mdargs.set(self.runtime_params)
                context = pycontext._api_object
                context.setMDArgs(mdargs)
                dag.nodes[name]['session'] = system.launch(context)
                dag.nodes[name]['close'] = dag.nodes[name]['session'].close

                if 'end_time' in self.runtime_params:
                    def special_close():
                        dag.nodes[name]['session'].close()
                        logger.debug("Unlinking temporary TPR file {}.".format(temp_filename))
                        os.unlink(temp_filename)
                    dag.nodes[name]['close'] = special_close
                else:
                    dag.nodes[name]['close'] = dag.nodes[name]['session'].close

                def runner():
                    """Currently we only support a single call to run."""
                    def done():
                        raise StopIteration()
                    # Replace the runner with a stop condition for subsequent passes.
                    dag.nodes[name]['run'] = done
                    return dag.nodes[name]['session'].run()
                dag.nodes[name]['run'] = runner
                return dag.nodes[name]['run']

            dag.nodes[name]['launch'] = launch

    return Builder(element)


def _get_mpi_ensemble_communicator(session_communicator, ensemble_size):
    """Get an ensemble communicator from an MPI communicator.

    An ensemble communicator is an object that implements mpi4py.MPI.Comm methods
    as described elsewhere in this documentation.

    :param session_communicator: MPI communicator with the interface described by mpi4py.MPI.Comm
    :param ensemble_size: number of ensemble members
    :return: communicator of described size on participating ranks and null communicator on any others.

    Must be called exactly once in every process in `communicator`. It is the
    responsibility of the calling code to refrain from running ensemble operations
    if not part of the ensemble. The calling code determines this by comparing its
    session_communicator.Get_rank() to ensemble_size. This is not a good solution
    because it assumes there is a single ensemble communicator and that ensemble
    work is allocated to ranks serially from session_rank 0. Future work might
    use process groups associated with specific operations in the work graph so
    that processes can check for membership in a group to decide whether to use
    their ensemble communicator. Another possibility would be to return None
    rather than a null communicator in processes that aren't participating in
    a given ensemble.
    """
    from mpi4py import MPI

    session_size = session_communicator.Get_size()
    session_rank = session_communicator.Get_rank()

    # Check the ensemble "width" against the available parallelism
    if ensemble_size > session_size:
        msg = 'ParallelArrayContext requires a work array that fits in the MPI communicator: '
        msg += 'array width {} > size {}.'
        msg = msg.format(ensemble_size, session_size)
        raise exceptions.UsageError(msg)
    if ensemble_size < session_size:
        msg = 'MPI context is wider than necessary to run this work:  array width {} vs. size {}.'
        warnings.warn(msg.format(ensemble_size, session_size))

    # Create an appropriate sub-communicator for the present work. Extra ranks will be in a
    # sub-communicator with no work.
    if session_rank < ensemble_size:
        # The session launcher should maintain an inventory of the ensembles and
        # provide an appropriate tag, but right now we just have a sort of
        # Boolean: ensemble or not.
        color = 0
    else:
        color = MPI.UNDEFINED

    ensemble_communicator = session_communicator.Split(color, session_rank)
    try:
        ensemble_communicator_size = ensemble_communicator.Get_size()
        ensemble_communicator_rank = ensemble_communicator.Get_rank()
    except:
        warnings.warn("Possible API programming error: ensemble_communicator does not provide required methods...")
        ensemble_communicator_size = 0
        ensemble_communicator_rank = None
    logger.info("Session rank {} assigned to rank {} of subcommunicator {} of size {}".format(
        session_rank,
        ensemble_communicator_rank,
        ensemble_communicator,
        ensemble_communicator_size
    ))

    # There isn't a good reason to worry about special handling for a null communicator,
    # which we have to explicitly avoid "free"ing, so let's just get rid of it.
    # To do: don't even get the null communicator in the first place. Use a group and create instead of split.
    if ensemble_communicator == MPI.COMM_NULL:
        ensemble_communicator = None

    return ensemble_communicator


def _acquire_communicator(communicator=None):
    """Get a workflow level communicator for the session.

    This function is intended to be called by the __enter__ method that creates
    a session get a communicator instance. The `Free` method of the returned
    instance must be called exactly once. This should be performed by the
    corresponding __exit__ method.

    Arguments:
        communicator : a communicator to duplicate (optional)

    Returns:
        A communicator that must be explicitly freed by the caller.

    Currently only supports MPI multi-simulation parallelism dependent on
    mpi4py. The mpi4py package should be installed and built with compilers
    that are compatible with the gmxapi installation.

    If provided, `communicator` must provide the mpi4py.MPI.Comm interface.
    Returns either a duplicate of `communicator` or of MPI_COMM_WORLD if mpi4py
    is available. Otherwise, returns a mock communicator that can only manage
    sessions and ensembles of size 0 or 1.

    gmx behavior is undefined if launched with mpiexec and without mpi4py
    """

    class MockSessionCommunicator(object):
        def Dup(self):
            return self

        def Free(self):
            return

        def Get_size(self):
            return 1

        def Get_rank(self):
            return 0

        def __str__(self):
            return 'Basic'

        def __repr__(self):
            return 'MockSessionCommunicator()'

    if communicator is None:
        try:
            import mpi4py.MPI as MPI
            communicator = MPI.COMM_WORLD
        except ImportError:
            logger.info("mpi4py is not available for default session communication.")
            communicator = MockSessionCommunicator()
    else:
        communicator = communicator

    try:
        new_communicator = communicator.Dup()
    except Exception as e:
        message = "Exception when duplicating communicator: {}".format(e)
        raise exceptions.ApiError(message)

    return new_communicator


def _get_ensemble_communicator(communicator, ensemble_size):
    """Provide ensemble_communicator feature in active_context, if possible.

    Must be called on all ranks in `communicator`. The communicator returned
    must be freed by a call to its `Free()` instance method. This function is
    best used in a context manager's `__enter__()` method so that the
    corresponding `context.Free()` can be called in the `__exit__` method.

    Arguments:
        communicator : session communicator for the session with the ensemble.
        ensemble_size : ensemble size of the requested ensemble communicator

    The ensemble_communicator feature should be present if the Context can
    provide communication between all ensemble members. The Context should
    determine this at the launch of the session and set the
    ``_session_ensemble_communicator`` attribute to provide an object that
    implements the same interface as an mpi4py.MPI.Comm object. Actually, this is
    a temporary shim, so the only methods that need to be available are `Get_size`,
    `Get_rank` and something that can be called as
    Allreduce(send, recv) where send and recv are objects providing the Python
    buffer interface.

    Currently, only one ensemble can be managed in a session.
    """
    ensemble_communicator = None

    class TrivialEnsembleCommunicator(object):
        def __init__(self):
            import numpy
            self._numpy = numpy

        def Free(self):
            return

        def Allreduce(self, send, recv):
            logger.debug("Faking an Allreduce for ensemble of size 1.")
            send_buffer = self._numpy.array(send, copy=False)
            recv_buffer = self._numpy.array(recv, copy=False)
            recv_buffer[:] = send_buffer[:]

        def Get_size(self):
            return 1

        def Get_rank(self):
            return 0

    # For trivial cases, don't bother trying to use MPI
    # Note: all ranks in communicator must agree on the size of the work!
    # Note: If running with a Mock session communicator in an MPI session (user error)
    # every rank will think it is the only rank and will try to perform the
    # same work.
    if communicator.Get_size() <= 1 or ensemble_size <= 1:
        message = "Getting TrivialEnsembleCommunicator for ensemble of size {}".format((ensemble_size))
        message += " for session rank {} in session communicator of size {}".format(
            communicator.Get_rank(),
            communicator.Get_size())
        logger.debug(message)
        ensemble_communicator = TrivialEnsembleCommunicator()
    else:
        message = "Getting an MPI subcommunicator for ensemble of size {}".format(ensemble_size)
        message += " for session rank {} in session communicator of size {}".format(
            communicator.Get_rank(),
            communicator.Get_size())
        logger.debug(message)
        ensemble_communicator = _get_mpi_ensemble_communicator(communicator, ensemble_size)

    return ensemble_communicator

def _get_ensemble_update(context):
    """Set up a simple ensemble resource.

    The context should call this function once per session to get an `ensemble_update`
    function object.

    This is a draft of a Context feature that may not be available in all
    Context implementations. This factory function can be wrapped as a
    ``ensemble_update`` "property" in a Context instance method to produce a Python function
    with the signature ``update(context, send, recv, tag=None)``.

    This feature requires that the Context is capabable of providing the
    ensemble_communicator feature and the numpy feature.
    If both are available, the function object provided by
    ``ensemble_update`` provides
    the ensemble reduce operation used by the restraint potential plugin in the
    gmxapi sample_restraint repository. Otherwise, the provided function object
    will log an error and then raise an exception.

    gmxapi 0.0.5 and 0.0.6 MD plugin clients look for a member function named
    ``ensemble_update`` in the Context that launched them. In the future,
    clients will use session resources to access ensemble reduce operations.
    In the mean time, a transitional implementation can involve defining a
    ``ensemble_update`` property in the Context object that acts as a factory
    function to produce the reducing operation, if possible with the given
    resources.
    """
    try:
        import numpy
    except ImportError:
        message = "ensemble_update requires numpy, but numpy is not available."
        logger.error(message)
        raise exceptions.FeatureNotAvailableError(message)

    def _ensemble_update(active_context, send, recv, tag=None):
        assert not tag is None
        assert str(tag) != ''
        if not tag in active_context.part:
            active_context.part[tag] = 0
        logger.debug("Performing ensemble update.")
        active_context._session_ensemble_communicator.Allreduce(send, recv)
        buffer = numpy.array(recv, copy=False)
        buffer /= active_context.work_width
        suffix = '_{}.npz'.format(tag)
        # These will end up in the working directory and each ensemble member will have one
        filename = str("rank{}part{:04d}{}".format(active_context.rank, int(active_context.part[tag]), suffix))
        numpy.savez(filename, recv=recv)
        active_context.part[tag] += 1

    def _no_ensemble_update(active_context, send, recv, tag=None):
        message = "Attempt to call ensemble_update() in a Context that does not provide the operation."
        # If we confirm effective exception handling, remove the extraneous log.
        logger.error(message)
        raise exceptions.FeatureNotAvailableError(message)

    if context._session_ensemble_communicator is not None:
        functor = _ensemble_update
    else:
        functor = _no_ensemble_update
    context.part = {}
    return functor


class _libgromacsContext(object):
    """Low level API to libgromacs library context provides Python context manager.

    Binds to a workflow and manages computation resources.

    Attributes:
        workflow (:obj:`gmx.workflow.WorkSpec`): bound workflow to be executed.

    Example:
        >>> with _libgromacsContext(my_workflow) as session: # doctest: +SKIP
        ...    session.run()

    Things are still fluid, but what we might do is have all of the WorkSpec operations that are supported
    by a given Context to correspond to member functions in the Context, a SessionBuilder, or Session. In
    any case, the operations allow a Context implementation to transform a work specification into a
    directed acyclic graph of schedulable work.
    """
    # The Context is the appropriate entity to own or mediate access to an appropriate logging facility,
    # but right now we are using the module-level Python logger.
    # Reference https://github.com/kassonlab/gmxapi/issues/135
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
        from gmx.workflow import workspec_version, get_source_elements, WorkElement
        # initialize return value.
        is_valid = True
        # Check compatibility
        if workspec.version != workspec_version:
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
        sources = set([element.name for element in get_source_elements(workspec)])
        if len(sources) < 1:
            is_valid = False
            if raises:
                raise exceptions.ApiError('WorkSpec must contain at least one source element')
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
            # launch() with no arguments is deprecated.
            # Ref: https://github.com/kassonlab/gmxapi/issues/124
            self._session = self.workflow.launch()
        except:
            self._session = None
            raise
        return self._session

    def __exit__(self, exception_type, exception_value, traceback):
        """Implement Python context manager protocol.

        Closing a session should not produce Python exceptions. Instead, exit
        state is accessible through API objects like Status.
        For evolving design points, see
        - https://github.com/kassonlab/gmxapi/issues/41
        - https://github.com/kassonlab/gmxapi/issues/121
        """
        self._session.close()
        self._session = None
        return False


class DefaultContext(_libgromacsContext):
    """ Produce an appropriate context for the work and compute environment.

    Deprecated:
        Use gmx.context.get_context() to find an appropriate high-level API
        context. For lower-level access to the library that does not employ the
        full API Context abstraction, but instead explicitly uses a local
        libgromacs instance, a replacement still needs to be devised. It may
        have this same interface, but the name and scoping of DefaultContext is
        misleading.
    """
    def __init__(self, work):
        # There is very little context abstraction at this point...
        super(DefaultContext, self).__init__(work)

# Unused.
# Reference https://github.com/kassonlab/gmxapi/issues/36
# def shared_data_maker(element):
#     """Make a shared data element for use by dependent nodes.
#
#     This version uses mpi4py to share data and supports a single downstream node.
#
#     The element provides a serialized argument list for numpy.empty() as two elements, args, and kwargs. Each
#     subscriber receives such
#     an array at launch along with a python function handle to call-back to at some interval (passed to
#     the plugin C++ code).
#     """
#
#     # New idea: Instead of being dependent on a shared data node, let participants add a downstream node
#     # that performs the reduce operation. A context can determine unsuitability for this parallelism with
#     # lack of support for a reduce with a period less than the length of the specified trajectories.
#     # To support reduce operations for ensembles wider than the Context, the Context could provide an
#     # additional tier in the reduction for batches of co-scheduled tasks.
#
#     import json
#
#     class Builder(object):
#         def __init__(self, element):
#             logger.debug("Processing element {}".format(element.serialize()))
#             self.context = element.workspec._context
#             self.rank = self.context.rank
#             self.subscriber = None
#             self.name = element.name
#             params = element.params
#             # Params contains a dictionary of kwargs
#             logger.debug("Processing parameters {}".format(params))
#             assert isinstance(params, dict)
#             kwargs = {name: params[name] for name in params}
#             self.args = kwargs['args']
#             self.kwargs = kwargs['kwargs']
#
#             # The builder can hold an updater to be provided to the subscriber at launch. The updater is
#             # a function reference that the user provides to perform a desired periodic action. Not sure
#             # how this will work in the future. Allowing arbitrary Python code to be provided during job
#             # configuration would be the hardest thing. The updater could be another user-provided operation.
#             # Hopefully we can provided some canned behaviors that can be selected with element parameters.
#             # Maybe both.
#             #self.updater = None
#
#         def add_subscriber(self, builder):
#             # At this point, we could find out how this data will be used (e.g. subscribing ranks)
#             if self.subscriber is None:
#                 self.subscriber = builder
#             else:
#                 raise exceptions.ApiError("This element does not support multiple consumers")
#
#         def build(self, dag):
#             # Either the builder needs to get the key for the subscribed node(s) so that we can
#             # create the edge now, or this builder needs to provide subscribers with the key of this
#             # DAG node so that the subscriber can create the edge. I think I prefer the latter, so that
#             # edge creation is tied to the binding process of a new node with its upstream nodes.
#             nodename = self.name
#             dag.add_node(nodename)
#             self.node = dag.nodes[nodename]
#
#             self.node['launch'] = self.__launch
#             # To avoid ambiguity, let's assert that only nodes that are active at launch will have data.
#             self.node['data'] = None
#             self.subscriber.input_nodes.append(nodename)
#             self.node['launch'] = self.__launch
#
#         def __launch(self, rank=None):
#             """Create the shared data resource for subscribed builders.
#
#             This is the place to provide subscribers with API references for interacting with
#             the shared data facility.
#             """
#             import numpy
#             data = numpy.empty(*self.args, **self.kwargs)
#             self.node['data'] = data
#             self.comm = self.context._communicator
#             self.node['comm'] = self.context._session_ensemble_communicator
#             # self.subscriber.shared_data_updater = self.updater
#             self.subscribinging_ranks = list(range(self.subscriber.width))
#
#             # Later, we can offload consumer responsibilities and the updater function to this runner,
#             # but we aren't there yet.
#             runner = None
#             return runner
#
#     builder = Builder(element)
#     return builder


class Context(object):
    """Manage an array of simulation work executing in parallel.

    This is the first implementation of a new style of Context class that has some extra abstraction
    and uses the new WorkSpec idea.

    Additional facilities are available to elements of the array members.

      * array element corresponding to work in the current sub-context
      * "global" resources managed by the ParallelArrayContext

    Attributes:
        work :obj:`gmx.workflow.WorkSpec`: specification of work to be performed when a session is launched.
        rank : numerical index of the current worker in a running session (None if not running)
        work_width : Minimum width needed for the parallelism required by the array of work being executed.
        elements : dictionary of references to elements of the workflow.

    `rank`, `work_width`, and `elements` are empty or None until the work is processed, as during session launch.


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

    def __init__(self, work=None, workdir_list=None, communicator=None):
        """Create manager for computing resources.

        Does not initialize resources because Python objects by themselves do
        not have a good way to deinitialize resources. Instead, resources are
        initialized using the Python context manager protocol when sessions are
        entered and exited.

        Appropriate computing resources need to be knowable when the Context is created.

        Keyword Arguments:
            work : work specification with which to initialize this context
            workdir_list : deprecated
            communicator : non-owning reference to a multiprocessing communicator

        If provided, communicator must implement the mpi4py.MPI.Comm interface. The
        Context will use this communicator as the parent for subcommunicators
        used when launching sessions. If provided, communicator is owned by the
        caller, and must be freed by the caller after any sessions are closed.
        By default, the Context will get a reference to MPI_COMM_WORLD, which
        will be freed when the Python process ends and cleans up its resources.
        The communicator stored by the Context instance will not be used directly,
        but will be duplicated when launching sessions using `with`.
        """

        # self.__context_array = list([Context(work_element) for work_element in work])
        from gmx.workflow import WorkSpec
        import gmx.core

        # Until better Session abstraction exists at the Python level, a
        # _session_communicator attribute will be added to and removed from the
        # context at session entry and exit. If necessary, a _session_ensemble_communicator
        # will be split from _session_communicator for simulation ensembles
        # present in the specified work.
        self.__communicator = communicator

        self.__work = WorkSpec()
        self.__workdir_list = workdir_list

        self._session = None
        # This may not belong here. Is it confusing for the Context to have both global and local properties?
        # Alternatively, maybe a trivial `property` that gets the rank from a bound session, if any.
        self.rank = None

        # `work_width` notes the required width of an array of synchronous tasks to perform the specified work.
        # As work elements are processed, self.work_width will be increased as appropriate.
        self.work_width = None

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
        self.__operations['gmxapi'] = {'md': lambda element : _md(self, element),
                                       # 'global_data' : shared_data_maker,
                                      }
        # Even if TPR file loading were to become a common and stable enough operation to be specified in
        # and API, it is unlikely to be implemented by any code outside of GROMACS, so let's not clutter
        # a potentially more universal namespace.
        self.__operations['gromacs'] = {'load_tpr': lambda element : _load_tpr(self, element),
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

        self._api_object = gmx.core.Context()

    @property
    def work(self):
        return self.__work

    @work.setter
    def work(self, work):
        """Set `work` attribute.

        Raises:
            gmx.exceptions.ApiError: work is not compatible with schema or
                known operations.
            gmx.exceptions.UsageError: Context can not access operations in
                the name space given for an Element
            gmx.exceptions.ValueError: assignment operation cannot be performed
                for the provided object (rhs)

        For discussion on error handling, see https://github.com/kassonlab/gmxapi/issues/125
        """
        from gmx.workflow import WorkSpec, WorkElement
        if work is None:
            return

        if isinstance(work, WorkSpec):
            workspec = work
        elif hasattr(work, 'workspec') and isinstance(work.workspec, WorkSpec):
            workspec = work.workspec
        else:
            raise exceptions.ValueError('work argument must provide a gmx.workflow.WorkSpec.')
        workspec._context = self

        # Make sure this context knows how to run the specified work.
        for e in workspec.elements:
            element = WorkElement.deserialize(workspec.elements[e])

            if element.namespace not in {'gmxapi', 'gromacs'} and element.namespace not in self.__operations:
                # Non-built-in namespaces are treated as modules to import.
                try:
                    element_module = importlib.import_module(element.namespace)
                except ImportError as e:
                    raise exceptions.UsageError(
                        'This context does not know how to invoke {} from {}. ImportError: {}'.format(
                            element.operation,
                            element.namespace,
                            str(e)))

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
                        raise exceptions.ApiError('Operation {} not found in {}.'.format(element.operation,
                                                                                         element.namespace))
                    # Set or update namespace map only if we have something to contribute.
                    self.__operations[element.namespace] = namespace_map
            else:
                # The requested element is a built-in operation or otherwise already configured.
                # element.namespace should be mapped, but not all operations are necessarily implemented.
                assert element.namespace in self.__operations
                if not element.operation in self.__operations[element.namespace]:
                    if self.rank < 1:
                        logger.error("Operation {} not found in map {}".format(element.operation,
                                                                               str(self.__operations)))
                    # This check should be performed when deciding if the context is appropriate for the work.
                    # If we are just going to use a try/catch block for this test, then we should differentiate
                    # this exception from those raised due to incorrect usage.
                    # The exception thrown here may evolve with https://github.com/kassonlab/gmxapi/issues/125
                    raise exceptions.ApiError(
                        'Specified work cannot be performed due to unimplemented operation {}.{}.'.format(
                            element.namespace,
                            element.operation))

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

    # Set up a simple ensemble resource
    # This should be implemented for Session, not Context, and use an appropriate subcommunicator
    # that is created and freed as the Session launches and exits.
    def ensemble_update(self, send, recv, tag=None):
        """Implement the ensemble_update member function that gmxapi through 0.0.6 expects.

        """
        # gmxapi through 0.0.6 expects to bind to this member function during "build".
        # This behavior needs to be deprecated (bind during launch, instead), but this
        # dispatching function should be an effective placeholder.
        if tag is None or str(tag) == '':
            raise exceptions.ApiError("ensemble_update must be called with a name tag.")
        # __ensemble_update is an attribute, not an instance function, so we need to explicitly pass 'self'
        return self.__ensemble_update(self, send, recv, tag)

    def __enter__(self):
        """Implement Python context manager protocol, producing a Session for the specified work in this Context.

        Returns:
            Session object that can be run and/or inspected.

        Additional API operations are possible while the Session is active. When used as a Python context manager,
        the Context will close the Session at the end of the `with` block by calling `__exit__`.

        Note: this is probably where we will have to process the work specification to determine whether we
        have appropriate resources (such as sufficiently wide parallelism). Until we have a better Session
        abstraction, this means the clean approach should take two passes to first build a DAG and then
        instantiate objects to perform the work. In the first implementation, we kind of muddle things into
        a single pass.
        """
        # Cache the working directory from which we were launched so that __exit__() can give us proper context
        # management behavior.
        self.__initial_cwd = os.getcwd()
        logger.debug("Launching session from {}".format(self.__initial_cwd))

        if self._session is not None:
            raise exceptions.Error('Already running.')
        if self.work is None:
            raise exceptions.UsageError('No work to perform!')

        # Set up the global and local context.
        # Check the global MPI configuration
        # Since the Context doesn't have a destructor, if we use an MPI communicator at this scope then
        # it has to be owned and managed outside of Context.
        self._session_communicator = _acquire_communicator(self.__communicator)
        context_comm_size = self._session_communicator.Get_size()
        context_rank = self._session_communicator.Get_rank()
        self.rank = context_rank
        # self._communicator = communicator
        logger.debug("Context rank {} in context {} of size {}".format(context_rank,
                                                                       self._session_communicator,
                                                                       context_comm_size))

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
                message += str(e)
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
        # Note: session_communicator is available, but ensemble_communicator has not been created yet.
        graph = _Graph(width=1)
        logger.info("Building sequence {}".format(builder_sequence))
        for name in builder_sequence:
            builder = builders[name]
            logger.info("Building {}".format(builder))
            logger.debug("Has build attribute {}.".format(builder.build))
            builder.build(graph)
        self.work_width = graph.graph['width']

        # Prepare working directories. This should probably be moved to some aspect of the Session and either
        # removed from here or made more explicit to the user.
        workdir_list = self.__workdir_list
        if workdir_list is None:
            workdir_list = [os.path.join('.', str(i)) for i in range(self.work_width)]
        self.__workdir_list = list([os.path.abspath(dir) for dir in workdir_list])

        # For gmxapi 0.0.6, all ranks have a session_ensemble_communicator
        self._session_ensemble_communicator = _get_ensemble_communicator(self._session_communicator, self.work_width)
        self.__ensemble_update = _get_ensemble_update(self)

        # launch() is currently a method of gmx.core.MDSystem and returns a gmxapi::Session.
        # MDSystem objects are obtained from gmx.core.from_tpr(). They also provide add_potential().
        # gmxapi::Session objects are exposed as gmx.core.MDSession and provide run() and close() methods.
        #
        # Here, I want to find the input appropriate for this rank and get an MDSession for it.
        # E.g. Make a pass that allows meta-objects to bind (setting md_proxy._input_tpr and md_proxy._plugins,
        # and then call a routine implemented by each object to run whatever protocol it needs, such
        # as `system = gmx.core.from_tpr(md._input_tpr); system.add_potential(md._plugins)
        # For future design plans, reference https://github.com/kassonlab/gmxapi/issues/65
        #
        # This `if` condition is currently the thing that ultimately determines whether the
        # rank attempts to do work.
        if context_rank < self.work_width:
            # print(graph)
            logger.debug(("Launching graph {}.".format(graph.graph)))
            logger.debug("Graph nodes: {}".format(str(list(graph.nodes))))
            logger.debug("Graph edges: {}".format(str(list(graph.edges))))

            logger.info("Launching work on context rank {}, subcommunicator rank {}.".format(
                self.rank,
                self._session_ensemble_communicator.Get_rank()))

            # Launch the work for this rank
            self.workdir = self.__workdir_list[self.rank]
            if os.path.exists(self.workdir):
                if not os.path.isdir(self.workdir):
                    raise exceptions.FileError('{} is not a valid working directory.'.format(self.workdir))
            else:
                os.mkdir(self.workdir)
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
                        logger.debug("Closing node: {}".format(close))
                        close()

            self._session = Session(runners, closers)
        else:
            logger.info("Context rank {} has no work to do".format(self.rank))
            class NullSession(object):
                def run(self):
                    logger.info("Running null session on rank {}.".format(self.rank))
                    return status.Status()
                def close(self):
                    logger.info("Closing null session.")
                    return
            self._session = NullSession()
            self._session.rank = self.rank

        # Make sure session has started on all ranks before continuing?

        self._session.graph = graph
        return self._session

    def __exit__(self, exception_type, exception_value, traceback):
        """Implement Python context manager protocol."""
        logger.info("Exiting session on context rank {}.".format(self.rank))
        if self._session is not None:
            logger.info("Calling session.close().")
            self._session.close()
            self._session = None
        else:
            # Note: we should not have a None session but rather an API-compliant Session that just has no work.
            # Reference: https://github.com/kassonlab/gmxapi/issues/41
            logger.info("No _session known to context or session already closed.")
        if hasattr(self, '_session_ensemble_communicator'):
            if self._session_communicator is not None:
                logger.info("Freeing sub-communicator {} on rank {}".format(
                    self._session_ensemble_communicator,
                    self.rank))
                self._session_ensemble_communicator.Free()
            else:
                logger.debug('"None" ensemble communicator does not need to be "Free"d.')
            del self._session_ensemble_communicator
        else:
            logger.debug("No ensemble subcommunicator on context rank {}.".format(self.rank))

        logger.debug("Freeing session communicator.")
        self._session_communicator.Free()
        logger.debug("Deleting session communicator reference.")
        del self._session_communicator

        os.chdir(self.__initial_cwd)
        logger.info("Session closed on context rank {}.".format(self.rank))
        # Note: Since sessions running in different processes can have different work, sessions have not necessarily
        # ended on all ranks. As a result, starting another session on the same resources could block until the
        # resources are available.

        # Python context managers return False when there were no exceptions to handle.
        return False


# The interface and functionality of ParallelArrayContext is the new generic
# Context behavior, but we need to keep the old name for compatibility for
# the moment.
ParallelArrayContext = Context

def get_context(work=None):
    """Get a concrete Context object.

    Args:
        work (gmx.workflow.WorkSpec): runnable work as a valid gmx.workflow.WorkSpec object

    Returns:
        An object implementing the gmx.context.Context interface, if possible.

    Raises:
        gmx.exceptions.ValueError if an appropriate context for `work` could not be loaded.

    If work is provided, return a Context object capable of running the provided work or produce an error.

    The semantics for finding Context implementations needs more consideration, and a more informative exception
    is likely possible.

    A Context can run the provided work if

      * the Context supports can resolve all operations specified in the elements
      * the Context supports DAG topologies implied by the network of dependencies
      * the Context supports features required by the elements with the specified parameters,
        such as synchronous array jobs.
      * anything else?

    """
    # We need to define an interface for WorkSpec objects so that we don't need
    # to rely on typing and inter-module dependencies.
    from gmx import workflow
    workspec = None
    if work is not None:
        if isinstance(work, workflow.WorkSpec):
            workspec = work
        elif hasattr(work, 'workspec') and isinstance(work.workspec,
                                                      workflow.WorkSpec):
            workspec = work.workspec
        else:
            raise exceptions.ValueError('work argument must provide a gmx.workflow.WorkSpec.')
    if workspec is not None and \
            hasattr(workspec, '_context') and \
            workspec._context is not None:
        context = workspec._context
    else:
        context = Context(work=workspec)

    return context
