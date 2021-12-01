#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019,2020,2021, by the GROMACS development team, led by
# Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# and including many others, as listed in the AUTHORS file in the
# top-level source directory and at http://www.gromacs.org.
#
# GROMACS is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public License
# as published by the Free Software Foundation; either version 2.1
# of the License, or (at your option) any later version.
#
# GROMACS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GROMACS; if not, see
# http://www.gnu.org/licenses, or write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
#
# If you want to redistribute modifications to GROMACS, please
# consider that scientific software is very special. Version
# control is crucial - bugs must be traceable. We will be happy to
# consider code for inclusion in the official distribution, but
# derived work must not be called official GROMACS. Details are found
# in the README & COPYING files - if they are missing, get the
# official version at http://www.gromacs.org.
#
# To help us fund GROMACS development, we humbly ask that you cite
# the research papers on the package. Check out http://www.gromacs.org.

"""Test gromacs.mdrun operation.

Factory produces deferred execution operation.

TODO: Factory expects input for conformation, topology, simulation parameters, simulation state.

TODO: Factory accepts additional keyword input to indicate binding
 to the "potential" interface.
"""

import logging
import os
import pytest

import gmxapi as gmx


# Configure the `logging` module before proceeding any further.
from gmxapi.mapping import make_mapping

gmx.logger.setLevel(logging.WARNING)

try:
    from mpi4py import MPI
    rank_number = MPI.COMM_WORLD.Get_rank()
    comm_size = MPI.COMM_WORLD.Get_size()
except ImportError:
    rank_number = 0
    comm_size = 1
    rank_tag = ''
    MPI = None
else:
    rank_tag = 'rank{}:'.format(rank_number)

# Use this formatter to improve the caplog log records.
#formatter = logging.Formatter(rank_tag + '%(name)s:%(levelname)s: %(message)s')

# For additional console logging, create and attach a stream handler.
# For example:
#    ch = logging.StreamHandler()
#    ch.setFormatter(formatter)
#    logging.getLogger().addHandler(ch)


@pytest.mark.usefixtures('cleandir')
def test_run_from_tpr(spc_water_box, mdrun_kwargs):
    assert os.path.exists(spc_water_box)

    md = gmx.mdrun(spc_water_box, runtime_args=mdrun_kwargs)
    md.run()
    # TODO: better handling of output on unused MPI ranks.


@pytest.mark.usefixtures('cleandir')
def test_mdrun_runtime_args(spc_water_box, caplog, mdrun_kwargs):
    """Test that *runtime_args* is respected.

    When an ensemble is possible, confirm that an array of inputs
    causes each rank to produce a unique simulation with unique output.
    """
    assert gmx.version.has_feature('mdrun_runtime_args')
    with caplog.at_level(logging.DEBUG):
        with caplog.at_level(logging.WARNING, 'gmxapi'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.mdrun'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.modify_input'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.read_tpr'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.simulation'):
            tpr = gmx.read_tpr([spc_water_box] * comm_size)
            # Note: It was originally assumed that each process (each rank) would be executing
            # with the same arguments at the user level and that ensemble differences would
            # happen within the framework. This is not enforced, but nor does it present a
            # particular problem. Nevertheless, pending further design conversations,
            # we will test the normative usage and refrain from doing fancy tricks with
            # rank-based input generation.
            traj_name = 'unusualtrajectoryname.trr'
            runtime_args = {'-o': traj_name}
            runtime_args.update(mdrun_kwargs)
            md = gmx.mdrun(tpr, runtime_args=runtime_args)
            md.run()

            if comm_size == 1:
                output = md.output.trajectory.result()
            else:
                assert comm_size > 1
                output = md.output.trajectory.result()[rank_number]
            assert(str(output).endswith(traj_name))
            assert(os.path.exists(output))
            if comm_size > 1:
                assert md.output.trajectory.result()[0] != md.output.trajectory.result()[1]


@pytest.mark.withmpi_only
@pytest.mark.usefixtures('cleandir')
def test_mdrun_parallel_runtime_args(spc_water_box, caplog, mdrun_kwargs):
    """Test that array input of *runtime_args* is respected.

    Confirm proper resolution of ensemble data flow.
    * Array of runtime_args causes broadcast of singular input.
    * Array of input and array of runtime_args are automatically mapped to parallel data flow.
    """
    assert comm_size > 1
    assert gmx.version.has_feature('mdrun_runtime_args')

    tpr = gmx.read_tpr(spc_water_box)
    output_files = [f'traj{i}.trr' for i in range(comm_size)]
    # Take care not to reference the same dictionary object.
    runtime_args = list(mdrun_kwargs.copy() for i in range(comm_size))
    for i, name in enumerate(output_files):
        runtime_args[i].update({'-o': name})
    md = gmx.mdrun(tpr, runtime_args=runtime_args)
    md.run()
    logging.getLogger().debug(f'testing rank {rank_number} with comm size {comm_size}.')
    output = md.output.trajectory.result()[rank_number]
    assert(str(output).endswith(f'traj{rank_number}.trr'))
    assert(os.path.exists(output))
    assert md.output.trajectory.result()[0] != md.output.trajectory.result()[1]

    tpr = gmx.read_tpr([spc_water_box] * comm_size)
    output_files = [f'traj{i}.trr' for i in range(comm_size)]
    runtime_args = list(mdrun_kwargs.copy() for i in range(comm_size))
    for i, name in enumerate(output_files):
        runtime_args[i].update({'-o': name})
    md = gmx.mdrun(tpr, runtime_args=runtime_args)
    md.run()
    logging.getLogger().debug(f'testing rank {rank_number} with comm size {comm_size}.')
    assert comm_size > 1
    output = md.output.trajectory.result()[rank_number]
    assert(str(output).endswith(f'traj{rank_number}.trr'))
    assert(os.path.exists(output))
    assert md.output.trajectory.result()[0] != md.output.trajectory.result()[1]


