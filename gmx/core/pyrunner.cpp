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


#include "pyrunner.h"

#include <memory>
#include <iostream>
#include <cassert>

#include "gmxapi/md.h"
#include "gmxapi/md/mdmodule.h"
#include "gmxapi/gmxapi.h"
#include "gmxapi/runner.h"
#include "gmxapi/context.h"

#include "pymd.h"

#include <pybind11/pybind11.h>
#include <pybind11/pytypes.h>

namespace gmxpy
{


PySingleNodeRunner::PySingleNodeRunner(std::shared_ptr<PyMD> m)
    : module_ {std::move(m)},
      state_{std::make_shared<PySingleNodeRunner::State>()},
      spec_{std::make_shared<gmxapi::MDWorkSpec>()}
{
};

PySingleNodeRunner::PySingleNodeRunner(std::shared_ptr<gmxapi::IMDRunner> runner)
{
    module_ = std::make_shared<PyMD>();
    state_ = std::make_shared<PySingleNodeRunner::State>(std::move(runner));
    spec_ = std::make_shared<gmxapi::MDWorkSpec>();
}

// Convert an inactive runner to an active runner. In this simple implementation, a handle
// to the same object is returned, but different implementation classes may be used to
// manage state.
std::shared_ptr<PySingleNodeRunner> PySingleNodeRunner::startup()
{
    std::shared_ptr<PySingleNodeRunner> product{nullptr};
    auto state = std::make_shared<PySingleNodeRunner::State>(this->state_->runner_);

    if (state == nullptr)
    {
        state = std::make_shared<PySingleNodeRunner::State>(module_->get());
    }

    assert(state != nullptr);
    if (state != nullptr)
    {
        state->runner_ = state->runner_->initialize(gmxapi::defaultContext());
        if (state->runner_ != nullptr)
        {
            product = std::make_shared<PySingleNodeRunner>(module_);
            product->state_ = state;
            product->spec_ = spec_;
        }
    }

    return product;
}

PyStatus PySingleNodeRunner::run()
{
    assert(state_ != nullptr);
    PyStatus status{};
    if (state_->runner_ != nullptr)
    {
        auto runner = state_->runner_;
        std::cout << "Starting runner with " << spec_->getModules().size() << " mdmodules" << std::endl;
        for (auto&& module : spec_->getModules())
        {
            runner->setRestraint(module);
        }
        auto runstatus = runner->run();
        status = PyStatus(runstatus);
    }
    else
    {
        status = PyStatus(false);
    }
    return PyStatus(status);
}

PyStatus PySingleNodeRunner::run(long int nsteps)
{
    PyStatus status{};
    if (state_->runner_ != nullptr)
    {
//        auto runstatus = state_->runner_->run(nsteps);
//        status = PyStatus(runstatus);
        throw gmxapi::NotImplementedError("...need to add back this behavior...");
    }
    else
    {
        status = PyStatus(false);
    }
    return PyStatus(status);
}

void PySingleNodeRunner::addForce(pybind11::object force_object)
{
    namespace py=pybind11;
    // If force_object has a bind method, give it a PyCapsule with a pointer
    // to our C++ object.
    if (py::hasattr(force_object, "bind"))
    {
//        // Wrap the work specification in an API object.
//        auto holder = std::make_shared<gmxapi::MDHolder>(spec_);
//        holder->name_ = "pygmx holder";
//        // Get a reference to a Python object with the bindings defined in this module.

        auto holder = new gmxapi::MDHolder(spec_);
        holder->name_ = "pygmx holder";
        auto deleter = [](PyObject* o){
            if (PyCapsule_IsValid(o, gmxapi::MDHolder_Name))
            {
                auto holder_ptr = (gmxapi::MDHolder*) PyCapsule_GetPointer(o, gmxapi::MDHolder_Name);
                delete holder_ptr;
            };
        };
        auto capsule = py::capsule(holder, gmxapi::MDHolder_Name, deleter);

        // Generate a capsule object that extends the lifetime of the holder, which extends the lifetime of the spec_ managed object, and pass it through the bind interface.


        py::object bind = force_object.attr("bind");
        // py::capsule does not have bindings and does not implicitly convert to py::object
        py::object obj = capsule;
        bind(obj);
        std::cout << "Work specification now has " << spec_->getModules().size() << " modules." << std::endl;
    }
    else
    {
        // Need to bind the exceptions...
        throw PyExc_RuntimeError;
    }
}

PySingleNodeRunner::~PySingleNodeRunner() = default;

//bool PySingleNodeRunner::bind_context(std::shared_ptr< PyContext > context)
//{
//    context_ = context;
//    return true;
//}

} // end namespace gmxpy
