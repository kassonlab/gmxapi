"""
Exceptions and Warnings raised by gmx module operations
=======================================================

Errors, warnings, and other exceptions used in the Gromacs
gmx Python package are defined in the gmx.exceptions submodule.

The Gromacs gmx Python package defines a root exception,
gmx.exceptions.Error, from which all Exceptions thrown from
within the module should derive. If a published component of
the gmx package throws an execption that cannot be caught
as a gmx.exceptions.Error, please report the bug.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


__all__ = ['Error',
           'ApiError',
           'FileError',
           'OptionalFeatureNotAvailableError',
           'OptionalFeatureNotAvailableWarning',
           'TypeError',
           'UsageError',
           'ValueError',
           ]

class Error(Exception):
    """Base exception for gmx.exceptions classes."""

class UsageError(Error):
    """Unsupported syntax or call signatures.

    Generic usage error for Gromacs gmx module.
    """

class ApiError(Error):
    """An API operation was attempted with an incompatible object."""

class FileError(Error):
    """Problem with a file or filename."""

class OptionalFeatureNotAvailableError(Error):
    """Optional feature is not installed or is missing dependencies."""

class OptionalFeatureNotAvailableWarning(Warning):
    """A feature is not installed or is missing dependencies."""

class TypeError(Error):
    """An object is of a type incompatible with the API operation."""
    def __init__(self, got=None, expected=None):
        message = "Incompatible type."
        if expected is not None:
            message += " Expected type {}.".format(expected)
        if got is not None:
            message += " Got type {}.".format(type(got))
        super(TypeError, self).__init__(message)

class ValueError(Error):
    """A user-provided value cannot be interpreted or doesn't make sense."""
