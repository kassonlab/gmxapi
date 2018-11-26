//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "tprfile.h"

namespace gmxpy {

class PyTprFileHandle
{
    // C++ may need to extend the life of a TprFile object provided by the Python
    // interpreter, so we use a reference-counted holder.
    std::shared_ptr<TprFileHandle> filehandle_;
};

void detail::export_tprfile(pybind11::module &m)
{
    namespace py = pybind11;

    py::class_<PyTprFileHandle> tprfile(m, "TprFile");

    m.def("copy_tprfile",
          &gmxpy::copy_tprfile,
          py::arg("source"),
          py::arg("destination"),
          py::arg("end_time"),
          "Copy a TPR file from `source` to `destination`, replacing `nsteps` with `end_time`.");
}

} // end namespace gmxpy
