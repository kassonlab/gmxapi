from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

class Status(object):
    """Status for API operation.

    As of gmxapi 0.0.6, there is not a clear mapping between gmx.status.Status
    and gmx.core.Status.

    Reference https://github.com/kassonlab/gmxapi/issues/121
    """
    def __init__(self, success=True):
        self.success = bool(success)

    def __str__(self):
        if self.success:
            return "Success"
        else:
            return "Failure"

    def __repr__(self):
        return "gmx.Status({})".format(self.success)
