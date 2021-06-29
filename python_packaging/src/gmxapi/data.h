/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2019, by the GROMACS development team, led by
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

#ifndef GMXPY_DATA_H
#define GMXPY_DATA_H

namespace gmxpy
{

// Note: avoid templating on number-of-dimensions because then we can't have an
// arbitrary number of dimensions after compile time. Instead, we can have special
// cases for 1 and 2 dimensions if optimizations are possible, and dispatch at
// run time.
template<typename Scalar, typename Handle> class NDArray; // primary template

// partial specialization where the handle is a container templated on the scalar type.
template<typename Scalar, template<typename> class Container>
class NDArray< Scalar, Container <Scalar> >;

// Partial specialization for vector container type.
template<typename Scalar>
class NDArray< Scalar, std::vector <Scalar> >;

// Partial specialization for array of size L can be compiled, but must be
// exported to Python with conversion to a type without L in its signature.
template<typename Scalar, int L>
class NDArray< Scalar, std::array<Scalar, L> >;



}      // end namespace gmxpy

#endif // GMXPY_DATA_H
