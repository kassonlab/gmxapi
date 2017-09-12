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

#include "gmxapi/runner.h"
#include "gmxapi/context.h"

#include "pymd.h"

namespace gmxpy
{


PySingleNodeRunner::PySingleNodeRunner(std::shared_ptr<PyMD> m)
    : module_ {std::move(m)},
      state_{std::make_shared<PySingleNodeRunner::State>()}
{
};

// Convert an inactive runner to an active runner. In this simple implementation, a handle
// to the same object is returned, but different implementation classes may be used to
// manage state.
std::shared_ptr<PySingleNodeRunner> PySingleNodeRunner::startup()
{
    std::shared_ptr<PySingleNodeRunner> product{nullptr};

    auto state = std::make_shared<PySingleNodeRunner::State>(module_->get());
    if (state != nullptr)
    {
        state->runner_ = state->runner_->initialize(gmxapi::defaultContext());
        if (state->runner_ != nullptr)
        {
            product = std::make_shared<PySingleNodeRunner>(module_);
            product->state_ = state;
        }
    }

    return product;
}

//PyStatus PySingleNodeRunner::startup()
//{
//    state_ = std::make_shared<PySingleNodeRunner::State>(module_->get());
//    auto builder = state_->proxy_->builder();
//    state_->runner_ = builder->build();
//    state_->proxy_ = std::make_shared<gmxapi::SingleNodeRunnerProxy>(module_->get());
//    return PyStatus();
//}

PyStatus PySingleNodeRunner::run()
{
    PyStatus status{};
    if (state_->runner_ != nullptr)
    {
        auto runstatus = state_->runner_->run();
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

PySingleNodeRunner::~PySingleNodeRunner() = default;

//bool PySingleNodeRunner::bind_context(std::shared_ptr< PyContext > context)
//{
//    context_ = context;
//    return true;
//}

} // end namespace gmxpy
