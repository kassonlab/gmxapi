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
 * \brief Declares Python session
 *
 * \ingroup module_python
 */
#ifndef PYGMX_SESSION_H
#define PYGMX_SESSION_H


#include <memory>

#include "core.h"

namespace gmxpy
{
using std::shared_ptr;
using std::unique_ptr;
using std::make_shared;

class PyRunner;
/*! Session of a running context.
 *
 * Session objects should be created by a context manager's `__enter__` method
 * so that they can relying on the semantics of the Python context manager protocol.
 *
 * A session is probably just the interface exposed by a Context API object that
 * has been initialized.
 */
class PySession
{
    public:
        PySession() = default;

        // Sessions must not be copied. They must be acquired from the context manager.
        PySession(const PySession &)            = delete;
        PySession &operator=(const PySession &) = delete;

        ~PySession() = default;

        PySession(shared_ptr<PyRunner> runner);

        /// Run the configured task.
        PyStatus run();
    private:
        shared_ptr<PyRunner> runner_;
};

};     // end namespace gmxpy
#endif // header guard
/// \endcond
