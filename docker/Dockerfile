# Build container for gmxapi/gmxapi:<tag>
# Initially we will use a tmpi libgromacs and openmpi mpi4py

# The default entry point for the resulting container is a jupyter notebook server, so
# assuming you have port 8888 free locally, access the web interface by binding the 8888 ports
# on host and container.
#
#    docker build -t gmxapi .
#    docker run --rm -ti -p 8888:8888 gmxapi
#
# Then use the URL in the terminal output to access the web server in the docker container on
# the local host. Documentation for the gmxapi Python module is accessible in the `docs` directory.
# Click on the `docs` link and then `index.html`
#
# To build from a branch other than 'master,' pass a build arg. For example:
#
#    docker build --build-arg BRANCH=devel -t gmxapi .
#
# If the repository has been updated, but the Dockerfile has not, specify `--no-cache` to `docker build`.
#
# Tagged docker images are available through Docker Hub by pulling / running gmxapi/gmxapi:master
# or gmxapi/gmxapi:devel
#
#    docker run --rm -ti gmxapi/gmxapi:devel
#
# Note that the `--rm` flag in the above commands means that the container you run from the image
# will be temporary. If you want to keep changes that you make, refer to Docker documentation on
# container naming, committing snapshots, and managing containers and disk space.
#

FROM gmxapi/gromacs-gmxapi:0.0.7

# Allow build for an arbitrary branch or tag, but default to the tip of `master`
ARG BRANCH=master
# URL where the archive file for BRANCH is located.
ARG SOURCE_URL=https://github.com/kassonlab/gmxapi/archive

RUN conda install pytest tox cmake

# At least one conda release does not leave tox executable...
# However, tox doesn't seem to be helping us here...
# RUN chmod a+x /opt/conda/bin/tox

# Note default for the base image at this point is Python3
RUN pip install --upgrade pip && \
    pip install sphinx sphinx-rtd-theme mpi4py

RUN pip install --upgrade setuptools --user

RUN wget $SOURCE_URL/$BRANCH.zip && \
    unzip $BRANCH.zip && \
    rm -rf /home/jovyan/gmxpy && \
    mv gmxapi-$BRANCH /home/jovyan/gmxpy && \
    rm $BRANCH.zip

RUN (cd /home/jovyan/gmxpy && \
    mkdir build && \
    cd build && \
    gmxapi_DIR=/home/jovyan/install/gromacs cmake .. && \
    make install)

RUN (cd /home/jovyan/gmxpy/build && \
    make docs && \
    mv docs /home/jovyan/)

# Test with
#    docker run --cpus 2 --rm -ti gmxapi/gmxapi bash -c \
#        "cd gmxpy && mpiexec -n 2 python -m mpi4py -m pytest  --log-cli-level=DEBUG --pyargs gmx -s --verbose"
