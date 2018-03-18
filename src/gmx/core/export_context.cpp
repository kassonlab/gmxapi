//
// Created by Eric Irrgang on 3/18/18.
//

#include "core.h"

#include "gmxapi/context.h"


namespace gmxpy
{

namespace detail
{

namespace py = pybind11;

void export_context(py::module &m)
{
    using ::gmxapi::Context;
    // Export execution context class
    py::class_<Context, std::shared_ptr<Context>> context(m, "Context");
    context.def(py::init(), "Create a default execution context.");
}

} // end namespace gmxpy::detail

} // end namespace gmxpy
