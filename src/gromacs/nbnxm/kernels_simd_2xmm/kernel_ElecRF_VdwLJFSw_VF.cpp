/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright 2012- The GROMACS Authors
 * and the project initiators Erik Lindahl, Berk Hess and David van der Spoel.
 * Consult the AUTHORS/COPYING files and https://www.gromacs.org for details.
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
 * https://www.gnu.org/licenses, or write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA.
 *
 * If you want to redistribute modifications to GROMACS, please
 * consider that scientific software is very special. Version
 * control is crucial - bugs must be traceable. We will be happy to
 * consider code for inclusion in the official distribution, but
 * derived work must not be called official GROMACS. Details are found
 * in the README & COPYING files - if they are missing, get the
 * official version at https://www.gromacs.org.
 *
 * To help us fund GROMACS development, we humbly ask that you cite
 * the research papers on the package. Check out https://www.gromacs.org.
 */
/*
 * Note: this file was generated by the Verlet kernel generator for
 * kernel type 2xmm.
 */

/* Some target architectures compile kernels for only some NBNxN
 * kernel flavours, but the code is generated before the target
 * architecture is known. So compilation is conditional upon
 * GMX_NBNXN_SIMD_2XNN, so that this file reduces to a stub
 * function definition when the kernel will never be called.
 */
#include "gmxpre.h"

#include "gromacs/mdtypes/interaction_const.h"
#include "gromacs/nbnxm/nbnxm_simd.h"

#define GMX_SIMD_J_UNROLL_SIZE 2
#include "kernels.h"

#define CALC_COUL_RF
#define LJ_FORCE_SWITCH
/* Use full LJ combination matrix */
#define CALC_ENERGIES

#ifdef GMX_NBNXN_SIMD_2XNN
#    include "kernel_common.h"
#endif /* GMX_NBNXN_SIMD_2XNN */

#ifdef CALC_ENERGIES
void nbnxm_kernel_ElecRF_VdwLJFSw_VF_2xmm(const NbnxnPairlistCpu gmx_unused* nbl,
                                          const nbnxn_atomdata_t gmx_unused* nbat,
                                          const interaction_const_t gmx_unused* ic,
                                          const rvec gmx_unused*  shift_vec,
                                          nbnxn_atomdata_output_t gmx_unused* out)
#else  /* CALC_ENERGIES */
void nbnxm_kernel_ElecRF_VdwLJFSw_VF_2xmm(const NbnxnPairlistCpu gmx_unused* nbl,
                                          const nbnxn_atomdata_t gmx_unused* nbat,
                                          const interaction_const_t gmx_unused* ic,
                                          const rvec gmx_unused*  shift_vec,
                                          nbnxn_atomdata_output_t gmx_unused* out)
#endif /* CALC_ENERGIES */
#ifdef GMX_NBNXN_SIMD_2XNN
#    include "kernel_outer.h"
#else  /* GMX_NBNXN_SIMD_2XNN */
{
    /* No need to call gmx_incons() here, because the only function
     * that calls this one is also compiled conditionally. When
     * GMX_NBNXN_SIMD_2XNN is not defined, it will call no kernel functions and
     * instead call gmx_incons().
     */
}
#endif /* GMX_NBNXN_SIMD_2XNN */
