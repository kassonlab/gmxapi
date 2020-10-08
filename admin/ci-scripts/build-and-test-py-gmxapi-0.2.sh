#!/usr/bin/env bash
#
# Build, install, and test the gmxapi 0.2 Python package developed with
# GROMACS 2021.
#
# This script assumes an activated Python venv with the
# gmxapi dependencies already installed, with `python` resolvable by the shell
# to the appropriate Python interpreter.
#
# This script is intended to support automated GROMACS testing infrastructure,
# and may be removed without notice.
#
# WARNING: This script assumes OpenMPI mpiexec. Syntax for launch wrappers from
# other implementations will need different syntax, and we should get a
# MPIRUNNER from the environment, or something.

# Make sure the script errors if any commands error.
set -e

# Create "sdist" source distribution archive.
pushd python_packaging/src
  # TODO: Remove extraneous environment variable with resolution of #3273
  # Ref: https://redmine.gromacs.org/issues/3273
  GMXTOOLCHAINDIR=$INSTALL_DIR/share/cmake/gromacs \
      python setup.py sdist
  # TODO: Identify SDIST

  # Build and install from sdist.
  # Note that tool chain may be provided differently in GROMACS 2020 and 2021.
  GMXTOOLCHAINDIR=$INSTALL_DIR/share/cmake/gromacs \
      python -m pip install \
          --no-cache-dir \
          --no-deps \
          --no-index \
          --no-build-isolation \
          dist/gmxapi*
  # TODO: Build and install from $SDIST instead of wildcard.

popd

# Run Python unit tests.
python -m pytest python_packaging/src/test --junitxml=$PY_UNIT_TEST_XML --threads=2

# Note: Multiple pytest processes getting --junitxml output file argument
# may cause problems, so we set the option on only one of the launched processes.
# See also Multiple Instruction Multiple Data Model for OpenMPI mpirun:
# https://www.open-mpi.org/doc/v3.0/man1/mpiexec.1.php
PROGRAM=(`which python` -m mpi4py -m pytest \
        -p no:cacheprovider \
        $PWD/python_packaging/src/test \
        --threads=1)
# shellcheck disable=SC2068
if [ -x `which mpiexec` ]; then
    PYTHONDONTWRITEBYTECODE=1 \
    mpiexec --allow-run-as-root \
      -x OMP_NUM_THREADS=1 \
      --mca opal_warn_on_missing_libcuda 0 \
      --mca orte_base_help_aggregate 0 \
      -n 1 ${PROGRAM[@]} --junitxml=$PLUGIN_MPI_TEST_XML : \
      -n 1 ${PROGRAM[@]}
fi

# Run Python acceptance tests.
python -m pytest python_packaging/test --junitxml=$PY_ACCEPTANCE_TEST_XML

# Note: Multiple pytest processes getting --junitxml output file argument
# may cause problems, so we set the option on only one of the launched processes.
# See also Multiple Instruction Multiple Data Model for OpenMPI mpirun:
# https://www.open-mpi.org/doc/v3.0/man1/mpiexec.1.php
PROGRAM=(`which python` -m mpi4py -m pytest \
        -p no:cacheprovider \
        $PWD/python_packaging/test \
        --threads=1)
# shellcheck disable=SC2068
if [ -x `which mpiexec` ]; then
    PYTHONDONTWRITEBYTECODE=1 \
    mpiexec --allow-run-as-root \
      -x OMP_NUM_THREADS=1 \
      --mca opal_warn_on_missing_libcuda 0 \
      --mca orte_base_help_aggregate 0 \
      -n 1 ${PROGRAM[@]} --junitxml=$PLUGIN_MPI_TEST_XML : \
      -n 1 ${PROGRAM[@]}
fi
