#include <gmxapi/gmxapi.h>
#include <iostream>
#include "core.h"
#include "pymd.h"


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

    // We don't have a reason to create objects of this type directly in Python.
    //gmxapi_mdmodule.def(py::init(), "");
    py::class_< TestModule, std::shared_ptr<TestModule> >(m, "TestModule", gmxapi_mdmodule).def(py::init<>(), "Test module...");

    // Consider whether to bother exporting base class and whether/how to overload methods for testing.
    gmxapi_mdmodule.def("bind",
                         [](py::object self, py::object object){

//                             if (capsule.name() == std::string(gmxapi::MDHolder::api_name))
                             if (PyCapsule_IsValid(object.ptr(), gmxapi::MDHolder::api_name))
                             {
                                 auto this_ = py::cast<gmxapi::MDModule*>(self);
                                 gmxapi::MDHolder* holder = (gmxapi::MDHolder*) PyCapsule_GetPointer(object.ptr(), gmxapi::MDHolder::api_name);;
                                 auto spec = holder->getSpec();
                                 std::cout << this_->name() << " received " << holder->name();
                                 std::cout << " containing spec of size ";
                                 std::cout << spec->getModules().size();
                                 std::cout << std::endl;
                             }
                             else
                             {
                                 throw gmxapi::ProtocolError("MDModule bind method requires properly named PyCapsule input.");
                             }
                         }
    );


    // The runner interface will be simplified and the add_force moved here.
//    py::class_<::gmxpy::MD> coremd(m, "MD");
//    coremd.def(py::init(), "");
//    coremd.def("add_force", &gmxpy::MD::addForce, "Attach a restraint or other potential.");

//    py::class_< PyGmxModule, std::shared_ptr<PyGmxModule> > gmxapi_module(m, "Module", "Base class for computation modules.");
//    gmxapi_module.def(py::init<>());

//    m.def("printName", [](MDModule* module){ return module->name(); }, "Print module name");
//    m.def("printName", [](PyGmxModule* module){ return module->info(); }, "Print module name");

//    py::class_< PyMDModule > plugin(m, "MDModule", plugindocs);
//    plugin.def(py::init());
//    plugin.def_readwrite("_api_object", &PyMDModule::module);

    py::class_< PyMD, std::shared_ptr<PyMD> > md(m, "MD");
    md.def(py::init(), "");
    md.def("__str__", [](PyMD* proxy){ return proxy->info(); }, "Get some human-readable runtime information.");
//    m.def("info", [](PyMD* md){ return md->info();}, "Get some human-readable runtime information.");
    md.def("add_potential", &PyMD::addPotential, "Add a restraint potential.");

    m.def("md_from_tpr", &PyMD::md_from_tpr, "Return an MD module to run the given input record.");


}

} // end namespace gmxpy::detail

} // end namespace gmxpy
