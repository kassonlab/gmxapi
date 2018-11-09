======
Python
======

Notes on the Python level of the package.

Other Python Gromacs interfaces
===============================

- `gmxscript <https://github.com/pslacerda/gmx>`__ : all-python CLI
   wrapper manages files, provides "checkpointed" re-runnable workflow with
   mdp rewriting and CLI replacement
- `GromacsWrapper <http://gromacswrapper.readthedocs.io/en/latest/>`__
   (Beckstein) : all-python CLI wrapper provides thorough scriptable
   interface with error handling
- `pmx <https://github.com/dseeliger/pmx>`__ (D. Seeliger) : Manipulate
   Gromacs files and data structures
- `grompy <https://github.com/GromPy>`__ (Rene Pool) : patches old Gromacs
   code to provide ctypes interface to Gromacs libraries
- `gmx\_wrapper <https://github.com/khuston/gmx_wrapper>`__ : very
   bare-bones CLI wrapper
- `GromacsPipeline <https://biod.pnpi.spb.ru/gitweb/?p=alexxy/gromacs.git;a=commit;h=1241cd15da38bf7afd65a924100730b04e430475>`__
   (Redmine 1625) adds SIP bindings to run Gromacs analysis modules in a
   single pass on a trajectory

Existing Python tools to leverage
=================================

Some of the tools available from the ``gmx`` command-line interface
are bundled largely for convenience,
and Python users may be better served by turning to other projects
rather than relying on exposing
redundant functionality from ``libgromacs``.
In other cases, Gromacs developers may simply want to be aware of the
other tools and interoperability requirements.

-  `pypdb <https://github.com/williamgilpin/pypdb>`__ A Python API for
   the RCSB Protein Data Bank (PDB)
-  `chemlab <http://chemlab.github.io/chemlab/>`__ Qt-powered molecular
   viewer
-  `chemview <https://github.com/gabrielelanaro/chemview>`__ molecular
   viewer for IPython from the author of chemlab
-  `MDTraj <http://mdtraj.org/>`__ Read, write and analyze MD
   trajectories
-  `MDAnalysis <http://www.mdanalysis.org>`__ analyze trajectories from
   molecular dynamics
-  `Biopython <https://github.com/biopython/biopython>`__ tools for
   computational molecular biology
-  several packages named "Biopy" do not seem relevant
-  `PyMOL <http://www.pymol.org/>`__ molecular viewer
-  `mmLib <http://pymmlib.sourceforge.net/>`__ Python Macromolecular
   Library analysis, manipulation, and viewing
-  `msmbuilder <http://msmbuilder.org/>`__ Statistical models for
   Biomolecular Dynamics
-  `PyEMMA <http://emma-project.org/>`__ estimation, validation and
   analysis Markov models from molecular dynamics (MD) data
-  `ExSTACY <http://extasy-project.org>`__ Collection of tools that
   couples large ensemble Molecular Dynamics calculations with analysis
   to provide improvements in sampling. Includes
-  `EnsembleMD <https://github.com/radical-cybertools/radical.ensemblemd>`__
   framework for running ensemble workflows
-  `COCO <https://bitbucket.org/extasy-project/coco>`__
-  `LSDMap <https://sourceforge.net/projects/lsdmap/>`__ Locally Scaled
   Diffusion Maps
-  `pyPcazip <https://bitbucket.org/ramonbsc/pypcazip>`__ principle
   component analysis
-  `Plumed <http://www.plumed.org>`__ free energy calculation using
   collective variables
-  pdb tools
-  OpenMM
-  msmbuilder
-  BioXL

Naming
======

The package should have a name that does not collide with other known
projects, particularly any projects on pypi.
"gmx" is available on pypi, but similar existing package names include

-  ``gmx-script``
-  ``python-gmx``

``pygmx`` is the name used for a bindings package posted to the Gromacs
list that resides at https://biod.pnpi.spb.ru/~alexxy/pygmx

There are several packages named ``grompy``

The Beckstein lab has ``GromacsWrapper`` which exists on
PythonHosted.org, GitHub, and PyPi.

Note that our CMake project is called ``gmxpy`` through (at least) release 0.0.7.

Python version
==============

The Python 2 end-of-support has been extended to 2020. It is reasonable to
assume that Python 2.7.15 is the final version of Python 2 and that it will be
officially end-of-lifed in 2020. On the one hand, Python 2 will be a mature
language with no further interface changes. On the other hand, the loss of the
commitment to bug fixes means it has already started fading away.

Python 3.3 has a lot of improvements and changes, including better 2.7 compatibility

Python 3.4

- built-in pip
- enum types
- new pickle protocol

Python 3.5

- typing and coroutines
- RecursionError exception
- Generators have gi_yieldfrom
- memoryview tuple indexing
- hexadecimal methods

Linux distributions released after June 2013 and supported at least to June 2019.

| Ubuntu 14.04 (trusty): Python 3.4
| Ubuntu 16.04 (denial): Python 3.5
| Debian 8 (jessie): Python 3.4
| Debian 9 (stretch): Python 3.5
| Linux Mint 18 (rosa): 3.4
| Linux Mint 17 (sarah): 3.5
| Fedora 23: 3.4
| Fedora 24+: 3.5
| RHEL 7: n/a
| CentOS 7: n/a

gmxapi policy
^^^^^^^^^^^^^

GROMACS will officially switch from Python 2.7 to Python 3+
during the GROMACS 2020 development cycle for its infrastructure.
gmxapi 0.0.7 officially supports Python 2.7 and Python 3.4+.
gmxapi will continue to support Python 2.7 for as long as is feasible,
but should default to Python 3 style and syntax.
As much as possible, current code is in a version-agnostic style, avoiding
dependencies on ``3to2`` or ``six``.
Future versions may use compatibility tools.
At some point, Python 2 compatibility will be achieved with conversion tools
during package installation instead of in the Python source code so that we can
remove ``from __future__`` imports and other clunky work-arounds.
