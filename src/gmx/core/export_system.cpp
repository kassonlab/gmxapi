#include "core.h"

#include <iostream>

#include "gmxapi/md.h"
#include "gmxapi/context.h"
#include "gmxapi/session.h"
#include "gmxapi/status.h"
#include "gmxapi/system.h"

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

    // Export system container class
    py::class_<System, std::shared_ptr<System> > system(m, "MDSystem");
    system.def(py::init(), "A blank system object is possible, but not useful. Use a helper function.");
    system.def("launch",
               [](System* system){ return system->launch(); },
               "Launch the configured workflow in the default context.");
    system.def("launch",
                [](System* system, std::shared_ptr<Context> context)
                {
                    return system->launch(context);
                },
                "Launch the configured workflow in the provided context.");

    system.def(
        "add_mdmodule",
        [](System* system, py::object force_object){
            // If force_object has a bind method, give it a PyCapsule with a pointer
            // to our C++ object.
            if (py::hasattr(force_object, "bind"))
            {
                auto spec = system->getSpec();
                auto holder = new gmxapi::MDHolder(spec);
                holder->name_ = "pygmx holder";
                auto deleter = [](PyObject *o) {
                    if (PyCapsule_IsValid(o, gmxapi::MDHolder_Name))
                    {
                        auto holder_ptr = (gmxapi::MDHolder *) PyCapsule_GetPointer(o, gmxapi::MDHolder_Name);
                        delete holder_ptr;
                        // \todo double-check whether there is something we should do to invalidate a PyCapsule.
                    };
                };
                auto capsule = py::capsule(holder,
                                           gmxapi::MDHolder_Name,
                                           deleter);
                py::object bind = force_object.attr("bind");
                // py::capsule does not have bindings and does not implicitly convert to py::object
                py::object obj = capsule;
                bind(obj);
                std::cout << "Work specification now has " << spec->getModules().size() << " modules." << std::endl;
            }
            else
            {
                // Todo: Need to bind the exceptions...
                throw PyExc_RuntimeError;
            }
        },
        "Set a restraint potential for the system.");

    // Export session class
    // \todo relocate
    // We can't completely surrender ownership to Python because other API objects may refer to it.
    py::class_<::gmxapi::Session, std::shared_ptr<::gmxapi::Session>> session(m, "MDSession");
    session.def("run", &::gmxapi::Session::run, "Run the simulation workflow");
    session.def("close", &::gmxapi::Session::close, "Shut down the execution environment and close the session.");

    // Module-level function
    m.def("from_tpr", &gmxpy::from_tpr, "Return a system container initialized from the given input record.");
}

} // end namespace gmxpy::detail

} // end namespace gmxpy
