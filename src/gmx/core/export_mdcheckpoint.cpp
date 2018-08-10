//
// Created by Eric Irrgang on 8/10/18.
//

#include "core.h"
#include "mdcheckpoint.h"

void gmxpy::detail::export_mdcheckpoint(pybind11::module &m) {
    namespace py = pybind11;

    // C++ may need to hold onto a MDCheckpoint for longer than a single Python
    // function call, so we should use a reference-counted handle.
    py::class_<MDCheckpoint, std::shared_ptr<MDCheckpoint>>
    mdcheckpoint(m, "MDCheckpoint", "Handle to a simulation checkpoint.");
}
