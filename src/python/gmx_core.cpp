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
#include "gromacs/options/optionsvisitor.h"
#include "gromacs/trajectory/trajectoryframe.h"

//#include <iostream>

#include "pybind11/pybind11.h"

using std::shared_ptr;
using std::make_shared;

namespace gmx
{
namespace pyapi
{

PyOptions::PyOptions() :
    options_{}
{
    //print_options(*this);
}

PyOptions::PyOptions(std::string filename) :
    options_{},
    filename_{filename}
{}

PyOptions::~PyOptions()
{}

gmx::Options* PyOptions::data()
{
    // Return a pointer to the Options object
    return &options_;
}


bool PyOptions::parse()
{
    /// Helper class for RAII wrapping of gmx::OptionsAssigner
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

        bool startOption(const std::string& name)
        {
            assigner_.startOption(name.c_str());
            return true;
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

    // Scope the lifetime of assigner
    {
        Assigner assigner{options_};
        // TrajectoryRunnerCommon names the filename option "f"

        const std::string name{"f"};

        try // assign a new option
        {
            if (assigner.startOption(name.c_str()))
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
    }
    options_.finish();
    //print_options(*this);
    return true;
}

void PyOptions::view_traverse(gmx::OptionsVisitor&& visitor) const
{
    visitor.visitSection(options_.rootSection());
}

void print_options(const PyOptions& pyoptions)
{
    /// Provide a way to explore the PyOptions object
    /*! gmx::OptionsVisitor defines an interface for visitor classes.
     *  gmx::OptionsIterator provides a means to traverse an Options collection
     *  as a non-member from arbitrary calling code, rather than as a member function of the collection,
     *  which would be more like the Visitor pattern I'm used to.
     *  gmx::OptionsIterator decorates an Options object to provide
     *  acceptSection(OptionsVisitor*) and acceptOptions(OptionsVisitor*)
     *  so that a visitor object should have its visit methods
     *  called directly. E.g. Visitor().visitSection(options.rootSection()) calls
     *  OptionsIteratory(options.rootSection()).acceptSections(visitor) and again
     *  for acceptOptions(visitor). It is not documented whether OptionsIterator.acceptSections(visitor) is made recursive through the Visitor's implementation of visitSection.
     */
    // TODO: IOptionsContainer can only throw APIError and has no way to tell
    // the caller that an option is already defined. However, it is implemented
    // in gmx::Options, so the calling code can get there in a roundabout way.
    // TODO: There is no const version of gmx::OptionsVisitor
    class Visitor : public gmx::OptionsVisitor
    {
        virtual void visitSection(const gmx::OptionSectionInfo& section)
        {
            // note hierarchy...
            // const std::string name = section.name()
            gmx::OptionsIterator iterator(section);
            iterator.acceptSections(this);
            iterator.acceptOptions(this);
        }
        virtual void visitOption(const OptionInfo &option)
        {
            // Do something...
            const std::string name = option.name();
            const bool is_set = option.isSet();

            // Can't see values? OptionInfo::option() returns a AbstractOptionStorage& but is a protected function.
            // There does not appear to be a way to get the OptionType (template
            // parameter) settings object used in addOption. OptionType is
            // derived from AbstractOption, I think. Unless there is a default
            // value, there is no option value until the Assigner runs, which
            // operates on a full gmx::Options object. Then the value is owned
            // by the caller of IOptionsContainer.addOption()
            // Where does the reference in AbstractOption.store(T*) end up?
            // Options have a T* store_ that points to the storage defined
            // in the object passed to addOption().
            // OptionSectionImpl::Group::addOptionImpl(AbstractOption& settings) calls
            // settings.createStorage() to get a OptionSectionImpl::AbstractOptionStoragePointer object.
            // When the Assigner gets to appendValue, there is ultimately a
            // commitValues() template method that calls OptionStorageTemplate<T>::store_->append(value). Here, store_ was
            // initialized in the constructor and is a
            // std::unique_ptr<IOptionValueStore<T> >
            // IOptionValueStore<T> is a wrapper that is implemented by various
            // basic ValueStore types to
            // provide some methods and a wrapped ArrayRef<T>.
            // Assigner::Impl uses Options::impl_->rootSection_ to get a
            // internal::OptionSectionImpl which provides findOption() to get
            // an AbstractOptionStorage*. AbstractOptionsStorage->appendValue()
            // results in the values actually being set through virtual functions
            // in the inaccessible OptionStorage object.
            // There appears to be no way to get from either an Options or
            // OptionInfo object to the OptionStorageTemplate object that can
            // see the actual storage. I would need to implement an alternative
            // IOptionsContainer or cause the modules to provide some interface.
            // Also, the parsed option values appear temporarily in the machinery
            // but I think are gone after assignment completes.
            //
            // In short, if I want to see the values being passed now, I can
            // look at the raw memory for the storage destinations, the values
            // being handled by the Assigner, or add printf debugging into the
            // core options handling code...
        }
    };
    pyoptions.view_traverse(Visitor());
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

void PyRunner::initialize(PyOptions& options)
{
    //gmx::FileNameOptionManager filename_option_manager;
    //options.data()->addManager(&filename_option_manager);
    //print_options(options);
    runner_.register_options(*options.data());
    // parse options...
    if (!options.parse())
        throw(InvalidInputError("could not parse"));
    //print_options(options);
    options.data()->finish();
    //print_options(options);
    runner_.initialize(*options.data());
    ////print_options(options);
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
    using namespace gmx::pyapi;

    // Instantiate the module
    py::module m(name, docstring);

    // Export runner class
    py::class_< PyRunner > runner(m, "TafRunner");
    // We shouldn't need a keep_alive<>() for the module we're attaching since
    // pybind knows how to handle shared_ptr and this object does not need to
    // survive after the associated module is done with it, but we need to
    // reconsider when the usage model changes for chained or more general modules.
    runner.def(py::init< shared_ptr<gmx::TrajectoryAnalysisModule> >())
        .def("initialize", &PyRunner::initialize, "handle options")
        .def("next", &PyRunner::next, "Advance the current frame one step.");

    // Export module classes
    py::class_< gmx::TrajectoryAnalysisModule,
                shared_ptr<gmx::TrajectoryAnalysisModule>
              >(m, "TafModuleAbstractBase");

    py::class_< PyTrajectoryFrame, shared_ptr<PyTrajectoryFrame> > (m, "Frame");
    // Default holder is std::unique_ptr, but we allow multiple handles to module.
    py::class_< gmx::trajectoryanalysis::CachingTafModule,
                shared_ptr<gmx::trajectoryanalysis::CachingTafModule>,
                gmx::TrajectoryAnalysisModule
              >(m, "CachingTafModule")
        .def(py::init())
        //.def("select", py:make_iterator...)
        //.def("frame", &gmx::trajectoryanalysis::CachingTafModule::frame, "Retrieve cached trajectory frame.")
        .def("frame",
            [](const gmx::trajectoryanalysis::CachingTafModule &cache) -> shared_ptr<PyTrajectoryFrame>
            {
                return std::make_shared<PyTrajectoryFrame>(cache.frame());
            }
        );

    py::class_< PyOptions, std::shared_ptr<PyOptions> >(m, "Options")
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
