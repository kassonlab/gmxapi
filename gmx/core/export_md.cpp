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
    py::class_< PyMD, PyGmxModule, std::shared_ptr<PyMD> > md(m, "MD");
    md.def(py::init());
    md.def("__str__", [](PyMD* proxy){ return proxy->info(); }, "Get some human-readable runtime information.");
//    m.def("info", [](PyMD* md){ return md->info();}, "Get some human-readable runtime information.");

    m.def("md_from_tpr", &PyMD::md_from_tpr, "Return an MD module to run the given input record.");

    py::class_< PyMDModule > plugin(m, "MDModule", plugindocs);

}

} // end namespace gmxpy::detail

} // end namespace gmxpy