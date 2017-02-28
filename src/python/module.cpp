#include "pybind11/pybind11.h"
#include "pygmx.h"

const char* const name = "pygmx"; // set __name__
const char* const docstring = "GMX module"; // set __doc__

PYBIND11_PLUGIN(pygmx) {
    // Instantiate the module
    py::module m(name, docstring);
    // Declare classes
    py::class_<pygmx::Trajectory>(m, "Trajectory")
        .def(py::init<const std::string &>())
        .def("dump", &pygmx::Trajectory::dump, "Dump trajectory");
    // Define module-level functions.
    m.def("version", &pygmx::version, "Get Gromacs version");
    m.def("trx", &pygmx::list_trx, "Dump a trajectory file");
    return m.ptr();
}
