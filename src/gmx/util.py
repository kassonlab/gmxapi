"""Utility functions supporting the Gromacs Python interface.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os

__all__ = []

from gmx.exceptions import UsageError
from gmx.exceptions import FileError

def _filetype(filename):
    """Use Gromacs file I/O module to identify known file types.

    Attempts to open the provided file. If successful, returns the gmx.io class
    associated with the identified file type. Relative file paths
    should be interpreted with regard to the execution context, but
    are currently interpreted relative to the directory set in the
    ``_current_dir`` attribute of the imported gmx.fileio module
    wherever the Python script is running, which can be reassigned
    by the user independently of actual current working directory.

    This function cannot be part of the public interface until the
    meaning of file paths is clarified regarding the presence of
    execution contexts.

    Args:
        filename (str): the name of a file for Gromacs to inspect

    Returns:
        gmx.io.File subclass

    Raises:
        FileError is filename is not a readable file.
    """
    from gmx import fileio
    # Get an absolute filename.
    if not os.path.isabs(filename):
        filename = os.path.join(fileio._current_dir, filename)
    if os.path.isfile(filename):
        return fileio.TprFile
    else:
        raise UsageError("Argument is not a readable file.")

def to_utf8(input):
    """Return a utf8 encoded byte sequence of the Unicode ``input`` or its string representation.

    In Python 2, returns a :py:str object. In Python 3, returns a :py:bytes object.
    """
    py_version = sys.version_info.major
    if py_version == 3:
        if isinstance(input, str):
            value = input.encode('utf-8')
        elif isinstance(input, bytes):
            value = input
        else:
            try:
                string = str(input)
            except:
                raise UsageError("Cannot find a Python 3 string representation of input.")
            value = string.encode('utf-8')
    else:
        assert py_version == 2
        if isinstance(input, unicode):
            value = input.encode('utf-8')
        else:
            try:
                value = str(input)
            except:
                raise UsageError("Cannot find a Python 2 string representation of input.")
    return value

def to_string(input):
    """Return a Unicode string representation of ``input``.

    If ``input`` or its string representation is not already a Unicode object, attempt to decode as utf-8.

    In Python 3, returns a native string, decoding utf-8 encoded byte sequences if necessary.

    In Python 2, returns a Unicode object, converting data types if necessary and possible.

    Note:
        In Python 2, byte sequence objects are :py:str type, so passing a :py:str actually converts from :py:str: to
        :py:unicode. To guarantee a native string object, wrap the output of this function in ``str()``.
    """
    py_version = sys.version_info.major
    if py_version == 3:
        if isinstance(input, str):
            value = input
        else:
            try:
                value = input.decode('utf-8')
            except:
                try:
                    value = str(input)
                except:
                    raise UsageError("Cannot find a Python 3 string representation of input.")
    else:
        assert py_version == 2
        if isinstance(input, unicode):
            value = input
        else:
            try:
                string = str(input)
            except:
                raise UsageError("Cannot find a Python 2 string representation of input.")
            value = string.decode('utf-8')
    return value

def _test():
        import doctest
        doctest.testmod()

if __name__ == "__main__":
    _test()
