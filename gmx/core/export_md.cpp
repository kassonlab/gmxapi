#include "bindings.h"
#include "pymd.h"


namespace gmxpy
{

namespace detail
{

namespace py = pybind11;

// Export Python module.
void export_md(py::module &m)
{
    py::class_< PyMDModule > plugin(m, "MDModule", plugindocs);
    plugin.def(py::init());
//    plugin.def_readwrite("_api_object", &PyMDModule::module);

    py::class_< PyMD, PyGmxModule, std::shared_ptr<PyMD> > md(m, "MD");
    md.def(py::init());
    md.def("__str__", [](PyMD* proxy){ return proxy->info(); }, "Get some human-readable runtime information.");
//    m.def("info", [](PyMD* md){ return md->info();}, "Get some human-readable runtime information.");
    md.def("add_potential", &PyMD::addPotential, "Add a restraint potential.");

    m.def("md_from_tpr", &PyMD::md_from_tpr, "Return an MD module to run the given input record.");


}

} // end namespace gmxpy::detail

} // end namespace gmxpy