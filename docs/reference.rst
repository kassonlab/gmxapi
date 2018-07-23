===========================
gmx Python module reference
===========================

.. contents:: :local:
    :depth: 2

.. Concise reference documentation extracted directly from code.
.. For new and non-backwards-compatible features, API versions must be given.

The Gromacs Python interface is implemented as a high-level scripting interface implemented in pure Python and a
lower-level API implemented as a C++ extension.
The pure Python implementation provides the basic ``gmx`` module and
classes with a very stable syntax that can be maintained with maximal compatibility
while mapping to lower level interfaces that may take a while to sort out. The
separation also serves as a reminder that different execution contexts may be
implemented quite diffently, though Python scripts using only the high-level
interface should execute on all. Bindings to the ``libgromacs`` C++ API are
provided in the submodule :mod:`gmx.core`.

The following documentation is extracted from the ``gmx`` Python module and is also available
directly, using either ``pydoc`` from the command line or :py:func:`help` from within Python, such
as during an interactive session.

Refer to the Python source code itself for additional clarification.

.. Configuration for doctest: automated syntax checking in documentation code snippets
.. testsetup::

    import gmx
    from gmx.data import tpr_filename

.. _python-procedural:

Procedural interface
====================

- :func:`gmx.run`
- :func:`gmx.get_context`
- :func:`gmx.workflow.from_tpr`
- :func:`gmx.workflow.get_source_elements`
- :func:`gmx.version.api_is_at_least`

.. autofunction:: gmx.run

.. autofunction:: gmx.get_context

.. autofunction:: gmx.workflow.from_tpr

.. autofunction:: gmx.workflow.get_source_elements

.. autofunction:: gmx.version.api_is_at_least

Python API
==========

.. contents:: :local:

Python Classes
--------------

- :class:`gmx.workflow.WorkSpec`
- :class:`gmx.workflow.WorkElement`
- :class:`gmx.context.Context`
- :class:`gmx.context.ParallelArrayContext`
- :class:`gmx.status.Status`

Python context managers
-----------------------

Objects implementing the Context interfaces defined in :mod:`gmx.context` implement
the Python context manager protocol. When used in a ``with`` block, a Context
produces a :class:`Session` object. See examples below.

.. note::

    :class:`Session` is not well specified in gmxapi 0.0.6.

gmx.system module
-----------------

.. automodule:: gmx.system
    :members:

gmx.workflow module
-------------------

.. automodule:: gmx.workflow
    :members:

gmx.context module
------------------
.. automodule:: gmx.context
    :members:

gmx.status
----------
.. automodule:: gmx.status
    :members:

gmx.exceptions
--------------
.. automodule:: gmx.exceptions
    :members:

gmx.version
-----------
.. automodule:: gmx.version
    :members:

Core API
========

.. automodule:: gmx.core

Functions
---------

.. autofunction:: gmx.core.from_tpr

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
