import gmx
import gmx.util

class System(object):
    """Gromacs simulation system objects.

    A System object connects all of the objects necessary to describe a molecular
    system to be simulated.

    Once a system is created, objects can be attached or edited, accessed through
    the following properties.

    Attributes:
        runner (:obj:`gmx.runner.Runner`): workflow runner to be used when executed.
        md (:obj:`gmx.md.MDEngine`): molecular dynamics computation object.

    Example:

        >>> my_sim = gmx.System._from_file(tpr_filename)
        >>> status = my_sim.run()

    Example:

        >>> system = gmx.System()
        >>> md_module = gmx.md.from_tpr(tpr_filename)
        >>> # Get a reference to a runner bound to the MD module.
        >>> runner = gmx.runner.SimpleRunner(md_module)
        >>> system.runner = runner
        >>> # Launch exectution of the runner and work on available resources.
        >>> with gmx.context.DefaultContext(system.runner) as session:
        ...     # Run the work specified in the TPR file
        ...     session.run()
        ...     # Extend the simulation and run an additional 1000 steps.
        ...     status = session.run(1000)
        ...     print(status)
        ...
        gmx.Status(True)
        Success
        >>>

    """

    def __init__(self):
        self.__runner = None
        self.__md = None
        #self.atoms = None
        #self.topology = None

    @property
    def runner(self):
        return self.__runner

    @runner.setter
    def runner(self, runner):
        """

        :type runner: gmx.runner.Runner
        """
        if not isinstance(runner, gmx.runner.Runner):
            message = "Got object of type {} but provided object must be a subclass of gmx.runner.Runner"
            message = message.format(type(runner))
            raise gmx.TypeError(message)
        self.__runner = runner

    @property
    def md(self):
        return self.__md

    @md.setter
    def md(self, md):
        if not isinstance(md, gmx.md.MD):
            raise gmx.TypeError("Provided object must be a subclass of gmx.md.MD")
        self.__md = md

    @staticmethod
    def _from_file(inputrecord):
        """Process a file to create a System object.

        Calls an appropriate helper function to parse a file in the current
        context and create a System object. If no Context is currently bound, a
        local default context is created and bound.

        TODO: clarify the file location relative to the execution context.
        Until then, this helper method should not be part of the public
        interface.

        Args:
            inputrecord (str): input file name

        Returns:
            gmx.System

        Example:
            simulation = gmx.System._from_file('membrane.tpr')
            status = simulation.run()

        """
        if gmx.util._filetype(inputrecord) is gmx.fileio.TprFile:
            # we use the API to process TPR files. We create a MD module and
            # retrieve a system from its contents.
            md_module = gmx.md.from_tpr(inputrecord)
            newsystem = gmx.core.from_tpr(inputrecord)
            if newsystem is None:
                raise gmx.Error("Got empty system when reading TPR file.")
        else:
            raise gmx.UsageError("Need a TPR file.")
        newrunner = gmx.runner.SimpleRunner()
        newrunner._runner = newsystem.runner
        system = System()
        system.runner = newrunner
        # TBD as md runner is reimplemented:
        #system.atoms = md_module.atoms
        #system.topology = md_module.topology

        #runner = gmx.runner.SimpleRunner(md_module)
        #system.runner = runner

        return system

    def run(self, parameters=None):
        """Launch execution.

        If the System is attached to a Context, the Context is initialized, if
        necessary, and its instance run()
        method is called. If there is not yet a Context, one is created and then
        used.

        Note: currently always initializes new context informed by the runner.

        Args:
            parameters: optional parameters to pass to runner. Parameter type varies by runner type.
        Returns:
            Gromacs status object.

        """
        with gmx.context.DefaultContext(self.runner) as session:
            if parameters is None:
                return session.run()
            else:
                return session.run(parameters)
