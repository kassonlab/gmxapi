#include "pysystem.h"
#include "pymd.h"
#include "pyrunner.h"


namespace gmxpy
{

namespace detail
{

namespace py = pybind11;


void export_system(py::module &m)
{
    // Export system container class
    py::class_< PySystem, std::shared_ptr<PySystem> > system(m, "MDSystem");
    system.def(py::init(), "");
    system.def_property_readonly("runner", &PySystem::get_runner, "Bound runner");
    system.def_property_readonly("md", &PySystem::get_md, "Bound MD engine");
    m.def("from_tpr", &PySystem::from_tpr, "Return a system container initialized from the given input record.");
}

} // end namespace gmxpy::detail

} // end namespace gmxpy
