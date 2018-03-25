==============
External Force
==============

Limited, external potentials can be applied during an MD simulation by attaching additional
objects to the MD element.

Example:

    >>> import gmx
    >>> import myplugin
    >>> # initialize molecular system
    >>> my_sim = gmx.workflow.from_tpr(tpr_filename)
    >>>
    >>> # access custom code
    >>> potential = gmx.workflow.WorkElement(namespace="myplugin",
    ...                                      operation="ensemble_restraint",
    ...                                      params=params)
    >>> potential.name = "ensemble_restraint"
    >>> md.add_dependency(potential)
    >>>
    >>> # run simulation
    >>> with gmx.context.ParallelArrayContext(md) as session:
    ...     session.run()

Restraints
==========

Restraints apply additional forces by defining an additional potential acting on a site
or sites. A common form of restraint consists of one or more pair potentials acting between sites.
Sites may be individual atoms or entire groups of molecules.

When applied to groups of molecules, force is applied at the center of mass and distributed,
either with mass-weighting (default) or spatial weighting (see "cosine weighting").

For efficiency, restraint potentials are implemented in C++. Most of the code involved
is boiler-plate, so adding a new potential consists of implementing a single function
in a new class, defining the input and output parameters, and registering the potential
(instantiating the templates).

Refer to the `sample plugin <https://github.com/kassonlab/sample_restraint>`_ for a step-by-step walk-through of implementing a new pair restraint.

At the Python level, restraint classes are just classes that provide a registration function
suitable for a call to gmx.md.ExtendedMD.add_potential() (TBD).
At the C++ level, restraint classes implement the restraint interface...

In the most basic case, all restraint classes will have a ``params`` property to serve as a
flexible container for run-time parameters.


Note: I don't know how pretty we can make any sort of auto-generated parameter structure.
There just isn't a good way to automatically name Python attributes. One alternative is to
rely on ordered arguments to a constructor for the plugin and do some magic at the Python level.
Another is to use SWIG or Cython to simultaneously generate the Python and C++. It may be
reasonable, though, to use Python data structures and/or string-mapped accessors in the
C++ code. For instance, in addition to the ``calculate()`` method, the restraint class
could have a ``register()`` method in which a series of ``addParameter()`` calls are made.
