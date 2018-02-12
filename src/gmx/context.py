"""
Execution Context
=================
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['Context', 'DefaultContext']

from gmx import exceptions

import os

class Context(object):
    """ Proxy to API Context provides Python context manager.

    Binds to a workflow (in the form of a Runner) and manages computation resources

    Attributes:
        workflow (:obj:`gmx.workflow.workflow`): bound workflow to be executed.

    Example:
        >>> with Context(my_workflow) as session: # doctest: +SKIP
        ...    session.run()

    """
    def __init__(self, workflow=None):
        """Create new context bound to the provided workflow, if any.

        Args:
            workflow (gmx.workflow) workflow object to bind.

        """
        self._session = None
        self.__workflow = workflow

    @property
    def workflow(self):
        return self.__workflow

    @workflow.setter
    def workflow(self, workflow):
        self.__workflow = workflow

    def __enter__(self):
        """Implement Python context manager protocol."""
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

    Hierarchical Context manages simpler contexts for array work that can be decomposed into an array of serial
    specifications. Additional facilities are available to elements of the array members.

      * array element corresponding to work in the current sub-context
      * "global" resources managed by the ParallelArrayContext

    Attributes:


    Example: Use ``mpiexec -n 2 python -m mpi4py myscript.py`` to run two jobs at the same time.
    In this example the jobs are identical. In myscript.py:

        >>> import gmx
        >>> import gmx.core
        >>> from gmx.data import tpr_filename # Get a test tpr filename
        >>> work = gmx.core.from_tpr(tpr_filename)
        >>> context = gmx.context.ParallelArrayContext([work, work])
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

        Appropriate computing resources need to be available when the
        """
        if not isinstance(work, list):
            raise ValueError("work specification should be a Python list.")
        if workdir_list is None:
            workdir_list = [os.path.join('.', str(i)) for i in range(len(work))]
        self.workdir_list = list([os.path.abspath(dir) for dir in workdir_list])
        for dir in self.workdir_list:
            if os.path.exists(dir):
                if not os.path.isdir(dir):
                    raise exceptions.FileError("{} is not a valid working directory.".format(dir))
            else:
                os.mkdir(dir)

        self.__context_array = list([Context(work_element) for work_element in work])
        self._session = None
        # This may not belong here. Is it confusing for the Context to have both global and local properties?
        self.rank = None

    def __enter__(self):
        """Implement Python context manager protocol."""
        if self._session is not None:
            raise exceptions.Error("Already running.")

        from mpi4py import MPI

        # Check the global MPI configuration
        communicator = MPI.COMM_WORLD
        if (len(self.__context_array) != communicator.Get_size()):
            raise exceptions.UsageError("ParallelArrayContext requires a work array that matches the MPI communicator size.")

        # Launch the work for this rank
        self.rank = communicator.Get_rank()
        my_workdir = self.workdir_list[self.rank]
        os.chdir(my_workdir)

        # The API runner currently has an implicit context.
        try:
            # \todo Use API context implementation object
            self._session = self.__context_array[self.rank].workflow.launch()
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
    """
    from . import workflow
    context = None
    if work is None:
        context = Context()
    elif isinstance(work, workflow.WorkSpec):
        # Assume simple simulation for now.
        # Get source elements.
        #
        # Use old-style constructor that takes gmx.core.MDSystem
        context = Context(work)
    else:
        raise exceptions.UsageError("Argument to get_context must be a runnable gmx.workflow.WorkSpec object.")
    return context
