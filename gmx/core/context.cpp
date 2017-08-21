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

#include "context.h"

#include <memory>

#include "bindings.h"
#include "core.h"

namespace py = pybind11;

namespace gmxpy
{

using std::shared_ptr;
using std::unique_ptr;
using std::make_shared;

PyContextManager::PyContextManager(const PyContext &context)
{
    session_ = make_shared<PySession>(context.get_runner());
}

shared_ptr<PySession> PyContextManager::enter()
{
    //session_->open();
    return session_;
}

bool PyContextManager::exit(py::object, py::object, py::object)
{
    //session_->close();
    return true;
}

shared_ptr<PyRunner> PyContext::get_runner() const
{
    return this->runner_;
}

void PyContext::set_runner(shared_ptr<PyRunner> runner)
{
    if (runner->bind_context(this->ptr()))
    {
        runner_ = runner;
    }
}

shared_ptr<PyContext> PyContext::ptr()
{
    return shared_from_this();
}

PySimpleContext::PySimpleContext() :
    PyContext(),
    is_initialized_(false)
{

}

std::shared_ptr<PyContextManager> PySimpleContext::initialize()
{
    if (is_initialized_)
    {
        // SimpleContext can only be run once.
        return nullptr;
    }
    ;

    // Tell the API we are setting up a context.
    std::shared_ptr<PyContextManager> ptr;
    ptr = make_shared<PyContextManager>(*this);
    return ptr;
}

};     // end namespace gmxpy
