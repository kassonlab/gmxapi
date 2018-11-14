=======================
Implementation overview
=======================

The primary user-facing component is the ``gmx`` :doc:`Python module </layers/python>`, which is implemented
in pure Python for consistency, transparency, and maintainability. It's purpose is to
provide an idiomatic and stable interface to the API functionality.

Where functionality and behavior should mirror that of the C++ API, the Python module refers to the
sub-package ``gmx.core``, which is a C++ extension that serves as a minimal wrapper to ``libgmxapi``.
The bindings in ``gmx.core`` are written entirely in C++ using pybind11, a template header library,
to be easy to maintain along side the GROMACS C++ API.

Wrapper code in ``gmx.core`` is contained in the ``gmxpy`` C++ namespace.
The ``gmxpy`` namespace contains implementation details only and should not be
used in other projects.
It is documented internally with doxygen syntax.

Wrapper code should only require linking to ``libgmxapi`` (not ``libgromacs``).
Compilation should only require the public ``gmxapi`` headers.
The Python package CMake configuration uses ``gmxapi_DIR`` or ``GROMACS_DIR`` to
find the ``Gromacs::gmxapi`` CMake target provided by the GROMACS installation.

The ``gmxapi`` library is provided in GROMACS 2019 and in a separate GROMACS fork at
https://github.org/kassonlab/gromacs-gmxapi/
