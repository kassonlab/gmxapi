/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2017, by the GROMACS development team, led by
 * Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
 * and including many others, as listed in the AUTHORS file in the
 * top-level source directory and at http://www.gromacs.org.
 *
 * GROMACS is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation; either version 2.1
 * of the License, or (at your option) any later version.
 *
 * GROMACS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with GROMACS; if not, see
 * http://www.gnu.org/licenses, or write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 * If you want to redistribute modifications to GROMACS, please
 * consider that scientific software is very special. Version
 * control is crucial - bugs must be traceable. We will be happy to
 * consider code for inclusion in the official distribution, but
 * derived work must not be called official GROMACS. Details are found
 * in the README & COPYING files - if they are missing, get the
 * official version at http://www.gromacs.org.
 *
 * To help us fund GROMACS development, we humbly ask that you cite
 * the research papers on the package. Check out http://www.gromacs.org.
 */
/*! \internal \file
 * \brief Exports Python bindings for gmx.core module.
 *
 * \ingroup module_python
 */

#include <memory>
#include "core.h"

#include "bindings.h"
#include "pymd.h"
#include "pyrunner.h"

namespace py = pybind11;
using namespace gmxpy;

// Export Python module.

/// Set module.__name__
const char* const name = "core";

/// used to set __doc__
/// pybind11 uses const char* objects for docstrings. C++ raw literals can be used.
const char* const docstring = R"delimeter(
Gromacs core module
===================

gmx.core provides Python access to the Gromacs C++ API so that client code can be
implemented in Python, C++, or a mixture. The classes provided are mirrored on the
C++ side in the gmxapi namespace.

This documentation is generated from docstrings exported by C++ extension code.

)delimeter";

/*! \brief Export gmx.core Python module in shared object file.
 *
 * One goal of these bindings is to declare a buffer type suitable for numpy Nx3 array output.
 * If we want to pass access but not ownership to Python, we need to make
 * sure we can allow a C++ shared pointer ref count to be increased.
 * The buffer protocol requires that the exporter (this code) keeps the
 * memory valid for the exported view until all consumers are done and
 * the PyBuffer_Release(buffer *view) is issued. I'm not sure, but I assume
 * pybind11 manages that for us by holding a shared_ptr to this. However, there
 * seem to be subtleties I overlooked in some testing, so this warrants
 * further investigation.
 *
 * To be safe (and in general) we can use the keep_alive<>() call policy
 * and return_value_policy annotations.
 * The keep_alive<Nurse, Patient>() call policy keeps Patient alive as long
 * as Nurse is alive. Indices for Nurse or Patient are 0 for the return value
 * of the annotated function
 * and higher numbers for arguments. For member functions, index 1 is used
 * for the this* object.
 *
 * The pybind11 documentation notes "For functions returning smart pointers, it is not necessary to specify a return value policy."
 * and
 * "It is even possible to completely avoid copy operations with Python expressions like np.array(matrix_instance, copy = False)"
 * \ingroup module_python
 */


// Export Python module.
void export_module_md(py::module &m)
{
    py::class_< PyMD, PyGmxModule, std::shared_ptr<PyMD> > md(m, "MD");
    md.def(py::init());
    md.def("__str__", [](PyMD* proxy){ return proxy->info(); }, "Get some human-readable runtime information.");
//    m.def("info", [](PyMD* md){ return md->info();}, "Get some human-readable runtime information.");

    m.def("md_from_tpr", &PyMD::md_from_tpr, "Return an MD module to run the given input record.");
}

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

//void export_context(py::module &m)
//{
//    py::class_< PyContext, shared_ptr<PyContext> > context(m, "Context");
//    context.def_property("runner", &PyContext::get_runner, &PyContext::set_runner);
//
//    py::class_< PySimpleContext, PyContext, shared_ptr<PySimpleContext> > simplecontext(m, "SimpleContext");
//    simplecontext.def(py::init())
//        .def("initialize", &PySimpleContext::initialize, "Initialize context and return a session.");
//
//    py::class_< PyContextManager > cm(m, "ContextManager");
//    cm.def("__enter__", &PyContextManager::enter)
//        .def("__exit__", &PyContextManager::exit);
//}

//void export_session(py::module &m)
//{
//    py::class_ < PySession, shared_ptr<PySession> > session(m, "Session");
//    session.def("run", &PySession::run, "Run the configured task(s)");
//}

const char* plugindocs = R"delimiter(
Provide external code for use in MD integration.

