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
PyRunner::PyRunner() {}
PyRunner::~PyRunner() {}

void PyRunner::next() {}

} // end namespace pyapi
} // end namespace gmx

// Export Python module.

namespace py = pybind11;

const char* const name = "core"; ///< used to set __name__
const char* const docstring = "Gromacs core module"; ///< used to set __doc__

/*! \internal \brief Export gmx.core Python module in shared object file.
 */
PYBIND11_PLUGIN(core) {
    // Instantiate the module
    py::module m(name, docstring);

    // Declare classes
    py::class_< gmx::pyapi::PyRunner >(m, "TafRunner")
        /* use empty constructor for initial test
        .def(py::init< std::shared_ptr<gmx::TrajectoryAnalysisModule> >())
        */
        .def(py::init())
        //.def("initialize")
        .def("next", &gmx::pyapi::PyRunner::next, "Advance the current frame one step.");

    py::class_< gmx::trajectoryanalysis::CachingTafModule >(m, "CachingTafModule")
        .def(py::init())
        .def("frame", &gmx::trajectoryanalysis::CachingTafModule::frame, "Retrieve cached trajectory frame.");
/*
    py::class_< gmx::Options >(m, "Options")
        .def(py::init<>()); // Need to figure out options passing...


    py::class_< gmx::Selection >(m, "Selection");
*/

    return m.ptr();
}
