==============
External Force
==============

Limited, external potentials can be applied during an MD simulation by attaching additional
:py:class:`gmx.core.MDModule` objects to the :py:class:`gmx.md.MD` object.

Example:

    >>> import gmx
    >>> import myplugin
    >>> my_sim = gmx.System._from_file(tpr_filename)
    >>> potential = myplugin.SomePotentia()
    >>> my_sim.md.add_potential(potential)

Restraints
==========

restraints...