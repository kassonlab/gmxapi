#include "pybind11/pybind11.h"
#include "pygmx.h"

const char* const name = "pygmx"; // set __name__
const char* const docstring = "GMX module"; // set __doc__

PYBIND11_PLUGIN(pygmx) {
    py::module m(name, docstring);
    m.def("version", &pygmx::version, "Get Gromacs version");
    return m.ptr();
}
