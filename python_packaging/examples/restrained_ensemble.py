#!/usr/bin/env python
"""Run restrained-ensemble sampling and biasing workflow.

Irrgang, M. E., Hays, J. M., & Kasson, P. M.
gmxapi: a high-level interface for advanced control and extension of molecular dynamics simulations.
*Bioinformatics* 2018.
DOI: `10.1093/bioinformatics/bty484 <https://doi.org/10.1093/bioinformatics/bty484>`_
"""

# Restrained-ensemble formalism is a variant of that defined by Roux et al., 2013

import json

import gmx
import myplugin
from restrained_md_analysis import calculate_js

# The user has already built 20 input files in 20 directories for an ensemble of width 20.
N = 100
starting_structure = 'input_conf.gro'
topology_file = 'input.top'
run_parameters = 'params.mdp'

initial_tpr = gmx.commandline_operation('gmx', 'grompp',
                                        input={'-f': run_parameters,
                                               '-p': topology_file,
                                               '-c': starting_structure})
initial_input = gmx.read_tpr([initial_tpr for _ in range(N)])  # An array of simulations

with open('params1.json', 'r') as fh:
    restraint1_params = json.load(fh)
with open('params2.json', 'r') as fh:
    restraint2_params = json.load(fh)

# The pair-distance histogram for a single pair is `nbins` wide in each ensemble
# member between iterations, and is broadcast to `N` instances when the potential
# is bound to the mdrun operation.
# NDArray syntax in Python is based on numpy user interfaces.
converge = gmx.subgraph(
    variables={'pair_distance1': gmx.NDArray(0., shape=restraint1_params['nbins']),
               'pair_distance2': gmx.NDArray(0., shape=restraint2_params['nbins']),
               }
)

with converge:
    # ensemble_restraint is implemented using gmxapi ensemble allReduce operations
    # that do not need to be expressed in this procedural interface.
    potential1 = myplugin.ensemble_restraint(label='ensemble_restraint_1',
                                             params=restraint1_params,
                                             input={'pair_distance': converge.pair_distance1})
    potential2 = myplugin.ensemble_restraint(label='ensemble_restraint_2',
                                             params=restraint2_params,
                                             input={'pair_distance': converge.pair_distance2})

    md = gmx.mdrun(initial_input)
    md.interface.potential.add(potential1)
    md.interface.potential.add(potential2)

    # Compare the distribution from the current iteration to the experimental
    # data and look for a threshold of low J-S divergence
    # We perform the calculation using all of the ensemble data.
    js_1 = calculate_js(input={'params': restraint1_params,
                               'simulation_distances': gmx.gather(potential1.output.pair_distance)})
    js_2 = calculate_js(input={'params': restraint2_params,
                               'simulation_distances': gmx.gather(potential2.output.pair_distance)})
    gmx.logical_and(js_1.is_converged, js_2.is_converged, label='is_converged')

    converge.pair_distance1 = potential1.output.pair_distance
    converge.pair_distance2 = potential2.output.pair_distance

work = gmx.while_loop(operation=converge, condition=gmx.logical_not(converge.is_converged))

# Command-line arguments for mdrun can be added to gmx run as below.
# Settings for a 20 core HPC node. Use 18 threads for domain decomposition for pair potentials
# and the remaining 2 threads for PME electrostatics.
gmx.run(work, tmpi=20, grid=gmx.NDArray([3, 3, 2]), ntomp_pme=1, npme=2, ntomp=1)
