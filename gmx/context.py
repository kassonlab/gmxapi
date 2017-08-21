"""
Execution Context
=================
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['Context', 'DefaultContext']

class Context(object):
    """ Proxy to API Context provides Python context manager.

    Binds to a workflow (in the form of a Runner) and manages computation resources

    Attributes:
        runner (:obj:`gmx.runner.Runner`): bound workflow to be executed.

    Example:
        >>> with Context(my_runner) as session: # doctest: +SKIP
        ...    session.run()

    """
    def __init__(self, runner=None):
        """Create new context bound to the provided runner, if any.

        Args:
            runner (gmx.Runner) Runner object to bind.

        """
        self.initialized = False
        self.runner = runner

    @property
    def runner(self):
        return self.__runner

    @runner.setter
    def runner(self, runner):
        self.__runner = runner

    def __enter__(self):
        """Implement Python context manager protocol."""
        self.initialized = True
        session = None
        # The API runner currently has an implicit context.
        try:
            session = self.runner.start(self)
        except:
            session = None
            self.initialized = False
            raise
        return session

    def __exit__(self, exception_type, exception_value, traceback):
        """Implement Python context manager protocol."""
        # Todo: handle exceptions.
        self.initialized = False

# In the next pass, Context can become more abstract and simplest-case behavior moved here.
# class SimpleContext(Context):
#     def __init__(self, options=None):
#         pass

class DefaultContext(Context):
    """ Produce an appropriate context for the work and compute environment."""
    def __init__(self, runner):
        # There is very little context abstraction at this point...
        super(DefaultContext, self).__init__(runner)
