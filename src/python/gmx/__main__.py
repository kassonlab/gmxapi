#!/usr/bin/env python

"""
Provides the gmx.__main__() method for the gmx package main module.
Defines behavior when module is invoked as a script or with
``python -m gmx``
"""

from .io import TrajectoryFile

# Create the Python proxy to the caching gmx::TrajectoryAnalysisModule object.
filename = 'em-vac.trr'
mytraj = TrajectoryFile(filename, 'r')

# Implicitly create the Runner object and get an iterator based on selection.
#frames = mytraj.select(...)

# Iterating on the module advances the Runner.
# Since the Python interpreter is explicitly asking for data,
# the runner must now be initialized and begin execution.
# mytraj.runner.initialize(context, options)
# mytraj.runner.next()
frames = mytraj.select('not implemented')
try:
    print(next(frames))
except StopIteration:
    print("no frames")

# Subsequent iterations only need to step the runner and return a frame.
for frame in frames:
    print(frame)

# The generator yielding frames has finished, so the runner has been released.
# The module caching the frames still exists and could still be accessed or
# given to a new runner with a new selection.
#for frame in mytraj.select(...):
#   # do some other stuff
