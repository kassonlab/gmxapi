"""
New DEER incorporation workflow in gmxapi
"""

import json

import gmx
import myplugin  # Custom potentials
import brer_tools

# Add a TPR-loading operation to the default work graph (initially empty) that
# produces simulation input data bundle (parameters, structure, topology)

N = 50  # Number of ensemble members
starting_structure = 'input_conf.gro'
topology_file = 'input.top'
run_parameters = 'params.mdp'
potential_parameters = 'myparams.json'
with open(potential_parameters, mode='r') as fh:
    my_dict_params = json.load(fh)

# make a single simulation input file
initial_tpr = gmx.commandline_operation(
    'gmx',
    'grompp',
    input={
        '-f': run_parameters,
        '-p': topology_file,
        '-c': starting_structure
    })

tpr_list = list([initial_tpr for _ in range(N)])  # A list of (the same) input file
initial_input = gmx.read_tpr(tpr_list)  # An array of N simulations

# just to demonstrate gmxapi functionality, modify a parameter here
# changed parameters with width 1 on an ensemble with width 50
# if we wanted each ensemble member to have a different value, we would just
# have the new parameter value be an array of width 50
lengthened_input = gmx.modify_input(
    initial_input, parameters={'nsteps': 50000000})

# Create subgraph objects that encapsulate multiple operations
# and can be used in conditional and loop operations.
# For subgraphs, inputs can be accessed as variables and are copied to the next
# iteration (not typical for gmxapi operation input/output).
train = gmx.subgraph(variables={'conformation': initial_input})

# References to the results of operations know which (sub)graph they live in.
# The `with` block activates and deactivates the scope of the subgraph in order
# to constrain the section of this script in which references are valid.
# Otherwise, a user could mistakenly use a reference that only points to the
# result of the first iteration of a "while" loop. If the `with` block succeeds,
# then the outputs of `train` are afterwards fully specified.
with train:
    myplugin.training_restraint(
        label='training_potential',
        params=my_dict_params)
    modified_input = gmx.modify_input(
        input=initial_input, structure=train.conformation)
    md = gmx.mdrun(input=modified_input, potential=train.training_potential)
    # Alternate syntax to facilitate adding multiple potentials:
    # md.interface.potential.add(train.training_potential)
    brer_tools.training_analyzer(
        label='is_converged',
        params=train.training_potential.output.alpha)
    train.conformation = md.output.conformation
# At the end of the `with` block, `train` is no longer the active graph, and
# gmx.exceptions.ScopeError will be raised if `modified_input`, or `md` are used
# in other graph scopes (without first reassigning, of course)
# More discussion at https://github.com/kassonlab/gmxapi/issues/205

# In the default work graph, add a node that depends on `condition` and
# wraps subgraph.
train_loop = gmx.while_loop(
    operation=train,
    condition=gmx.logical_not(train.is_converged))

# in this particular application, we "roll back" to the initial input
converge = gmx.subgraph(variables={'conformation': initial_input,
                                   }
                        )

with converge:
    modified_input = gmx.modify_input(
        input=initial_input, structure=converge.conformation)
    myplugin.converge_restraint(
        label='converging_potential',
        params=train_loop.training_potential.output)
    brer_tools.converge_analyzer(
        converge.converging_potential.output.distances,
        label='is_converged',
    )
    md = gmx.mdrun(input=modified_input, potential=converge.converging_potential)

conv_loop = gmx.while_loop(
    operation=converge,
    condition=gmx.logical_not(converge.is_converged))

production_input = gmx.modify_input(
    input=initial_input, structure=converge.conformation)
prod_potential = myplugin.production_restraint(
    params=converge.converging_potential.output)
prod_md = gmx.mdrun(input=production_input, potential=prod_potential)

gmx.run()

print('Final alpha value was {}'.format(
    train_loop.training_potential.output.alpha.result()))
# also can extract conformation filenames, etc.
