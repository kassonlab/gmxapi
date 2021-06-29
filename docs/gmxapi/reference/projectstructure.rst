=======================
Implementation overview
=======================

The primary user-facing component is the ``gmx`` :doc:`Python module <python>`, which is implemented
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

GROMACS master and 2020
=======================

Python packages and C++ interfaces for post-2019 GROMACS repository...

Run time behavior
=================

The ``gmx`` Python module interprets gmxapi operations in a Context that supports
deferred execution and input/output connectivity in a work graph: a data-flow
constrained directed acyclic graph with Operations as nodes, and API data
references as edges.

The package provides utilities to wrap custom Python code in gmxapi-compatible
Operation factories.

Depending on the properties of the provided Context,
implementation code for each Operation factory determines how to process input
in a few possible forms (determined when Director code is expressed).

*explain what happens (serializability, factory functions) when outputs are used as inputs*

..  uml:: diagrams/graphSequence.pu

Output is generated to satisfy data dependencies when a Session is launched from
the ``gmx`` graph-enabled Context.

..  uml:: diagrams/launchSequence.pu

We maximize opportunities for deferred execution and minimal data copies while
minimizing code dependencies and implementation overhead by specifying some
protocols for data proxies, data futures, and data access control.

..  uml:: diagrams/outputAccessSequence.pu

Operations
==========

*illustrate the implications for what happens in the mdrun CLI program or libgromacs MD session.*

..  uml:: diagrams/operationFactory.pu
