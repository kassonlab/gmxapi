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

#ifndef GMXPY_MD_H
#define GMXPY_MD_H

#include <memory>
#include <string>

#include "core.h"
#include "gmxapi/md.h"

namespace gmxpy
{

class PyMDModule; // forward declaration

/*!
 * \brief Wrapper for C++ MD interface.
 */
class PyMD : public PyGmxModule
{
    public:
        PyMD();
        ~PyMD() final; // Need to define later, after pImpl types are complete
        PyMD(PyMD&&) = default;
        PyMD& operator=(PyMD&&) = default;

        // Copy semantics are unknown at this point.
        PyMD(const PyMD&) = delete;
        PyMD& operator=(const PyMD&) = delete;

        // Construct from a gmxapi::MDProxy reference to wrap
        explicit PyMD(std::shared_ptr<gmxapi::MDProxy> md);

        void addPotential(PyMDModule module);

        std::string info() override;

        /*!
         * \brief Get a reference to the underlying gmxapi object.
         */
        std::shared_ptr<gmxapi::MDProxy> get();

        /*!
         * \brief Create a new MD proxy.
         * \param filename TPR file from which to initialize MD input.
         * \return New MD proxy object.
         */
        static std::shared_ptr<PyMD> md_from_tpr(const std::string filename);

        /*!
         * \brief Invoke the API to evaluate pending computation or data flow.
         * \return status object.
         */
        //PyStatus eval();
    private:
        // Other objects may be able to extend the lifetime of the md API object?
        std::shared_ptr<gmxapi::MDProxy> mdProxy_;
};

// Todo: I should double-check that static const C strings get optimized out when not used or move this.
static const char* plugindocs = R"delimiter(
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
 * \brief Wrapper for pluggable MD modules.
 */
class PyMDModule
{
public:
    std::shared_ptr<gmxapi::MDModule> module;
};

}      // end namespace gmxpy
#endif // header guard
