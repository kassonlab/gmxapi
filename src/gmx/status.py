class Status(object):
    """Ultimately hold status for API operation.

    Either this should be inherited by gmx.core.Status or a reference to it or it gets
    much more complicated to maintain the transition between Python and C++ implementation
    code and a consistent interface.
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
