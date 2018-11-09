==========
Change Log
==========

.. rubric:: 0.0.7

Interface and feature updates

Internal

Bug fixes

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
