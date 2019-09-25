import gmx

# Add a TPR-loading operation to the default work graph (initially empty) that
# produces simulation input data bundle (parameters, structure, topology)

# Make N run input files
N = 50  # Number of ensemble members
starting_structure = 'input_conf.gro'
topology_file = 'input.top'
run_parameters = 'params.mdp'

initial_tpr = gmx.commandline_operation(
    'gmx',
    'grompp',
    input={
        '-f': run_parameters,
        '-c': starting_structure,
        '-p': topology_file
    },
    output={'-o': gmx.File(suffix='.tpr')})
# Note: Before gmx.File, users still have to manage filenames
# The above would have `output={'-o': [initial_tpr for _ in range(N)]}`

# Note: initial_tpr has a single output that can be automatically broadcast now or later.
# Broadcast to the read_tpr operation:
# simulation_input = gmx.read_tpr([initial_tpr for _ in range(N)])
# Wait to broadcast until the next operation:
simulation_input = gmx.read_tpr(initial_tpr.output.file['-o'])

# Array inputs imply array outputs.
input_array = gmx.modify_input(
    simulation_input, params={'tau-t': [t / 10.0 for t in range(N)]})

md = gmx.mdrun(input_array)  # An array of simulations

rmsf = gmx.commandline_operation(
    'gmx',
    'rmsf',
    input={
        '-f': md.output.trajectory,
        '-s': initial_tpr
    },
    output={'-o': gmx.File(suffix='.xvg')})
output_files = gmx.gather(rmsf.output.file['-o'])
gmx.run()

print('Output file list:')
print(', '.join(output_files.result()))
