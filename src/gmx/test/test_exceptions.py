"""Test gmx module exceptions

Regression tests for defined exceptions and inheritance.

Make sure the documented exceptions are defined correctly.
Throwing of appropriate exceptions is tested using assertRaises
in test for the components that throw them.

\todo these tests are stale but we probably should update and use them...
"""

import unittest

import gmx
from gmx.exceptions import Error
from gmx.exceptions import UsageError
from gmx.exceptions import OptionalFeatureNotAvailableError

# Note: should note API level...

class ExceptionTestCase(unittest.TestCase):
    def test_exception_inheritance(self):
        exception = None
        try:
            raise UsageError("generic usage error")
        except gmx.exceptions.UsageError as e:
            exception = e
        self.assertTrue(isinstance(exception, UsageError))
        self.assertTrue(isinstance(exception, Error))
        try:
            raise OptionalFeatureNotAvailableError("description of feature requirement")
        except gmx.exceptions.OptionalFeatureNotAvailableError as e:
            exception = e
        self.assertTrue(isinstance(exception, OptionalFeatureNotAvailableError))
        self.assertTrue(isinstance(exception, Error))

if __name__ == '__main__':
    unittest.main()
