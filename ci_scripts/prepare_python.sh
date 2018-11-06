#!/usr/bin/env bash
#
# Prepare the environment for the current Python interpreter. Assumes the
# current shell environment variable PYTHON contains the path to the intended
# Python interpreter. Assumes the environment variable MPICC is set to an
# appropriate compiler wrapper (will be used to build mpi4py). Then this script
# makes sure mpi4py is built with the intended compiler.
#
# To use, evaluate the results of this script in the root directory of the
# gmxapi repository, i.e. the directory containing `requirements.txt`
#
# Example:
#     $ export PYTHON=`which python`
#     $ eval $(./ci_scripts/prepare_python.sh)
#

if [ -x "$PYTHON" ] ; then
    # Quiet output if QUIET is non-null
    echo "$PYTHON -m pip install --upgrade pip setuptools ${QUIET:+'-q'};
    $PYTHON -m pip install --no-cache-dir --upgrade --no-binary \":all:\" --force-reinstall mpi4py  ${QUIET:+'-q'};
    $PYTHON -m pip install -r requirements.txt ${QUIET:+'-q'}"
else
    echo "echo Set PYTHON to a Python interpreter before using prepare_python.sh"
fi
