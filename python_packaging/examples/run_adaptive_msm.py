"""
Runner for adaptive MSMs
"""

import analysis
import gmxapi as gmx

# Add a TPR-loading operation to the default work graph (initially empty) that
# produces simulation input data bundle (parameters, structure, topology)

N = 50  # Number of ensemble members
starting_structure = 'input_conf.gro'  # Could start with a list of distinct confs
topology_file = 'input.top'
run_parameters = 'params.mdp'

initial_tpr = gmx.commandline_operation('gmx', 'grompp',
                                        input_files={'-f': run_parameters,
                                                     '-p': topology_file,
                                                     '-c': starting_structure})
# Project roadmap notes:
# To do:
#  * GROMACS CLI tools receive improved Python-level support over generic
#    command line operations. (FR18)
#  * GROMACS CLI tools receive improved C++-level support over gneric command
#    line operations. (FR19)
#  * Python bindings use C++ API for expressing UI. (FR20)

# Set up an array of N simulations, starting from a single input.
initial_input = gmx.read_tpr([initial_tpr for _ in range(N)])
# Project roadmap notes:
# Output proxy establishes execution dependency (FR2 and FR3 in ../roadmap.rst and ../test/)
# Dimensionality and typing of named data causes generation of correct work topology (FR4)

# We will need a pdb for MSM building in PyEmma
editconf = gmx.commandline_operation('gmx', 'editconf',
                                     input_files={'-f': starting_structure},
                                     output_files={'-o': gmx.File('.pdb')})
# Project roadmap notes:
# User insulated from filesystem paths: FR21

# Get a placeholder object that can serve as a sub context / work graph owner
# and can be used in a control operation.
subgraph = gmx.subgraph(variables={
    'conformation': initial_input.conformation,
    'P': gmx.ndarray(0., shape=(N, N)),
    'is_converged': False,
})
# Project roadmap notes:
# Python access to TPR file contents: FR11

with subgraph:
    modified_input = gmx.modify_input(
        input=initial_input, structure=subgraph.conformation)
    # Project roadmap notes:
    # Simulation input modification: FR15
    # Prepare simulation input from multiple sources: FR17

    md = gmx.mdrun(input=modified_input)
    # Project roadmap notes:
    # Python bindings for launching simulations: FR7.
    # Simulations implicitly handle ensemble work: FR8.

    # Get the output trajectories and pass to PyEmma to build the MSM
    # Return a stop condition object that can be used in gmx while loop to
    # terminate the simulation
    allframes = gmx.commandline_operation('gmx', 'trajcat',
                                          input_files={'-f': gmx.gather(md.output.trajectory.file)},
                                          output_files={'-o': gmx.File('.trr')})
    # Project roadmap notes:
    # User insulated from filesystem paths: FR21

    # Project roadmap notes:
    # Explicit many-to-one data flow with gmx.gather: FR5

    adaptive_msm = analysis.msm_analyzer(topfile=editconf.file['-o'],
                                         trajectory=allframes.output.file['-o'],
                                         P=subgraph.P)
    # Update the persistent data for the subgraph
    subgraph.P = adaptive_msm.output.transition_matrix
    # adaptive_msm here is responsible for maintaining the ensemble width
    subgraph.conformation = adaptive_msm.output.conformation
    subgraph.is_converged = adaptive_msm.output.is_converged

# In the default work graph, add a node that depends on `condition` and
# wraps subgraph.
my_loop = gmx.while_loop(operation=subgraph, condition=gmx.logical_not(subgraph.is_converged))
# Project roadmap notes:
# Fused operations for use in looping constructs: FR10.

gmx.run()
# Project roadmap notes:
# `run()` module function simplifies user experience: FR13.
