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

#include "pybind11/pybind11.h"

namespace gmx
{
namespace pyapi
{

PyRunner::PyRunner(std::shared_ptr<gmx::TrajectoryAnalysisModule> module) {}
PyRunner::~PyRunner() {}

void PyRunner::next() {}

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
    runner.def(py::init< std::shared_ptr<gmx::TrajectoryAnalysisModule> >())
        /*
        .def(py::init())
        */
        //.def("initialize")
        .def("next", &gmx::pyapi::PyRunner::next, "Advance the current frame one step.");

    // Export module classes
    py::class_< gmx::TrajectoryAnalysisModule,
                std::shared_ptr<gmx::TrajectoryAnalysisModule>
              >(m, "TafModuleAbstractBase");
    // Default holder is std::unique_ptr, but we allow multiple handles to module.
    py::class_< gmx::trajectoryanalysis::CachingTafModule,
                std::shared_ptr<gmx::trajectoryanalysis::CachingTafModule>,
                gmx::TrajectoryAnalysisModule
              >(m, "CachingTafModule")
        .def(py::init())
        //.def("select", py:make_iterator...)
        .def("frame", &gmx::trajectoryanalysis::CachingTafModule::frame, "Retrieve cached trajectory frame.");
/*
    py::class_< gmx::Options >(m, "Options")
        .def(py::init<>()); // Need to figure out options passing...


    py::class_< gmx::Selection >(m, "Selection");
*/

    return m.ptr();
}
