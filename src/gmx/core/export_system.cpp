/*! \file
 * \brief Bindings for System and session launch.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */

#include "core.h"

#include <iostream>

#include "gmxapi/md.h"
#include "gmxapi/session.h"
#include "gmxapi/status.h"
#include "gmxapi/system.h"

#include "pycontext.h"
#include "pysystem.h"

// Note that PyCapsule symbols from Python.h should be imported by way of the pybind headers, so let's not
// muddy the waters by explicitly including Python.h here unless we want to get more particular about the
// CMake configuration.

namespace gmxpy
{

namespace detail
{

namespace py = pybind11;


void export_system(py::module &m)
{
    using ::gmxapi::System;
    using ::gmxapi::Context;

    // Export session class
    // We can't completely surrender ownership to Python because other API objects may refer to it.
    py::class_<::gmxapi::Session, std::shared_ptr<::gmxapi::Session>> session(m, "MDSession");
    session.def("run", &::gmxapi::Session::run, "Run the simulation workflow");
    session.def("close", &::gmxapi::Session::close, "Shut down the execution environment and close the session.");

    // Export system container class
    py::class_<System, std::shared_ptr<System> > system(m, "MDSystem");
//    system.def(py::init(), "A blank system object is possible, but not useful. Use a helper function.");
    system.def("launch",
                [](System* system, std::shared_ptr<PyContext> context)
                {
                    auto newSession = system->launch(context->get());
                    for (auto && module : context->getSpec()->getModules())
                    {
                        gmxapi::addSessionRestraint(newSession.get(), module);
                    }
                    return newSession;
                },
                "Launch the configured workflow in the provided context.");

    // Module-level function
    m.def("from_tpr", &gmxpy::from_tpr, "Return a system container initialized from the given input record.");
}

} // end namespace gmxpy::detail

} // end namespace gmxpy
