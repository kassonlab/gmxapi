"""
Workflow Runners
================
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

__all__ = ['Runner', 'SimpleRunner']

import gmx

class Runner(object):
    """Gromacs Runner base class.

    When initialized with a Gromacs Context, provides a Python context manager
    and a Session with a run() method that returns a Gromacs status object.
    """
    def __init__(self):
        """a clean slate..."""

    def run(self, nsteps=None):
        return gmx.Status(True)

class SimpleRunner(Runner):
    """Gromacs runner for a workflow containing a single task.

    Workflows with no dependence between multiple computation modules are substantially
    simpler and can be executed with a simpler runner.
    """
    def __init__(self, module):
        """
        Create the runner and bind it to an existing module of computational work.

        Args:
            module: reference to an element of work.
        """
        self.module = module
        super(SimpleRunner, self).__init__()
        self._runner = gmx.core.SimpleRunner(self.module._api_object)

    def start(self, context):
        """Ask the API to set up and launch an execution session using the given runner and context."""
        session = self._runner.start()
        return session