"""
Exceptions and Warnings raised by gmx module operations
=======================================================

Errors, warnings, and other exceptions used in the Gromacs
gmx Python package are defined in the gmx.exceptions submodule.

The Gromacs gmx Python package defines a root exception,
gmx.exceptions.Error, from which all Exceptions thrown from
within the module should derive. If a published component of
the gmx package throws an exception that cannot be caught
as a gmx.exceptions.Error, please report the bug.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


__all__ = ['Error',
           'ApiError',
           'CompatibilityError',
           'FeatureNotAvailableError',
           'FeatureNotAvailableWarning',
           'FileError',
           'TypeError',
           'UsageError',
           'ValueError',
           ]

class Error(Exception):
    """Base exception for gmx.exceptions classes."""

class Warning(Warning):
    """Base warning class for gmx.exceptions."""

class UsageError(Error):
    """Unsupported syntax or call signatures.

    Generic usage error for Gromacs gmx module.
    """

class ApiError(Error):
    """An API operation was attempted with an incompatible object."""

class CompatibilityError(Error):
    """An operation or data is incompatible with the current gmxapi environment."""

class FileError(Error):
    """Problem with a file or filename."""

class FeatureNotAvailableError(Error):
    """Feature is not installed, is missing dependencies, or is not compatible."""

class FeatureNotAvailableWarning(Warning):
    """Feature is not installed, is missing dependencies, or is not compatible."""

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
