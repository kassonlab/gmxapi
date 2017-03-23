/*! \internal \file
 * \brief Exports Python bindings for gmx.core module.
 *
 * \ingroup module_python
 */

#include "pybind11/pybind11.h"
#include "gmx_core.h"

const char* const name = "core"; ///< used to set __name__
const char* const docstring = "Gromacs core module"; ///< used to set __doc__

/*! \internal \brief Export gmx.core Python module in shared object file.
 */
PYBIND11_PLUGIN(core) {
    // Instantiate the module
    py::module m(name, docstring);

    // Declare classes
    py::class_< pygmx::PyRunner >(m, "TafRunner")
        .def(py::init< std::shared_ptr<gmx::TrajectoryAnalysisModule> >())
        //.def("initialize")
        .def("next");

/*
    py::class_< gmx::Options >(m, "Options")
        .def(py::init<>()); // Need to figure out options passing...

    py::class_< gmx::trajectoryanalysis::CachingTafModule >(m, "CachingTafModule")
        .def("frame");

    py::class_< gmx::Selection >(m, "Selection");
*/

    return m.ptr();
}
