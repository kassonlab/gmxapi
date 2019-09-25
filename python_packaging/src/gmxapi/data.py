"""Provide helpers to access package data.

Some sample files are provided with the module for testing purposes.
"""

# At some point, these will probably be accessed in the newer get_data()
# idiom, but an unzippable package and direct file access is okay for now.

import os

from gmxapi import exceptions

tpr_filename = None

_tpr_filename = 'data/topol.tpr'
try:
    from pkg_resources import resource_filename

    _tpr_filename = resource_filename(__name__, _tpr_filename)
except Exception as e:
    raise exceptions.ApiError("Need pkg_resources from setuptools package to access gmx "
                              "package data.") from e

if os.path.exists(_tpr_filename) and os.path.isfile(_tpr_filename):
    tpr_filename = os.path.abspath(_tpr_filename)
else:
    raise exceptions.ApiError('Package data file data/topol.tpr not accessible at {}'.format(_tpr_filename))
