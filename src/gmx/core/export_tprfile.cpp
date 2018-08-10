//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "tprfile.h"

void gmxpy::detail::export_tprfile(pybind11::module &m)
{
    namespace py = pybind11;

    // C++ may need to extend the life of a TprFile object provided by the Python
    // interpreter, so we need a reference-counted holder.
    py::class_<TprFile, std::shared_ptr<TprFile>> tprfile(m, "TprFile");
    tprfile.def("__enter__", )
}
