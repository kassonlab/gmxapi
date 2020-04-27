#
# This file is part of the GROMACS molecular simulation package.
#
# Copyright (c) 2019,2020, by the GROMACS development team, led by
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

"""Python logging facilities use the built-in logging module.

Upon import, the gmxapi package sets a placeholder "NullHandler" to block
propagation of log messages to the root logger (and sys.stderr, if not handled).

If you want to see gmxapi logging output on sys.stderr, attach a
logging.StreamHandler to the 'gmxapi' logger.

Example::

    ch = logging.StreamHandler()
    # Optional: Set log level.
    ch.setLevel(logging.DEBUG)
    # Optional: create formatter and add to character stream handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add handler to logger
    logging.getLogger('gmxapi').addHandler(ch)

To handle log messages that are issued while importing :py:mod:`gmxapi` and its submodules,
attach the handler before importing :py:mod:`gmxapi`

Each module in the gmxapi package uses its own hierarchical logger to allow
granular control of log handling (e.g. ``logging.getLogger('gmxapi.operation')``).
Refer to the Python :py:mod:`logging` module for information on connecting to and handling
logger output.
"""

__all__ = ['logger']

# Import system facilities
from logging import getLogger, DEBUG, NullHandler

# Define `logger` attribute that is used by submodules to create sub-loggers.
logger = getLogger('gmxapi')
# Prevent gmxapi logs from propagating to the root logger (and to sys.stderr)
# if the user does not take action to handle logging.
logger.addHandler(NullHandler(level=DEBUG))
logger.info("Importing gmxapi.")
