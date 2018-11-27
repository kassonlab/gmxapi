//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "tprfile.h"
#include <pybind11/stl.h>

namespace gmxpy {

void detail::export_tprfile(pybind11::module &m)
{
    namespace py = pybind11;
    using gmxapicompat::TprFileHandle;
    using gmxapicompat::readTprFile;

    py::class_<TprFileHandle> tprfile(m, "TprFile");
    tprfile.def("params",
            [](const TprFileHandle& self)
            {
                return gmxapicompat::keys(gmxapicompat::getMdParams(self));
            });

    m.def("read_tprfile",
            &readTprFile,
            py::arg("filename"),
            "Get a handle to a TPR file resource for a given file name.");

    m.def("copy_tprfile",
          &gmxpy::copy_tprfile,
          py::arg("source"),
          py::arg("destination"),
          py::arg("end_time"),
          "Copy a TPR file from `source` to `destination`, replacing `nsteps` with `end_time`.");
}

} // end namespace gmxpy
