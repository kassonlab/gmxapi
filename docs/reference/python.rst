===========================
gmx Python module reference
===========================

The following documentation is extracted from the ``gmx`` Python module and is also available
directly, using either ``pydoc`` from the command line or ``help()`` from within Python, such
as during an interactive session.

Refer to the Python source code itself for additional clarification.

.. testsetup::

    import gmx
    from gmx.data import tpr_filename

.. automodule:: gmx

.. automodule:: gmx.system
    :members:

.. automodule:: gmx.runner
    :members:

.. automodule:: gmx.context
    :members:

.. automodule:: gmx.md
    :members:

.. automodule:: gmx.status
    :members:

.. automodule:: gmx.exceptions
    :members:

.. automodule:: gmx.core

.. autofunction:: gmx.core.from_tpr

.. skipping gmx.core.md_from_tpr

.. autoclass:: gmx.core.MD
    :members:

.. autoclass:: gmx.core.SimpleRunner
    :members:

.. autoclass:: gmx.core.MDSystem
    :members:

.. autoclass:: gmx.core.Status
    :members:

.. autoclass:: gmx.core.MDModule
    :members:

