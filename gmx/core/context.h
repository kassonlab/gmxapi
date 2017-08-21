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
 * \brief Declares Python contexts
 *
 * \ingroup module_python
 */
#ifndef PYGMX_CONTEXT_H
#define PYGMX_CONTEXT_H

#include <memory>

#include "bindings.h"
#include "core.h"
#include "runner.h"
#include "session.h"

namespace py = pybind11;

namespace gmxpy
{

class PyContext;
/*! \brief Implement Python context manager protocol.
 *
 * Python guarantees that when used in a `with` clause, if the `__enter__`
 * method succeeds, the `__exit__` method will be called after executing the
 * intervening code block and releasing references to whatever was returned
 * by `__enter__`, even if there are exceptions. Note that exceptions thrown
 * by `__enter__` ought to be distinguishable from any thrown by the intervening
 * code block.
 */
class PyContextManager
{
    public:
        PyContextManager() = default;

        // Ownership of a context manager is exclusive.
        // It is not yet clear what is involved in transfering ownership, so no
        // move constructor or assignment is yet allowed.
        PyContextManager(const PyContextManager &)            = delete;
        PyContextManager &operator=(const PyContextManager &) = delete;

        // Create a new manager for a context
        explicit PyContextManager(const PyContext &context);

        std::shared_ptr<PySession> enter();

        // Return true to suppress exception being
        // raised in calling code.
        bool exit(py::object, py::object, py::object);

    private:
        std::shared_ptr<PySession> session_;
};


/*! \brief Handle to a Context API object.
 *
 * Can be used to define work and configure the execution environment.
 * Execution is launched by a ContextManager, which provides a Session handle
 * with additional API features available during the lifetime of the execution
 * environment.
 */
class PyContext : public std::enable_shared_from_this<PyContext>
{
    public:
        PyContext() = default;
        PyContext(const PyContext &context)     = default;
        PyContext &operator=(const PyContext &) = default;

        virtual ~PyContext() = default;

        virtual std::shared_ptr<PyRunner> get_runner() const;

        // Context will keep the runner alive.
        virtual void set_runner(std::shared_ptr<PyRunner> runner);

        //ToDo: context should probably assure only one manager at a time.

        std::shared_ptr<PyContext> ptr();

    protected:
        std::shared_ptr<PyRunner> runner_;
};

/*! \brief Minimal Context implementation.
 *
 * Provides `initialize()`, which takes no arguments and returns a context manager
 * for a local session.
 *
 * Methods:
 *     initialize() invokes a context manager for a locally-executing session.
 */
class PySimpleContext : public PyContext
{
    public:
        PySimpleContext();
        PySimpleContext(const PySimpleContext &context) = delete;

        PySimpleContext &operator=(const PySimpleContext &) = delete;

        ~PySimpleContext() = default;

        /// Initialize the context and return a manager.
        std::shared_ptr<PyContextManager> initialize();

    private:
        bool is_initialized_;
};

};     // end namespace gmxpy
#endif // header guard
/// \endcond
