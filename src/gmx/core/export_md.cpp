/*! \file
 * \brief Bindings for external GROMACS MD modules.
 *
 * \ingroup module_python
 * \author M. Eric Irrgang <ericirrgang@gmail.com>
 */
#include "core.h"

#include <iostream>

#include "gmxapi/exceptions.h"
#include "gmxapi/gmxapi.h"
#include "gmxapi/md.h"
#include "gmxapi/md/mdmodule.h"

namespace gmxpy
{

namespace detail
{

namespace py = pybind11;

class TestModule : public gmxapi::MDModule {};

// Export Python module.
void export_md(py::module &m)
{
    // Since this binding is for an external class (libgmxapi, not gmxpy or core.so or whatever)
    // we need to either prevent the binding from being global (the default) or require
    // that any other Python extension that wants to use gmxapi::MDModule would have to
    // inherit from this Python module. For much greater flexibility, we will allow other
    // Python extension modules to interact with ours by having their own local bindings
    // for gmxapi classes and to just implement functions that take gmxapi objects as
    // arguments. To avoid messing with Python references and such, gmxapi classes used
    // in this way should be copy-safe, such as a container with a shared_ptr member.
    py::class_< ::gmxapi::MDModule, std::shared_ptr<::gmxapi::MDModule> >
    gmxapi_mdmodule(m, "MDModule", py::module_local());
    // In fact the only purpose to exporting the base class here is so that it can be
    // used in function arguments for other more complete bindings. We do not need to
    // actually be able to instantiate it, but we do so for testing until we have
    // actually useful modules in the core package.
    py::class_< TestModule, std::shared_ptr<TestModule> >(m,
                                                          "TestModule",
                                                          gmxapi_mdmodule)
            .def(py::init<>(), "Test module...");

    // Consider whether to bother exporting base class and whether/how to overload methods for testing.
    gmxapi_mdmodule.def(
        "bind",
        [](std::shared_ptr<TestModule> self, py::object object){
            if (PyCapsule_IsValid(object.ptr(), gmxapi::MDHolder::api_name))
            {
                auto holder = (gmxapi::MDHolder*) PyCapsule_GetPointer(
                    object.ptr(),
                    gmxapi::MDHolder::api_name);
                auto spec = holder->getSpec();
                std::cout << self->name() << " received " << holder->name();
                std::cout << " containing spec of size ";
                std::cout << spec->getModules().size();
                std::cout << std::endl;
                spec->addModule(self);
            }
            else
            {
                throw gmxapi::ProtocolError("MDModule bind method requires properly named PyCapsule input.");
            }
        }
    );


}

} // end namespace gmxpy::detail

} // end namespace gmxpy
