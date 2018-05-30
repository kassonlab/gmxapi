# Test gmx.workflow classes and fumctions

import unittest
import pytest

import gmx

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

class PathManagementTestCase(unittest.TestCase):
    """Test proper directory management for load_tpr and Session startup.

    - [ ] Session should use working directory keyed by WorkSpec unique identifier.
    - [ ] Existing directory should not be corrupted.
    - [ ] Existing directory should be checked for state.
    - [ ] File inputs should be made accessible to the Session.
    - [ ] Filesystem artifacts from an element should be accessible by another element.
    - [ ] Filesystem artifacts should be made accessible to the client.
    """
    # Use the harness features to set up a reusable temporary directory
    def setUp(self):
        return

    def tearDown(self):
        return

    def test_directory_creation(self):
        """Check that the session launched but not run in setUp() got created."""
        return

    def test_directory_safety(self):
        """Check that the Session logic refuses to overwrite existing data."""
        return

class PathManagementTestCase(unittest.TestCase):
    """Test proper directory management for load_tpr and Session startup.

    - [ ] Session should use working directory keyed by WorkSpec unique identifier.
    - [ ] Existing directory should not be corrupted.
    - [ ] Existing directory should be checked for state.
    - [ ] File inputs should be made accessible to the Session.
    - [ ] Filesystem artifacts from an element should be accessible by another element.
    - [ ] Filesystem artifacts should be made accessible to the client.
    """
    # Use the harness features to set up a reusable temporary directory
    def setUp(self):
        return

    def tearDown(self):
        return

    def test_directory_creation(self):
        """Check that the session launched but not run in setUp() got created."""
        return

    def test_directory_safety(self):
        """Check that the Session logic refuses to overwrite existing data."""
        return
