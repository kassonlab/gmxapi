//
// Created by Eric Irrgang on 11/7/17.
//

#ifndef GMXPY_PYMDMODULE_H
#define GMXPY_PYMDMODULE_H

#include "pybind11/pybind11.h"

#include <memory>
#include "gmxapi/md.h"
#include "gmxapi/md/mdmodule.h"

namespace gmxpy
{

// Todo: I should double-check that static const C strings get optimized out when not used or move this.
static const char *plugindocs = R"delimiter(
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


/*!
 * \brief Thin wrapper for gmxapi objects.
 *
 * To avoid dependencies on anything Python-related in the C++ API implementation, we wrap types from the external
 * library with definitions that can be compiled according to the constraints of a Python extension, if we need to make
 * objects from the external library available in our Python bindings.
 */
class GmxModule
{
    public:
        virtual ~GmxModule() = default;
        const std::string name{"GmxModule"};
        std::shared_ptr<::gmxapi::MDModule> module;
};



/*! \brief Trampoline class for Gromacs modules exported to Python
 *
 * PyGmxModule objects provide sufficient interface to bind with Runners.
 * Derived classes may provide additional interfaces.
 *
 * \internal
 * \ingroup module_python
 */
class PyGmxModule
{
    public:
        PyGmxModule()                               = default;
        PyGmxModule(const PyGmxModule &)            = default;
        PyGmxModule(PyGmxModule&&) noexcept         = default;
        virtual ~PyGmxModule()                      = default;
        PyGmxModule &operator=(const PyGmxModule &) = default;
        PyGmxModule& operator=(PyGmxModule&&) noexcept      = default;

        /*!
         * \brief Generic string output.
         *
         * Provide a generic way to implement simple self-representation. Optionally implemented
         * to allows for some trivial
         * introspection and/or runtime debugging. May ultimately be used as the hook for __str__()
         * or __repr__().
         * \return some useful information on the type or state of the object in string form.
         */
        virtual std::string info() { return "PyGmxModule"; };
};

} //end namespace gmxpy

#endif //GMXPY_PYMDMODULE_H
