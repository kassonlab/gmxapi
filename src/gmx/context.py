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

from gmx import exceptions
from gmx import logging
import gmx.core
from . import workflow
from .workflow import WorkSpec

# Module-level logger
logger = logging.getLogger(__name__)
logger.info("Importing gmx.context")

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
    # The Context is the appropriate entity to own or mediate access to an appropriate logging facility.
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
                raise exceptions.ApiError("Incompatible workspec version.")
        # Check that Elements are uniquely identifiable.
        elements = dict()
        for element in workspec.elements:
            if element.name is not None and element.name not in elements:
                elements[element.name] = element
            else:
                is_valid = False
                if raises:
                    raise exceptions.ApiError("WorkSpec must contain uniquely named elements.")
        # Check that the specification is complete. There must be at least one source element and all
        # dependencies must be fulfilled.
        sources = set([element.name for element in gmx.workflow.get_source_elements(workspec)])
        if len(sources) < 1:
            is_valid = False
            if raises:
                raise exceptions.ApiError("WorkSpec must contain at least one source element")
        for name in workspec.elements:
            element = gmx.workflow.WorkElement.deserialize()
        return is_valid


    def __enter__(self):
        """Implement Python context manager protocol.

        Returns:
            runnable session object.
        """
        if self._session is not None:
            raise exceptions.Error("Already running.")
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
            raise ValueError("work specification should be a Python list.")
        self.__context_array = list([DefaultContext(work_element) for work_element in work])
        self._session = None

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
        elements : dictionary of references to running elements of the workflow.

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
        ...    print("Worker {} produced {}".format(rank, output_path))
        ...

    One proposal would be that using a Context as a Python context manager would be optional. Context.launch() produces
    an object with __enter__() and __exit__() to get a session handle, but if these are not called, as by ``with``, then
    the object produced by launch() attempts to resolve the work it is responsible for during __del__(). This seems
    problematic and un-Pythonic, though. I think we just need to go with the original plan of having some slight
    specializations of session classes produced by different contexts and a little extra wrapping to abstract the
    context management related stuff from the lower level stuff.

    \todo ParallelArrayContext should not operate on an array of work objects, but on a work object representing a job array.
    Ultimately, a job array is just a workflow graph that contains multiple pipelines. We don't need to make special
    provisions for the case where the pipelines have no interdependencies, because that is just a trivial version of the
    more general case in which the array of simulations are coupled in some way.

    """

    def __init__(self, work, workdir_list=None):
        """Initialize compute resources.

        Appropriate computing resources need to be knowable when the Context is created.
        """
        # self.__context_array = list([Context(work_element) for work_element in work])
        self.__work = None
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
        # The gmxapi namespace of operations should be consistent with a specified universal set of functionalities
        self.__operations['gmxapi'] = {'md': lambda : self.__md(),
                                       # 'open_global_data_with_barrier'...
                                      }
        # Even if TPR file loading were to become a common and stable enough operation to be specified in
        # and API, it is unlikely to be implemented by any code outside of GROMACS, so let's not clutter
        # a potentially more universal namespace.
        self.__operations['gromacs'] = {'load_tpr': lambda *params : self.__load_tpr(*params),
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
        self.work._context = self

    @property
    def work(self):
        return self.__work

    @work.setter
    def work(self, work):
        import importlib

        if isinstance(work, WorkSpec):
            workspec = work
        elif hasattr(work, "workspec") and isinstance(work.workspec, WorkSpec):
            workspec = work.workspec
        else:
            raise ValueError("work argument must provide a gmx.workflow.WorkSpec.")

        # Make sure this context knows how to run the specified work.
        for e in workspec.elements:
            element = gmx.workflow.WorkElement.deserialize(workspec.elements[e])

            if element.namespace not in {'gmxapi', 'gromacs'}:
                # Non-built-in namespaces are treated as modules to import.
                try:
                    element_module = importlib.import_module(element.namespace)
                except ImportError as e:
                    raise exceptions.UsageError("This context does not know how to invoke {} from {}. ImportError: {}".format(element.operation, element.namespace, e.message))

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
                        raise exceptions.ApiError("Operation {} not found in {}.".format(element.operation, element.namespace))
                    # Set or update namespace map only if we have something to contribute.
                    self.__operations[element.namespace] = namespace_map
            else:
                # element.namespace should be mapped, but not all operations are necessarily implemented.
                assert element.namespace in self.__operations
                if not element.operation in self.__operations[element.namespace]:
                    if self.rank < 1:
                        logger.error(self.__operations)
                    # This check should be performed when deciding if the context is appropriate for the work.
                    # If we are just going to use a try/catch block for this test, then we should differentiate
                    # this exception from those raised due to incorrect usage.
                    # \todo Consider distinguishing API misuse from API failures.
                    raise exceptions.ApiError("Specified work cannot be performed due to unimplemented operation {}.{}.".format(element.namespace, element.operation))

        self.__work = workspec

    def __load_tpr(self, *params):
        """Implement the gromacs.load_tpr operation.
        """

        # Note that the actual semantics are to just grab a filename for future reference in a fairly rigid way.

        if not hasattr(self, "_tpr_inputs") or self._tpr_inputs is None:
            self._tpr_inputs = params
        else:
            logger.error("Existing tpr_input: {}".format(self._tpr_inputs))
            logger.error("Unexpected additional input: {}".format(params))
            raise exceptions.ApiError("Context cannot process multiple load_tpr elements.")
        self.size = max(self.size, len(self._tpr_inputs))
        assert not self._tpr_inputs is None
        assert self.size > 0

    def __md(self, element):
        pass

    def __enter__(self):
        """Implement Python context manager protocol.

        Launch the necessary tasks to perform the specified work.

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
        import importlib

        if self._session is not None:
            raise exceptions.Error("Already running.")

        # \todo Logically, this is where resources should be detected / initialized / claimed.
        # At the very least, this would be a good place to identify the current local rank.

        # Initialize the work array width.
        self.size = 0
        # Initialize the running elements of the workflow.
        self.elements = {}

        # Process the work specification.
        self._tpr_inputs = None
        for element in workflow.get_source_elements(self.__work):
            # dispatch operation implementation
            try:
                operation = self.__operations[element.namespace][element.operation]
                args = element.params
                try:
                    self.elements[element.name] = operation(*args)
                except Exception as e:
                    print(e.message)
                    try:
                        self.elements[element.name] = operation()
                    except Exception as e:
                        print(element.name, element, operation)
                        raise e
                    if not args is None and len(args) > 0:
                        self.elements[element.name].set_params(*args)
            except LookupError as e:
                request = '.'.join([element.namespace, element.operation])
                message = "Could not find an implementation for the specified operation: {}. ".format(request)
                message += e.message
                raise exceptions.ApiError(message)

        if self._tpr_inputs is None:
            print(str(self.work))
            print(self.elements)
            raise exceptions.ApiError("WorkSpec was expected to have a load_tpr operation.")
        # Element parameters are the list of inputs that define the work array.
        assert self.size == len(self._tpr_inputs)

        # Prepare working directories. This should probably be moved to some aspect of the Session and either
        # removed from here or made more explicit to the user.
        workdir_list = self.__workdir_list
        if workdir_list is None:
            workdir_list = [os.path.join('.', str(i)) for i in range(self.size)]
        self.__workdir_list = list([os.path.abspath(dir) for dir in workdir_list])
        for dir in self.__workdir_list:
            if os.path.exists(dir):
                if not os.path.isdir(dir):
                    raise exceptions.FileError("{} is not a valid working directory.".format(dir))
            else:
                os.mkdir(dir)

        # Check the global MPI configuration
        communicator = MPI.COMM_WORLD
        comm_size = communicator.Get_size()
        if (self.size > comm_size):
            raise exceptions.UsageError("ParallelArrayContext requires a work array that fits in the MPI communicator: array width {} > size {}.".format(self.size, comm_size))
        if (self.size < comm_size):
            warnings.warn("MPI context is wider than necessary to run this work: array width {} vs. size {}.".format(self.size, comm_size))
        self.rank = communicator.Get_rank()

        assert not self.rank is None

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
            # Launch the work for this rank
            self.rank = communicator.Get_rank()
            self.workdir = self.__workdir_list[self.rank]
            os.chdir(self.workdir)
            logger.info("rank {} changed directory to {}".format(self.rank, self.workdir))

            infile = self._tpr_inputs[self.rank]
            logger.info("TPR input parameter: {}".format(infile))
            infile = os.path.abspath(infile)
            logger.info("Loading TPR file: {}".format(infile))
            assert os.path.isfile(infile)
            system = gmx.core.from_tpr(infile)

            # Agh! This is horrible!
            for element_name in self.__work.elements:
                element = workflow.WorkElement.deserialize(self.__work.elements[element_name], name=element_name, workspec=self.__work)
                if element.operation == 'md':
                    dependancies = element.depends
            for element_name in dependancies:
                element = workflow.WorkElement.deserialize(self.__work.elements[element_name], name=element_name, workspec=self.__work)
                if element.operation != 'load_tpr':

                    element_module = importlib.import_module(element.namespace)
                    element_operation = getattr(element_module, element.operation)
                    args = element.params
                    try:
                        potential = element_operation(*args)
                    except:
                        potential = element_operation()
                        potential.set_params(*args)
                    system.add_potential(potential)

            self._session = system.launch()
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
        sims = [element for element in work if element.operation == "md"]
        if len(sims) != 1:
            raise exceptions.UsageError("gmx currently requires exactly one MD element in the work specification.")
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
            if element.operation == "load_tpr":
                if tpr_input is None:
                    tpr_input = list(element.params)
                else:
                    raise exceptions.ApiError("This Context can only handle work specifications with a single load_tpr operation.")
        if tpr_input is None:
            raise exceptions.UsageError("Work specification does not provide any input for MD simulation.")
        if len(tpr_input) != 1:
            raise exceptions.UsageError("This Context does not support arrays of simulations.")


        # Use old-style constructor that takes gmx.core.MDSystem
        newsystem = gmx.core.from_tpr(tpr_input[0])
        context = Context(newsystem)
    else:
        raise exceptions.UsageError("Argument to get_context must be a runnable gmx.workflow.WorkSpec object.")
    return context
