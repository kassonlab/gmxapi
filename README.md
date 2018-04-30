[![Build Status](https://travis-ci.org/kassonlab/gmxapi.svg?branch=master)](https://travis-ci.org/kassonlab/gmxapi)
[![Documentation Status](https://readthedocs.org/projects/gmxapi/badge/?version=latest)](http://gmxapi.readthedocs.io/en/latest/?badge=latest)

The gmxapi project provides interfaces for managing and extending molecular dynamics simulation workflows.
In this repository, a Python package provides the `gmx` module for high-level interaction with GROMACS.
`gmx.core` provides Python bindings to the `gmxapi` C++ GROMACS external API.

The project is hosted on [GitHub](https://github.com/kassonlab/gmxapi) and includes
the `gmxapi` repository along with supporting respositories.
The [`gromacs-gmxapi`](https://github.com/kassonlab/gromacs-gmxapi) repository includes a modified version of GROMACS that
supports the latest `gmxapi` features not yet available through an official GROMACS distribution.
A [sample repository](https://github.com/kassonlab/sample_restraint) illustrates
how to implement a GROMACS plugin that applies restrained-ensemble forces
to a loosely-coupled ensemble of simulation trajectories.

The whole thing is driven at the highest level by a simple Python interface.

See the latest gmxapi documentation at [http://gmxapi.readthedocs.io/en/latest/](http://gmxapi.readthedocs.io/en/latest/)

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

gmxapi is just entering beta, so many more features and more flexibility are to
come. Feel free to make suggestions or describe your own priorities and research
needs in the issue tracking system.

# Installation and getting started

A compatible version of GROMACS must either be already installed or may be installed
as part of package installation. See [`gromacs-gmxapi`](https://github.com/kassonlab/gromacs-gmxapi)

We recommend installing gmxapi in a Python virtual environment. See [docs/install.rst](docs/install.rst) for details
or refer to the online [user documentation](http://gmxapi.readthedocs.io/en/latest/).
