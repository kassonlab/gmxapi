# gmxapi-scripts

Sample scripts for running some high-level tasks including ensemble simulation in gmxapi.

These scripts illustrate the functionality to be delivered in the second quarter of 2019 under subtasks
 of 
GROMACS issue [2045](https://redmine.gromacs.org/issues/2045)
and as outlined in the 
[roadmap](https://redmine.gromacs.org/projects/gromacs/repository/revisions/master/entry/python_packaging/roadmap.rst).
Syntax and comments illustrate expected user interaction with data flow between operations in a work graph.

For implementation status, refer to Gerrit [gmxapi topic](https://gerrit.gromacs.org/q/topic:%22gmxapi%22) and the 
gmxapi 
[sandbox branch](https://github.com/kassonlab/gromacs-gmxapi/commits/kassonLabFork)

## Examples

### `brer.py`

BRER simulation-analysis protocol implemented as a gmxapi script, with a Python analysis
 module (`brer_tools.py` not implemented here) and C++ MD extension code (`myplugin.so` also not shown).

### `restrained_ensemble.py`

Restrained ensemble example script using restraint potentials implemented in `myplugin` (not shown) and analysis code
 expressed in `restrained_md_analysis.py`.

### `rmsf.py`

Run simulations with a range of `tau-t` values and analyze
with the `gmx rmsf` tool.

### `run_adaptive_msm.py`

Use custom analysis code from `analysis.py` to set the initial conformations for iterations of simulation batches.
