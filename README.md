The gmxapi project provides interfaces for managing and extending molecular
dynamics simulation workflows. In this repository, a Python package provides the 
`gmx` module for high-level interaction with GROMACS 2019 via gmxapi 0.0.7.
`gmx.core` provides Python bindings to the `gmxapi` C++ GROMACS external API.

The gmxapi 0.0.7 Python project for GROMACS 2019 is hosted at
[GitHub](https://github.com/kassonlab/gmxapi/tree/release-0_0_7)
and includes the `gmxapi` repository along with supporting respositories.
(For current version, see GROMACS 2020+ or the
[latest work](https://github.com/kassonlab/gmxapi)
 from the Kasson Lab.)

A [sample repository](https://github.com/kassonlab/sample_restraint) illustrates
how to implement a GROMACS plugin that applies restrained-ensemble forces
to a loosely-coupled ensemble of simulation trajectories.

The whole thing is driven at the highest level by a simple Python interface.

See the [version 0.0.7 documentation](https://gmxapi.readthedocs.io/en/release-0_0_7/).

Note that gmxapi is now (after 0.0.7) maintained as
[part of](https://redmine.gromacs.org/projects/gromacs/repository/revisions/master/entry/python_packaging/README.md)
the GROMACS project.

##### Reference:
Irrgang, M. E., Hays, J. M., & Kasson, P. M.
gmxapi: a high-level interface for advanced control and extension of molecular dynamics simulations.
_Bioinformatics_ 2018.
DOI: [10.1093/bioinformatics/bty484](https://doi.org/10.1093/bioinformatics/bty484)

## 0.0.7 release branch
[![Build Status](https://travis-ci.org/kassonlab/gmxapi.svg?branch=release-0_0_7)](https://travis-ci.org/kassonlab/gmxapi)
[![Documentation Status](https://readthedocs.org/projects/gmxapi/badge/?version=release-0_0_7)](https://gmxapi.readthedocs.io/en/release-0_0_7/?badge=release-0_0_7)

# Running simulations from Python

To run a simulation as you would with the `gmx` command-line tool, a gmxapi
Python script would look simply like the following.

```py
    import gmx
    md = gmx.workflow.from_tpr('myTPRfile.tpr')
    gmx.run(md)
```

With a plugin, such as the sample [ensemble-restraint](https://github.com/kassonlab/sample_restraint), you can
run a coupled ensemble of simulations that collectively refine a bias potential.
Assuming `tpr_list` is a Python list of input files defining the ensemble, and
`params` is a Python dictionary of keyword arguments,

```py
    import gmx
    import myplugin

    md = gmx.workflow.from_tpr(tpr_list)
    potential = gmx.workflow.WorkElement(
        namespace="myplugin",
        operation="ensemble_restraint",
        depends=[],
        params=params)
    potential.name = "ensemble_restraint_1"
    md.add_dependency(potential)
	gmx.run(md)
```

Currently, given an MPI environment, gmxapi would run the above workflow on a
number of nodes equal to the length of the `tpr_list` array, parallelizing each
simulation across a single node, periodically sharing data via MPI calls across
the ensemble.

Many more features and more flexibility are still to come. Feel free to make
suggestions or describe your own  priorities and research needs in the 
[issue tracking system](https://github.com/kassonlab/gmxapi/issues).

# Installation and getting started

[GROMACS 2019](http://manual.gromacs.org/documentation/2019-current/download.html) with
[`GMXAPI=ON`](http://manual.gromacs.org/2019-current/install-guide/index.html#gmxapi-external-api) 
must be installed before building the Python package.

We recommend installing gmxapi in a Python virtual environment. See [docs/install.rst](docs/install.rst) for details
or refer to the online [user documentation](http://gmxapi.readthedocs.io/).
