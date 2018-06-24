===========================
gmx Python module reference
===========================

.. Concise reference documentation extracted directly from code.
.. For new and non-backwards-compatible features, API versions must be given.

The Gromacs Python interface is implemented as a high-level scripting interface implemented in pure Python and a lower-level API implemented as a C++ extension.
The pure Python implementation provides the basic ``gmx`` module and
classes with a very stable syntax that can be maintained with maximal compatibility
while mapping to lower level interfaces that may take a while to sort out. The
separation also serves as a reminder that different execution contexts may be
implemented quite diffently, though Python scripts using only the high-level
interface should execute on all. Bindings to the ``libgromacs`` C++ API are
provided in the submodule :py:mod:`gmx.core`.

The following documentation is extracted from the ``gmx`` Python module and is also available
directly, using either ``pydoc`` from the command line or ``help()`` from within Python, such
as during an interactive session.

Refer to the Python source code itself for additional clarification.

.. Configuration for doctest: automated syntax checking in documentation code snippets
.. testsetup::

    import gmx
    from gmx.data import tpr_filename

.. automodule:: gmx

User interface
==============

.. automodule:: gmx.system
    :members:

.. automodule:: gmx.workflow
    :members:

.. automodule:: gmx.context
    :members:

.. automodule:: gmx.status
    :members:

.. automodule:: gmx.exceptions
    :members:

Core API
========

.. automodule:: gmx.core

Classes
-------

.. autoclass:: gmx.core.Context
    :members:

.. autoclass:: gmx.core.MDArgs
    :members:

.. autoclass:: gmx.core.MDSession
    :members:

.. autoclass:: gmx.core.MDSystem
    :members:

.. autoclass:: gmx.core.Status
    :members:

.. autoclass:: gmx.core.TestModule
    :members:

Functions
---------

.. autofunction:: gmx.core.from_tpr