@pytest.mark.usefixtures('cleandir')
def test_extend_simulation_via_checkpoint(spc_water_box, mdrun_kwargs):
    assert os.path.exists(spc_water_box)
    assert gmx.version.has_feature('mdrun_runtime_args')

    tpr = gmx.read_tpr(spc_water_box)
    parameters = make_mapping({
        'nsteps': 2,
        'nstxout': 2
    })
    input1 = gmx.modify_input(
        tpr,
        parameters=parameters)
    runtime_args = {
        '-cpo': 'continuation.cpt'
    }
    runtime_args.update(mdrun_kwargs)
    md1 = gmx.mdrun(input1, runtime_args=runtime_args)
    cpt_in = os.path.join(md1.output._work_dir.result(), 'continuation.cpt')
    if rank_number == 0:
        assert os.path.exists(cpt_in)
    input2 = gmx.modify_input(tpr,
                                 parameters={
                                     'nsteps': 4,
                                     'nstxout': 2
                                 })
    runtime_args = {
        '-cpi': cpt_in,
        '-cpo': 'state.cpt',
        '-noappend': None
    }
    runtime_args.update(mdrun_kwargs)
    md2 = gmx.mdrun(input2,
                    runtime_args=runtime_args
                    )
    md2.run()
    # By inspection of the output, we can see that the second trajectory has continued
    # from the checkpoint, but we cannot programmatically confirm it at this point.
    # TODO: Check more rigorously when we can read trajectory files.


@pytest.mark.withmpi_only
@pytest.mark.usefixtures('cleandir')
def test_run_trivial_ensemble(spc_water_box, caplog, mdrun_kwargs):
    with caplog.at_level(logging.DEBUG):
        with caplog.at_level(logging.WARNING, 'gmxapi'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.mdrun'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.modify_input'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.read_tpr'), \
                caplog.at_level(logging.DEBUG, 'gmxapi.simulation'):

            tpr_filename = spc_water_box
            ensemble_width = 2
            simulation_input = gmx.read_tpr([tpr_filename] * ensemble_width)
            assert simulation_input.output.ensemble_width == ensemble_width
            assert len(simulation_input.output._simulation_input.result()) == ensemble_width
            md = gmx.mdrun(simulation_input, runtime_args=mdrun_kwargs)
            assert md.output.ensemble_width == ensemble_width
            md.run()

            output_directory = md.output._work_dir.result()
            logging.info('output_directory result: {}'.format(str(output_directory)))
            assert len(output_directory) == ensemble_width

            # Note that the 'cleandir' test fixture will clean up the output directory on
            # other ranks, so only check the current rank. Generally, our behavior
            # is undefined if the client removes the working directory while the job
            # is in progress. We can consider adding some sort of synchronization at
            # the end of the job if running in temporary directories becomes an
            # important use case outside of testing.
            assert output_directory[0] != output_directory[1]
            if rank_number < ensemble_width:
                assert os.path.exists(output_directory[rank_number])
                assert os.path.exists(md.output.trajectory.result()[rank_number])


@pytest.mark.usefixtures('cleandir')
def test_run_from_read_tpr_op(spc_water_box, caplog, mdrun_kwargs):
    with caplog.at_level(logging.DEBUG):
        with caplog.at_level(logging.DEBUG, 'gmxapi'):
            simulation_input = gmx.read_tpr(spc_water_box)
            md = gmx.mdrun(input=simulation_input, runtime_args=mdrun_kwargs)

            md.run()
            if rank_number == 0:
                assert os.path.exists(md.output.trajectory.result())


@pytest.mark.usefixtures('cleandir')
def test_run_from_modify_input_op(spc_water_box, caplog, mdrun_kwargs):
    with caplog.at_level(logging.DEBUG):

        simulation_input = gmx.read_tpr(spc_water_box)
        modified_input = gmx.modify_input(input=simulation_input, parameters={'nsteps': 4})
        md = gmx.mdrun(input=modified_input, runtime_args=mdrun_kwargs)

        md.run()
