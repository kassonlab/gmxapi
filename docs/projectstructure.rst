=======================
Implementation overview
=======================

The primary user-facing component is the ``gmx`` :doc:`Python module </layers/python>`, which is implemented
in pure Python for consistency, transparency, and maintainability. It's purpose is to
provide an idiomatic and stable interface to the API functionality.

Where functionality and behavior should mirror that of the C++ API, the Python module refers to the
sub-package ``gmx.core``, which is a C++ extension that serves as a minimal wrapper to ``libgmxapi``.
The bindings in ``gmx.core`` are written entirely in C++ using pybind11, a template header library,
in part to encourage maintainability by GROMACS developers accustomed to C++.
For the same reason, the bindings are a minimal wrapper, relying on functionality of the C++
API provided by ``libgmxapi``.
Wrapper code for exposing the API to ``gmx.core`` is contained in the ``gmxpy`` C++ namespace
and is documented with doxygen.
Wrapper code should only require linking to ``libgmxapi`` (not ``libgromacs``) and compilation
using only the public ``gmxapi`` headers.

The C++ API implementation is provided by the ``gmxapi`` library (e.g. ``libgmxapi.so``)
compiled and installed with GROMACS. Currently, this library is only available in a separate
GROMACS fork at `bitbucket.org/kassonlab/gromacs <https://bitbucket.org/kassonlab/gromacs/>`_.
Clients written against ``libgmxapi`` should only require the ``gmxapi`` headers and
``libgmxapi`` for compilation and linking.
All symbols exposed are in the ``gmxapi`` C++ namespace.
This allows an important distinction from symbols provided by
``libgromacs`` in the top-level namespace and the ``gmx`` namespace that
do not have clear guarantees of stability.
Many of the classes provided by libgromacs do
not have clear memory management and can not safely be used by arbitrary client code outside
of libgromacs.
