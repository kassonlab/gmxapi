Improvements to |Gromacs| tools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Note to developers!
   Please use """"""" to underline the individual entries for fixed issues in the subfolders,
   otherwise the formatting on the webpage is messed up.
   Also, please use the syntax :issue:`number` to reference issues on GitLab, without the
   a space between the colon and number!

``gmx msd`` has been migrated to the trajectoryanalysis framework
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The tool now uses the |Gromacs| selection syntax. Rather than piping selections via stdin,
selections are now made using the "-sel" option. There is a new option called ``-maxtau``,
which limits maximum time delta between frames to compare for calculating MSDs. This will allow
users who otherwise would run into out-of-memory errors and slow execution with large systems
to restrict sampling to useful tau values.

This migration comes with about a 20% speedup in execution time.

Some rarely used features have yet to be migrated, including:

- The -tensor option is not yet implemented.
- System COM removal with -rmcomm has not yet been implemented.
- B-factor writing using the -pdb option is not yet supported.

A slight behavior change is the removal of the -mw option. ``gmx msd`` with ``-mol`` will
take the MSD of the center-of-mass of of molecules, while no mass-weighting is done
when ``-mol`` is not selected. In previous |Gromacs| versions, ``-mw`` was on by default,
and ``-nomw`` was silently ignored when ``-mol`` was chosen. This change will only cause
different results when performing MSD calculations on a non-homogenous group of particles without
``-mol`` set.

:issue:`2368`

``gmx lie`` now reads energy files from reruns
""""""""""""""""""""""""""""""""""""""""""""""

This tool formerly relied on the presence of a pressure field in the .edr file,
and that field will be missing if the .edr came from a rerun. However it was
never necessary to rely on the presence of the pressure field, so now the
tool just works correctly.

:issue:`4070`

``gmx chi`` no longer needs ``residuetypes.dat`` entries for custom residues
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

The need to add the names of custom residues to ``residuetypes.dat`` has been
removed, because it served no purpose. This makes ``gmx chi`` easier to use.

``gmx wham`` has had minor improvements to its text output
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Reporting about file handling and input-file column contents are easier to
follow.

``gmx do_dssp`` supports DSSP version 4
"""""""""""""""""""""""""""""""""""""""

The newer DSSP version 4 program can be used by ``do_dssp`` by specifying 
option ``-ver 4`` and setting the DSSP environement variable to the ``mkdssp``
executable path (e.g. ``setenv DSSP /opt/dssp/mkdssp``)

:issue:`4129`

``gmx trjconv -dump`` now works reliably
""""""""""""""""""""""""""""""""""""""""

The frame nearest the dump time is now always written, even if the
time is before or after the range present in the trajectory file. To
get the last frame of a trajectory file whose frames are in temporal
order, you can request the dump of any time larger than the time of
any frame in the trajectory, like ``gmx trjconv -dump 9999999``.

:issue:`2873`

``gmx trjconv`` handles selections in TNG files better
""""""""""""""""""""""""""""""""""""""""""""""""""""""

When writing TNG files the whole system was written even if the user requested only a
selection of atoms. Now only the selected atoms should be written. If the selection name
matches a molecule type and the selected atoms are all present in that molecule
then the molecule will be written as expected with the correct molecule count etc.
If the selection only matches some atoms in a molecule or atoms from multiple molecules
then the TNG file will contain a single molecule instance containing all those atoms.

:issue:`2785`

``gmx pdb2gmx`` no longer accepts charged glutamine (QLN) with the OPLS-AA forcefield
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

A torsion angle definition was missing from the (non-standard) charged glutamine
residue. Grompp would use the default torsion angle instead. To avoid silent errors
the charged glutamine residue was removed from the OPLS-AA forcefield.

:issue:`3054`

``gmxapi.commandline_operation`` isolates working directories.
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Subprocesses launched for wrapped command line operations now run in unique subdirectories. Users
who rely on the *output_files* input and *file* output mapping should not be affected. Users who
rely on assumptions about where wrapped commands are executed will need to adjust their scripts.

The *stderr*, *stdout*, and *file* output members are still the primary
supported means to access command output. Additionally, a new *directory* output gives the
filesystem path that was used for the subprocess.
See :py:func:`gmxapi.commandline_operation` for details.

:issue:`3130`
