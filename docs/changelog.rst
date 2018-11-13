==========
Change Log
==========

.. rubric:: 0.0.7

Interface and feature updates

- :py:class:`gmx.context.Context` is generic (ParallelArrayContext, DefaultContext deprecated)
- :py:class:`gmx.system.System` deprecated (use :py:func:`gmx.workflow.from_tpr`)
- Add ``end_time`` keyword argument to :py:func:`gmx.workflow.from_tpr()`

Deprecation

- ``steps`` keyword argument to :py:func:`gmx.workflow.from_tpr()` is deprecated
  in accordance with changes planned for GROMACS 2020.

Internal

- substantial updates for compatibility with GROMACS 2019
- various improvements to CI testing
- Context functionality is now composed according to available resources.
  (Resource tags, such as ``ensemble_update`` will be specified in
  *workspec version 0.2* before the gmxapi 0.1 release.)

Bug fixes

- :py:func:`gmx.get_context()` and :py:func:`gmx.run()` did not behave as expected for all work types.
- substantial documentation updates

.. rubric:: 0.0.6

Interface and feature updates

- Updates to :mod:`gmx.version` module
- Automatically set and restore from MD simulation checkpoints in the session working directory.
- Allow control of whether simulation output is appended or truncated
  (PR `#126 <https://github.com/kassonlab/gmxapi/pull/126>`_).
- Allow plugins to issue a stop signal to MD simulations
  (reference `#62 <https://github.com/kassonlab/gmxapi/issues/62>`_ for gromacs-gmxapi and sample_restraint repos).
- Changes to :mod:`gmx.exceptions`
- Allow full CMake-driven install
- Updated example notebooks in sample_restraint repository.

Internal

- Improved CI testing
- `#64 <https://github.com/kassonlab/gmxapi/issues/64>`_ Unique work spec identification.

Bug fixes

- `#66 <https://github.com/kassonlab/gmxapi/issues/66>`_ Docker does not access current gmxpy version.
- `#123 <https://github.com/kassonlab/gmxapi/issues/123>`_ Race condition in session closing.

.. rubric:: 0.0.5

- allow multiple MD restraints
- documentation updates
- provide Dockerfile for convenience
- continuous integration testing on Travis-CI

.. rubric:: 0.0.4

Initial beta with support for pluggable pair restraints
