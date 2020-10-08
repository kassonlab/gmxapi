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
/*! \libinternal \file
 *
 * \brief Declarations for GPU implementation of Leap-Frog.
 *
 * \author Artem Zhmurov <zhmurov@gmail.com>
 *
 * \ingroup module_mdlib
 * \inlibraryapi
 */
#ifndef GMX_MDLIB_LEAPFROG_GPU_H
#define GMX_MDLIB_LEAPFROG_GPU_H

#include "config.h"

#if GMX_GPU_CUDA
#    include "gromacs/gpu_utils/devicebuffer.cuh"
#    include "gromacs/gpu_utils/gputraits.cuh"
#endif

#include "gromacs/gpu_utils/hostallocator.h"
#include "gromacs/pbcutil/pbc.h"
#include "gromacs/pbcutil/pbc_aiuc.h"
#include "gromacs/utility/arrayref.h"
#include "gromacs/utility/classhelpers.h"

class DeviceContext;
class DeviceStream;
struct t_grp_tcstat;

namespace gmx
{


/*! \brief Sets the number of different temperature coupling values
 *
 *  This is needed to template the kernel
 *  \todo Unify with similar enum in CPU update module
 */
enum class NumTempScaleValues
{
    None,    //!< No temperature coupling
    Single,  //!< Single T-scaling value (one group)
    Multiple //!< Multiple T-scaling values, need to use T-group indices
};

/*! \brief Different variants of the Parrinello-Rahman velocity scaling
 *
 *  This is needed to template the kernel
 *  \todo Unify with similar enum in CPU update module
 */
enum class VelocityScalingType
{
    None,     //!< Do not apply velocity scaling (not a PR-coupling run or step)
    Diagonal, //!< Apply velocity scaling using a diagonal matrix
    Full      //!< Apply velocity scaling using a full matrix
};

class LeapFrogGpu
{

public:
    /*! \brief Constructor.
     *
     * \param[in] deviceContext  Device context (dummy in CUDA).
     * \param[in] deviceStream   Device stream to use.
     */
    LeapFrogGpu(const DeviceContext& deviceContext, const DeviceStream& deviceStream);
    ~LeapFrogGpu();

    /*! \brief Integrate
     *
     * Integrates the equation of motion using Leap-Frog algorithm.
     * Updates coordinates and velocities on the GPU. The current coordinates are saved for constraints.
     *
     * \param[in,out] d_x                      Coordinates to update
     * \param[out]    d_xp                     Place to save the values of initial coordinates coordinates to.
     * \param[in,out] d_v                      Velocities (will be updated).
     * \param[in]     d_f                      Forces.
     * \param[in]     dt                       Timestep.
     * \param[in]     doTemperatureScaling     If velocities should be scaled for temperature coupling.
     * \param[in]     tcstat                   Temperature coupling data.
     * \param[in]     doParrinelloRahman       If current step is a Parrinello-Rahman pressure coupling step.
     * \param[in]     dtPressureCouple         Period between pressure coupling steps
     * \param[in]     prVelocityScalingMatrix  Parrinello-Rahman velocity scaling matrix
     */
    void integrate(const DeviceBuffer<float3>        d_x,
                   DeviceBuffer<float3>              d_xp,
                   DeviceBuffer<float3>              d_v,
                   const DeviceBuffer<float3>        d_f,
                   const real                        dt,
                   const bool                        doTemperatureScaling,
                   gmx::ArrayRef<const t_grp_tcstat> tcstat,
                   const bool                        doParrinelloRahman,
                   const float                       dtPressureCouple,
                   const matrix                      prVelocityScalingMatrix);

    /*! \brief Set the integrator
     *
     * Allocates memory for inverse masses, and, if needed for temperature scaling factor(s)
     * and temperature coupling groups. Copies inverse masses and temperature coupling groups
     * to the GPU.
     *
     * \param[in] numAtoms            Number of atoms in the system.
     * \param[in] inverseMasses       Inverse masses of atoms.
     * \param[in] numTempScaleValues  Number of temperature scale groups.
     * \param[in] tempScaleGroups     Maps the atom index to temperature scale value.
     */
    void set(const int             numAtoms,
             const real*           inverseMasses,
             int                   numTempScaleValues,
             const unsigned short* tempScaleGroups);

    /*! \brief Class with hardware-specific interfaces and implementations.*/
    class Impl;

private:
    //! GPU context object
    const DeviceContext& deviceContext_;
    //! GPU stream
    const DeviceStream& deviceStream_;
    //! GPU kernel launch config
    KernelLaunchConfig kernelLaunchConfig_;
    //! Number of atoms
    int numAtoms_;

    //! 1/mass for all atoms (GPU)
    DeviceBuffer<float> d_inverseMasses_;
    //! Current size of the reciprocal masses array
    int numInverseMasses_ = -1;
    //! Maximum size of the reciprocal masses array
    int numInverseMassesAlloc_ = -1;

    //! Number of temperature coupling groups (zero = no coupling)
    int numTempScaleValues_ = 0;
    /*! \brief Array with temperature scaling factors.
     * This is temporary solution to remap data from t_grp_tcstat into plain array
     * \todo Replace with better solution.
     */
    gmx::HostVector<float> h_lambdas_;
    //! Device-side temperature scaling factors
    DeviceBuffer<float> d_lambdas_;
    //! Current size of the array with temperature scaling factors (lambdas)
    int numLambdas_ = -1;
    //! Maximum size of the array with temperature scaling factors (lambdas)
    int numLambdasAlloc_ = -1;


    //! Array that maps atom index onto the temperature scaling group to get scaling parameter
    DeviceBuffer<unsigned short> d_tempScaleGroups_;
    //! Current size of the temperature coupling groups array
    int numTempScaleGroups_ = -1;
    //! Maximum size of the temperature coupling groups array
    int numTempScaleGroupsAlloc_ = -1;

    //! Vector with diagonal elements of the Parrinello-Rahman pressure coupling velocity rescale factors
    float3 prVelocityScalingMatrixDiagonal_;
};

} // namespace gmx

#endif
