========================
Using the Python package
========================

The primary user interface provided through ``gmxapi`` is a Python module
called :mod:`gmx`. The interface is designed to be maximally portable to different
execution environments, with an API that can be used and extended from Python or
C++.

For full documentation of the Python-level interface and API, use the ``pydoc``
command line tool or the ``help()`` interactive Python function, or refer to
the :ref:`python-procedural` documentation.

Once the ``gmxapi`` package is installed, running simulations is easy with :func:`gmx.workflow.from_tpr` and
:func:`gmx.run`.::

    import gmx
    md = gmx.workflow.from_tpr(tpr_filename)
    gmx.run(md)

To run a batch of simulations, just pass an array of inputs.::

    import gmx
    md = gmx.workflow.from_tpr([tpr_filename1, tpr_filename2, ...])
    gmx.run(md)

If additional arguments need to be provided to the simulation as they would for
the ``mdrun`` command line tool, you can add them to the workflow specification
when you create the MD work element.::

    md = gmx.workflow.from_tpr(tpr_list,
                               tmpi=20,
                               grid=[3, 3, 2],
                               pme_threads_per_rank=1,
                               pme_ranks=2,
                               threads_per_rank=1)

Python does not wrap a command-line tool, so once installation is complete,
there shouldn't be any additional configuration necessary, and any errors that
occur should be caught at the Python level. Exceptions should all be descendants
of :class:`gmx.exceptions.Error`.

If you have written plugins or if you have downloaded and built the
`sample <https://github.com/kassonlab/sample_restraint>`_ plugin, you attach it
to your workflow by making it a dependency of the MD element. You can use the
:func:`add_dependency() <gmx.workflow.WorkElement.add_dependency>` member function
of the :class:`gmx.workflow.WorkElement` returned by :func:`from_tpr() <gmx.workflow.from_tpr>`. The following
example applies a harmonic spring restraint between atoms 1 and 4::

    import gmx
    import myplugin
    assert gmx.version.is_at_least(0,0,6)

    md = gmx.workflow.from_tpr([tpr_filename])
    params = {'sites': [1, 4],
              'R0': 2.0,
              'k': 10000.0}
    potential_element = gmx.workflow.WorkElement(namespace="myplugin",
                                                 operation="create_restraint",
                                                 params=params)
    potential_element.name = "harmonic_restraint"
    md.add_dependency(potential_element)
    gmx.run(md)

Refer to the `sample <https://github.com/kassonlab/sample_restraint>`_ plugin
for an additional example of an ensemble-restraint biasing potential that
accumulates statistics from several trajectories in parallel to refine a
pair restraint to bias for a target distribution.

