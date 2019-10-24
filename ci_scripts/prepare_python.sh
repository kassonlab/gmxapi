#!/bin/bash

# Prepare the environment for the current Python interpreter. Assumes the
# current shell environment variable PYTHON contains the path to the intended
# Python interpreter. Assumes the environment variable MPICC is set to an
# appropriate compiler wrapper (will be used to build mpi4py). Then this script
# makes sure mpi4py is built with the intended compiler.

set -ev

# TODO: Use a tagged release of mpi4py. 3.0.2 did not support Python 3.8.0.

if [ -x "$PYTHON" ] ; then
    # Quiet output if QUIET is non-null
    $PYTHON -m pip install --upgrade pip setuptools ${QUIET:+'-q'}
    $PYTHON -m pip install --no-cache-dir --upgrade --no-binary \":all:\" --force-reinstall https://bitbucket.org/mpi4py/mpi4py/get/maint.tar.gz  ${QUIET:+'-q'}
    $PYTHON -m pip install -r python_packaging/src/requirements.txt ${QUIET:+'-q'}
    $PYTHON -m pip install -r python_packaging/requirements-docs.txt ${QUIET:+'-q'}
    $PYTHON -m pip install -r python_packaging/requirements-test.txt ${QUIET:+'-q'}
else
    echo Set PYTHON to a Python interpreter before using prepare_python.sh
fi
