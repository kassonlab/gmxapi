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

#include "pymd.h"

#include <memory>
#include <string>

#include "core.h"

#include "gmxapi/md.h"

namespace gmxpy
{

PyMD::PyMD(std::shared_ptr<gmxapi::MDProxy> md) :
    mdProxy_{std::move(md)}
{};

PyMD::PyMD() :
    PyMD{std::make_shared<gmxapi::MDProxy>()}
{};

PyMD::~PyMD() = default;

//PyStatus PyMD::eval()
//{
//    return PyStatus();
//};

std::shared_ptr<PyMD> PyMD::md_from_tpr(const std::string filename)
{
    auto md = std::make_shared<PyMD>();

    // Call the API to process the TPR file and wrap the resulting objects.
    md->mdProxy_ = gmxapi::mdFromTpr(filename);

    return md;
}

std::string PyMD::info()
{
    if (mdProxy_ != nullptr)
    {
        return mdProxy_->info();
    }
    else
    {
        return "uninitialized";
    }
}

std::shared_ptr<gmxapi::MDProxy> PyMD::get()
{
    return mdProxy_;
}

void PyMD::addPotential(std::shared_ptr<::gmxapi::MDModule> module)
{
    (void)module;
}

} // end namespace gmxpy
