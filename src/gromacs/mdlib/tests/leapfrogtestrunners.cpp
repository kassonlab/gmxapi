/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2019,2020, by the GROMACS development team, led by
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
 * \brief Runner for CPU-based implementation of the integrator.
 *
 * \author Artem Zhmurov <zhmurov@gmail.com>
 * \ingroup module_mdlib
 */
#include "gmxpre.h"

#include "leapfrogtestrunners.h"

#include "gromacs/math/vectypes.h"
#include "gromacs/mdlib/gmx_omp_nthreads.h"
#include "gromacs/mdlib/update.h"
#include "gromacs/utility/arrayref.h"

#include "testutils/testasserts.h"

#include "leapfrogtestdata.h"


namespace gmx
{
namespace test
{

void LeapFrogHostTestRunner::integrate(LeapFrogTestData* testData, int numSteps)
{
    testData->state_.x.resizeWithPadding(testData->numAtoms_);
    testData->state_.v.resizeWithPadding(testData->numAtoms_);
    for (int i = 0; i < testData->numAtoms_; i++)
    {
        testData->state_.x[i] = testData->x_[i];
        testData->state_.v[i] = testData->v_[i];
    }

    gmx_omp_nthreads_set(emntUpdate, 1);

    for (int step = 0; step < numSteps; step++)
    {
        testData->update_->update_coords(
                testData->inputRecord_, step, &testData->mdAtoms_, &testData->state_, testData->f_,
                testData->forceCalculationData_, &testData->kineticEnergyData_,
                testData->velocityScalingMatrix_, etrtNONE, nullptr, false);
        testData->update_->finish_update(testData->inputRecord_, &testData->mdAtoms_,
                                         &testData->state_, nullptr, false);
    }
    const auto xp = makeArrayRef(*testData->update_->xp()).subArray(0, testData->numAtoms_);
    for (int i = 0; i < testData->numAtoms_; i++)
    {
        for (int d = 0; d < DIM; d++)
        {
            testData->x_[i][d]      = testData->state_.x[i][d];
            testData->v_[i][d]      = testData->state_.v[i][d];
            testData->xPrime_[i][d] = xp[i][d];
        }
    }
}

} // namespace test
} // namespace gmx
