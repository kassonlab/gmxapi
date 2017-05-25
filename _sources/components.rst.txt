==========
Components
==========

This describes major sections of the project from a development perspective.
Hierarchical functionality descriptions help group features to guide development.
For documentation organized by interface level, see :doc:`layers`.
This section describes groups of functionality that require development at multiple levels, but for which design and development are compartmentalized.

.. toctree::

    components/fileio
    components/microstate
    components/graphmodules
    components/context
    components/plugins

A Gromacs extension may use interfaces to several components, but should
access each at the highest and most stable interface that is reasonable.
For instance, consider an extension to steer a simulation to refine a model
against experimental SAXS data and that is

* configured through the Python interface before launching the simulation
* is originally designed to read experimental data from a file, and
* registers code with hooks in the simulation loop

The respective Python and C++ aspects may look something like the following.

At the Python API level:

.. code-block:: python

    class SaxsFileFormat(gmx.fileio.File):
        ...

    class SaxsInput(gmx.types.StaticArrayData):
        ...
        def from_file(filename):
            SaxsFileFormat(filename, 'r')
            return process_data()

    class SaxsPlugin(gmx.md.Plugin):
        def __init__(self, mysaxsinput):
            ...

At various levels in the C++ implementation:

.. code-block:: cpp

    class SaxsPlugin : public ISimulationPlugin
    {
    public:
        // Implement ISimulationPlugin interface
        ...

        // Provide additional behavior:
        // Consume reference data.
        void register_reference_data(shared_ptr<gmxapi::StaticArrayData> data);
    };

    // Helper class for external interface
    class SaxsData
    {
    public:
        // Give interface to caller
        shared_ptr<gmxapi::StaticArrayData> datahandle();

        // helper function for controller interface
        void from_file(shared_ptr<gmxapi::io::ArrayDataFile> filehandle);
    }

    // API object implementing custom file reader.
    class SaxsFile : gmxapi::io::ArrayDataFile
    {
        // Implement ArrayDataFile interface
    }
