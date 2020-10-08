/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2020, by the GROMACS development team, led by
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
 * \brief
 * Test for MD with dispersion correction.
 *
 * \author Paul Bauer <paul.bauer.q@gmail.com>
 * \ingroup module_mdrun_integration_tests
 */
#include "gmxpre.h"

#include "moduletest.h"

namespace gmx
{
namespace test
{

class DispersionCorrectionTestFixture : public MdrunTestFixture
{
protected:
    DispersionCorrectionTestFixture();
    ~DispersionCorrectionTestFixture() override;
};

DispersionCorrectionTestFixture::DispersionCorrectionTestFixture() {}

DispersionCorrectionTestFixture::~DispersionCorrectionTestFixture() {}

//! Test fixture for mdrun with dispersion correction
typedef gmx::test::DispersionCorrectionTestFixture DispersionCorrectionTest;

/* Check whether the dispersion correction function works. */
TEST_F(DispersionCorrectionTest, DispersionCorrectionCanRun)
{
    runner_.useTopGroAndNdxFromDatabase("alanine_vsite_vacuo");
    const std::string mdpContents = R"(
        dt            = 0.002
        nsteps        = 200
        tcoupl        = Berendsen
        tc-grps       = System
        tau-t         = 0.5
        ref-t         = 300
        constraints   = h-bonds
        cutoff-scheme = Verlet
        DispCorr      = AllEnerPres
    )";
    runner_.useStringAsMdpFile(mdpContents);

    EXPECT_EQ(0, runner_.callGrompp());

    ::gmx::test::CommandLine disperCorrCaller;

    // Do an mdrun with ORIRES enabled
    ASSERT_EQ(0, runner_.callMdrun(disperCorrCaller));
}

} // namespace test
} // namespace gmx
