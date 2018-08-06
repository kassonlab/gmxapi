# Test gmx.workflow classes and fumctions

import unittest
import pytest

import gmx
import gmx.core

class MDArgsTestCase(unittest.TestCase):
    """Test creation and setting of MDArgs for Context runtime."""
    def test_creation(self):
        """Create the parameters object."""
        mdargs = gmx.core.MDArgs()
        params = {'max_hours': 2}
        mdargs.set(params)
    def test_setting(self):
        """Test the setting of MDArgs values and passing them to context."""
        params_list = [
            {
                'grid': [1, 1, 1]
            },
            {
                'pme_ranks': 1
            }
        ]
        # Test each parameter individually for clarity. Note all are optional.
        for param in params_list:
            mdargs = gmx.core.MDArgs()
            mdargs.set(param)
            context = gmx.core.Context()
            context.setMDArgs(mdargs)
