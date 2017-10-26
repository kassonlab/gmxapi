#include "bindings.h"
#include "pyrunner.h"
#include "pymd.h"

namespace gmxpy
{

namespace detail
{

namespace py = pybind11;


void export_runner(py::module &m)
{
    // Export runner classes
    py::class_< PySingleNodeRunner, std::shared_ptr<PySingleNodeRunner> > simple_runner(m, "SimpleRunner");
    simple_runner.def(py::init<std::shared_ptr<PyMD>> ());
    simple_runner.def("start", &PySingleNodeRunner::startup, "Initialize runner." );
    simple_runner.def("run", (PyStatus (PySingleNodeRunner::*)()) &PySingleNodeRunner::run, "Invoke runner for configured number of steps.");
    simple_runner.def("run", (PyStatus (PySingleNodeRunner::*)(long int)) &PySingleNodeRunner::run, "Invoke runner for configured number of steps.");

//    //
//    // py::class_< PyRunner > tafrunner(m, "TafRunner");
//    // // We shouldn't need a keep_alive<>() for the module we're attaching since
//    // // pybind knows how to handle shared_ptr and this object does not need to
//    // // survive after the associated module is done with it, but we need to
//    // // reconsider when the usage model changes for chained or more general modules.
//    // tafrunner.def(py::init< shared_ptr<gmx::TrajectoryAnalysisModule> >())
//    //     .def("initialize", &PyRunner::initialize, "handle options")
//    //     .def("next", &PyRunner::next, "Advance the current frame one step.");
//
}


} // end namespace gmxpy::detail

} // end namespace gmxpy