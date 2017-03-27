/*! \internal \file
 * \brief Exports Python bindings for gmx.core module.
 *
 * \ingroup module_python
 */

#include "gmx_core.h"

// TODO: Tell doxygen to suggest quotes instead of angle brackets for headers.
#include "gromacs/trajectoryanalysis/runner.h"
#include "gromacs/trajectoryanalysis/analysismodule.h"
#include "gromacs/trajectoryanalysis/modules/caching.h"
#include "gromacs/options/options.h"
#include "gromacs/options/filenameoptionmanager.h"
#include "gromacs/utility/exceptions.h"
#include "gromacs/options/optionsassigner.h"

#include "pybind11/pybind11.h"

using std::shared_ptr;
using std::make_shared;

namespace gmx
{
namespace pyapi
{

PyOptions::PyOptions() :
    options_{make_shared<gmx::Options>()}
{
}

PyOptions::PyOptions(std::string filename) :
    options_{make_shared<gmx::Options>()},
    filename_{filename}
{}

PyOptions::~PyOptions()
{}

gmx::Options& PyOptions::data()
{
    // Return a pointer to the Options object
    return *options_;
}

class Assigner
{
public:
    Assigner(gmx::Options& options) : assigner_{&options}
    {
        assigner_.start();
    };
    ~Assigner()
    {
        assigner_.finish();
    };
    bool tryStartOption(const std::string& name)
    {
        return assigner_.tryStartOption(name.c_str());
    };
    bool addSingleValue(const std::string& value)
    {
        try
        {
            assigner_.appendValue(value.c_str());
        }
        catch (GromacsException &ex)
        {
            assigner_.finishOption();
            return false;
        }
        assigner_.finishOption();
        return true;
    };

private:
    gmx::OptionsAssigner assigner_;
};

bool PyOptions::parse()
{
    // use gmx::OptionsAssigner to set parsed options, but refer to
    // CommandLineParser().impl_->assigner for example helper functions.
    // Note that toOptionName just identifies command-line flags and strips
    // them into the form of an option name. We can do this with py dict...
    // E.g.
    //    assigner.start();
    //    // loop over args
    //    const char* const optionName = toOptionName(arg);
    //    // note, arg sets optionName = nullptr implies append to previous option
    //    try
    //        is_valid_name = assigner.tryStartOption(optionName);
    //        // handle invalid options...
    //    catch (UserInputError &ex)
    //        // badly formed option argument
    //    // If instead we are appending:
    //    assigner.appendValue(arg) // throws GromacsException
    //    // conclude single or multivalue options. Multivalue options receive
    //    // additional checking and get another chance to throw.
    //    assigner.finishOption() // throws UserInputError
    //    // end loop
    //    assigner.finish();
    //
    // In the longer term, the options object has a parser available after
    // interacting with the module runner, and can then
    // provide useful user help. It probably doesn't make sense to allow kwargs
    // in a generic and configurable Python class, but maybe the various
    // components can be independently configured or accessed statically to
    // build an argparse-like object. I suppose that's what the help generator
    // does...

    // TrajectoryRunnerCommon names the filename option "f"
    Assigner assigner{*options_};

    const std::string name{"f"};

    try // assign a new option
    {
        if (assigner.tryStartOption(name.c_str()))
        {
            // assign (all of) the value(s) for name
            if (!assigner.addSingleValue(filename_.c_str()))
            {
                throw(InvalidInputError("bad option value"));
            }
            // else value successfully appended
        }
        else
        {
            throw(InvalidInputError("bad option name"));
        };
    }
    catch (InvalidInputError &ex)
    {
        // InvalidInputError is thrown if option is not recognized or inappropriate (e.g. specified more than once)
        throw(ex);
    }
    return true;
}

PyRunner::PyRunner(shared_ptr<gmx::TrajectoryAnalysisModule> module) :
    runner_(),
    module_(module)
{
    runner_.add_module(module_);
}

PyRunner::~PyRunner() {}

bool PyRunner::next()
{
    return runner_.next();
}

void PyRunner::initialize(PyOptions options)
{
    gmx::FileNameOptionManager filename_option_manager;
    options.data().addManager(&filename_option_manager);
    runner_.register_options(options.data());
    // parse options...
    if (!options.parse())
        throw(InvalidInputError("could not parse"));
    options.data().finish();
    runner_.initialize(options.data());
}

} // end namespace pyapi
} // end namespace gmx

// Export Python module.

namespace py = pybind11;

const char* const name = "core"; ///< used to set __name__
// pybind11 uses const char* objects for docstrings. C++ raw literals can be used.
const char* const docstring = "Gromacs core module"; ///< used to set __doc__

/*! \internal \brief Export gmx.core Python module in shared object file.
 */
PYBIND11_PLUGIN(core) {
    // Instantiate the module
    py::module m(name, docstring);

    // Export runner class
    py::class_< gmx::pyapi::PyRunner > runner(m, "TafRunner");
    // We shouldn't need a keep_alive<>() for the module we're attaching since
    // pybind knows how to handle shared_ptr and this object does not need to
    // survive after the associated module is done with it, but we need to
    // reconsider when the usage model changes for chained or more general modules.
    runner.def(py::init< shared_ptr<gmx::TrajectoryAnalysisModule> >())
        .def("initialize", &gmx::pyapi::PyRunner::initialize, "handle options")
        .def("next", &gmx::pyapi::PyRunner::next, "Advance the current frame one step.");

    // Export module classes
    py::class_< gmx::TrajectoryAnalysisModule,
                shared_ptr<gmx::TrajectoryAnalysisModule>
              >(m, "TafModuleAbstractBase");
    // Default holder is std::unique_ptr, but we allow multiple handles to module.
    py::class_< gmx::trajectoryanalysis::CachingTafModule,
                shared_ptr<gmx::trajectoryanalysis::CachingTafModule>,
                gmx::TrajectoryAnalysisModule
              >(m, "CachingTafModule")
        .def(py::init())
        //.def("select", py:make_iterator...)
        .def("frame", &gmx::trajectoryanalysis::CachingTafModule::frame, "Retrieve cached trajectory frame.");

    py::class_< gmx::pyapi::PyOptions >(m, "Options")
        .def(
            py::init<const std::string>(),
            py::arg("filename")
        )
        ;
/*
    py::class_< gmx::Options >(m, "Options")
        .def(py::init<>()); // Need to figure out options passing...


    py::class_< gmx::Selection >(m, "Selection");
*/

    return m.ptr();
}
