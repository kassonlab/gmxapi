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
/// \cond internal
/*! \internal \file
 * \brief Declares Python runner
 *
 * \ingroup module_python
 */
#ifndef PYGMX_RUNNER_H
#define PYGMX_RUNNER_H

#include <memory>

#include "core.h"
#include "gmxapi/runner.h"
namespace gmxpy
{

class PyContext;
class PyMD;

//class PyRunner
//{
//    public:
//        PyRunner() = default;
//        PyRunner(const PyRunner&) = delete;
//        PyRunner& operator=(const PyRunner&) = delete;
//
//        virtual ~PyRunner() = default;
//
//        /// Conceptually, a Session can be run and a PyRunner just helps build one, but complexity comes later.
//        virtual PyStatus run() = 0;
//
//        // Runner can be bound to zero or one contexts, but will not extend the lifetime
//        // of the context. Not all runners are compatible with all contexts.
////        virtual bool bind_context(std::shared_ptr<PyContext> context) = 0;
//
//};

class PySingleNodeRunner : public std::enable_shared_from_this<PySingleNodeRunner>
{
    public:
        /// Implementation class
        class State;

        PySingleNodeRunner() = delete;
        PySingleNodeRunner(const PySingleNodeRunner &smr) = delete;
        PySingleNodeRunner&operator=(const PySingleNodeRunner&) = delete;
        PySingleNodeRunner(PySingleNodeRunner&&) = default;
        PySingleNodeRunner&operator=(PySingleNodeRunner&&) = default;

        /// Can only be created by binding to a task.
        explicit PySingleNodeRunner(std::shared_ptr<PyMD> m);
        /// ... or from to wrap an API object
        explicit PySingleNodeRunner(std::shared_ptr<gmxapi::IMDRunner> runner);

        ~PySingleNodeRunner();

        /// Call the configured runner if possible.
        PyStatus run();
        PyStatus run(long int nsteps);

        std::shared_ptr<gmxapi::IMDRunner> get_apiObject();

        /// Initialize a gmx::Mdrunner object for the attached module.
        /// \returns handle to runner if successful or else a nullptr
        std::shared_ptr<PySingleNodeRunner> startup();
//        PyStatus startup();

//        virtual bool bind_context(std::shared_ptr<PyContext> context);

    private:
        /// Gromacs module to run
        std::shared_ptr<PyMD>  module_;
        /// Ability to get a handle to an associated context manager.
        std::weak_ptr<PyContext> context_;
        /// Implementation object
        std::shared_ptr<State> state_;
};

class PySingleNodeRunner::State
{
    public:
        /// Object should be initialized with the startup() method of the owning object.
        State() :
            runner_{std::make_shared<gmxapi::RunnerProxy>()}
        {};
        explicit State(std::shared_ptr<gmxapi::MDProxy> md) :
            runner_{std::make_shared<gmxapi::RunnerProxy>(std::move(md))}
        {};

        explicit State(std::shared_ptr<gmxapi::IMDRunner> runner) :
            runner_(std::move(runner))
        {};

        std::shared_ptr<gmxapi::IMDRunner> runner_;
};



};     // end namespace gmxpy
#endif // header guard
/// \endcond
