#include "pybind11/pybind11.h"
#include "pygmx.h"

const char* const name = "pygmx"; // set __name__
const char* const docstring = "GMX module"; // set __doc__

PYBIND11_PLUGIN(pygmx) {
    // Instantiate the module
    py::module m(name, docstring);
    // Declare classes
    py::class_<pygmx::TrajectoryFrame>(m, "TrajectoryFrame")
        .def(py::init<const gmx_trr_header_t&>())
        .def_property_readonly("box", &pygmx::TrajectoryFrame::box, "box matrix");
    py::class_<pygmx::Trajectory>(m, "Trajectory")
        .def(py::init<const std::string &>())
        .def("dump", &pygmx::Trajectory::dump, "Dump trajectory")
        .def_property_readonly("version", &pygmx::Trajectory::version)
        .def("nextFrame", &pygmx::Trajectory::nextFrame);
    // Define module-level functions.
    m.def("version", &pygmx::version, "Get Gromacs version");
    return m.ptr();
}