Example:
    >>> from mymdconfig import md
    >>> context = gmx.ParallelEnsemble(replicate=10)
    >>> plugin = MyPlugin()
    >>> plugin.set_params(...)
    >>> md.add_potential(plugin.potential)
    >>> with context(md) as session:
    ...   session.run()
    >>> assert(os.path.exists('traj.tng'))
    >>> histogram = plugin.histogram

Above, the user has specified their MD task in a separate `mymdconfig.py` using
the same syntax shown elsewhere in this documentation.
By constructing a ParallelEnsemble, gmx is told it will be running the same
task 10 distinct times in a loosely-coupled parallelism.

The MyPlugin class has been written to use the API to discover its coworkers.
In addition to higher-level functions, MyPlugin provides an MD potential that is
bound in to the MD evaluation. The `md` object is a Gromacs task that is fully
configured and ready to run, so the `context` is able to build an appropriate
runner and launch execution by binding with `context(md)`. Calling `run()` on
the resulting session performs all work that has been specified.

In this case,
the provided `md` object was already configured to produce a trajectory of a specific number of MD
steps. Before the `with` block ends, the user could have added additional work,
such as `session.run(10000)` to extend the trajectory by 10000 steps. As the
`with` block ends, requested data is made available locally by the API. In this
case, the MD task produced a trajectory output file and the MyPlugin class was
written to always provide the final histogram data in a data attribute.

An alternative syntax with the same result follows. Setting scalar parameters
(`seed`) to array data (10-element random number array) implies 10 distinct
trajectories from replicated initial conditions. Hard-coding the requirement of
a local copy of histogram data in the above plugin could be avoided by requiring
the user to explicitly request the data only if needed.

Example:
    >>> plugin = MyPlugin2()
    >>> plugin.set_params(...)
    >>> md.seed(np.random((10,)))
    >>> md.add_potential(plugin.potential)
    >>> with context:
    ...   histogram = plugin.histogram.extract()

Even more coding could be avoided in the plugin by relying on the API to manage
data shared by the members of the simulation ensemble. The runner syntax below
can be considered as an alternative implementation or as explicit expression of
implicit behavior in the previous examples. In each case, the script only
specifies once that the ensemble consists of ten simulations. Members of the
workflow that need this information and have not received it explicitly from the
user can discover it through the API as the work is launched.

Without additional parameters, the MD object has sensible default behavior.
Replicates will produce separate trajectories initialized from distinct random
number seeds, here generated implicitly.

MyPlugin3 has been written to perform ensemble analysis and provide a Boolean
evaluation of some estimate of convergence. It provides an `update` method to
add a number of steps to the requirements on its input trajectory and allows the
user to update the parameters of the potential it provides between calls to
`converged()`. As conceived, this syntax implies that the data requirements are
only resolved when needed (by the call to `converged`), but this is potentially
confusing since it is probably counter-intuitive that the order of operations
in the `while` loop does not matter. Two ways to avoid this ambiguity would be
(a) to make the 1000 additional steps a requirement of the `do_something` function,
or (b) to explicitly specify timesteps on which introspective API operations are
to be performed. I favor the latter, but it requires settling on conventions to
indicate which methods provided by plugin code are API operations with the power
to trigger computation to resolve dependencies. Here, I am proposing that
`MyPlugin3.update()` is such a method and is inherited from a base class (or
mix-in class) of gmx.core.ApiObject (or something).

Example:
    >>> plugin = MyPlugin3()
    >>> plugin.potential.set_params(json.load(params)))
    >>> md.add_potential(plugin.potential)
    >>> runner = gmx.EnsembleRunner(md.replicate(10))
    >>> with context:
    ...   plugin.shared_data = gmx.SharedArray((N,M))
    ...   while not plugin.converged():
    ...     plugin.update(nsteps=1000)
    ...     plugin.potential.set_params(do_something(plugin.shared_data))
    ...   histogram = plugin.histogram.extract()
    ...   runner.run(10000)
)delimiter";

// Instantiate the module
PYBIND11_MODULE(core, m) {
    m.doc() = docstring;

    // Export core bindings
    py::class_< PyGmxModule, std::shared_ptr<PyGmxModule> > gmx_module(m, "Module", "Base class for computation modules.");
    py::class_< PyStatus > gmx_status(m, "Status", "Holds status for API operations.");
    py::class_< PyMDModule > plugin(m, "MDModule", plugindocs);

    // Get bindings exported by the various components.
    export_module_md(m);
    export_runner(m);
//    export_context(m);
//    export_session(m);
    //export_options()
    //export_datatypes(m);
    //export_trajectory(m);
}
