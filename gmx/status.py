class Status(object):
    """Ultimately hold status for API operation.

    This should probably inherit from gmx.core.Status.
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
