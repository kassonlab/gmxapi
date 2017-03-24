#!/usr/bin/env/python
#
# Provide Python access to trajectory files via the
# Trajectory Analysis Framework.
#
# 1. Python asks for first frame.
# 2. Runner starts.
# 3. Runner calls analyze_frame.
# 4. Runner returns control to Python interpreter.
# 5. Python accesses the frame by interacting with the module.
# 6. Python asks for next frame.
# 7. Runner calls finish for the current frame and analyze for the next.
# 8. Runner returns control to Python.
# 9. When Runner runs out of frames, it cleans up and raises StopIteration.
# 10. When Python leaves the context object or otherwise destroys the runner, it cleans up.
#
# Example usage:
#
#    import gmx
#
#    # Create the Python proxy to the caching gmx::TrajectoryAnalysisModule object.
#    mytraj = gmx.io.TrajectoryFile(filename, 'r')
#
#    # Implicitly create the Runner object and get an iterator based on selection.
#    frames = mytraj.select(...)
#
#    # Iterating on the module advances the Runner.
#    # Since the Python interpreter is explicitly asking for data,
#    # the runner must now be initialized and begin execution.
#    # mytraj.runner.initialize(context, options)
#    # mytraj.runner.next()
#    next(frames)
#
#    # Subsequent iterations only need to step the runner and return a frame.
#    for frame in frames:
#        # do some stuff
#
#    # The generator yielding frames has finished, so the runner has been released.
#    # The module caching the frames still exists and could still be accessed or
#    # given to a new runner with a new selection.
#    for frame in mytraj.select(...):
#        # do some other stuff

import io
import core
