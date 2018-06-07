# Build container for gmxapi/gmxapi:<tag>
# Initially we will use a tmpi libgromacs and openmpi mpi4py

FROM gmxapi/gromacs-gmxapi:devel

# Allow build for an arbitrary branch or tag, but default to the tip of `master`
ARG BRANCH=devel

RUN conda install pytest tox cmake

# At least one conda release does not leave tox executable...
# However, tox doesn't seem to be helping us here...
# RUN chmod a+x /opt/conda/bin/tox

# Note default for the base image at this point is Python3
RUN pip install --upgrade pip && \
    pip install sphinx mpi4py

RUN pip install --upgrade setuptools --user

#ADD --chown=1000:100 gmxpy /home/jovyan/gmxpy

RUN wget https://github.com/kassonlab/gmxapi/archive/$BRANCH.zip && \
    unzip $BRANCH.zip && \
    rm -rf /home/jovyan/gmxpy && \
    mv gmxapi-$BRANCH /home/jovyan/gmxpy && \
    rm $BRANCH.zip

RUN (cd /home/jovyan/gmxpy && \
    gmxapi_DIR=/home/jovyan/install/gromacs pip install . --upgrade --verbose)

# Test with
#    docker run --cpus 2 --rm -ti gmxapi/gmxapi bash -c "cd gmxpy && mpiexec -n 2 python -m mpi4py -m pytest  --log-cli-level=DEBUG --pyargs gmx -s --verbose"
