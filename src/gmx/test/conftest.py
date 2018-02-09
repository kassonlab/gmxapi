"""Configuration and fixtures for pytest."""

import pytest
import tempfile
import os

@pytest.fixture()
def cleandir():
    """Provide a clean working directory for tests.

    Example usage:

        import os
        import pytest

        @pytest.mark.usefixtures("cleandir")
        class TestDirectoryInit(object):
            def test_cwd_starts_empty(self):
                assert os.listdir(os.getcwd()) == []
                with open("myfile", "w") as f:
                    f.write("hello")

            def test_cwd_again_starts_empty(self):
                assert os.listdir(os.getcwd()) == []

    Ref: https://docs.pytest.org/en/latest/fixture.html#using-fixtures-from-classes-modules-or-projects
    """
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)
