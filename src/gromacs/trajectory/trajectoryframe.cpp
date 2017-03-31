/*
 * This file is part of the GROMACS molecular simulation package.
 *
 * Copyright (c) 2016,2017, by the GROMACS development team, led by
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
#include "gmxpre.h"

#include "trajectoryframe.h"

#include <cstdio>

#include <algorithm>

#include "gromacs/math/veccompare.h"
#include "gromacs/topology/atoms.h"
#include "gromacs/utility/compare.h"
#include "gromacs/utility/smalloc.h"

void comp_frame(FILE *fp, t_trxframe *fr1, t_trxframe *fr2,
                gmx_bool bRMSD, real ftol, real abstol)
{
    fprintf(fp, "\n");
    cmp_int(fp, "not_ok", -1, fr1->not_ok, fr2->not_ok);
    cmp_int(fp, "natoms", -1, fr1->natoms, fr2->natoms);
    if (cmp_bool(fp, "bTitle", -1, fr1->bTitle, fr2->bTitle))
    {
        cmp_str(fp, "title", -1, fr1->title, fr2->title);
    }
    if (cmp_bool(fp, "bStep", -1, fr1->bStep, fr2->bStep))
    {
        cmp_int(fp, "step", -1, fr1->step, fr2->step);
    }
    cmp_int(fp, "step", -1, fr1->step, fr2->step);
    if (cmp_bool(fp, "bTime", -1, fr1->bTime, fr2->bTime))
    {
        cmp_real(fp, "time", -1, fr1->time, fr2->time, ftol, abstol);
    }
    if (cmp_bool(fp, "bLambda", -1, fr1->bLambda, fr2->bLambda))
    {
        cmp_real(fp, "lambda", -1, fr1->lambda, fr2->lambda, ftol, abstol);
    }
    if (cmp_bool(fp, "bAtoms", -1, fr1->bAtoms, fr2->bAtoms))
    {
        cmp_atoms(fp, fr1->atoms, fr2->atoms, ftol, abstol);
    }
    if (cmp_bool(fp, "bPrec", -1, fr1->bPrec, fr2->bPrec))
    {
        cmp_real(fp, "prec", -1, fr1->prec, fr2->prec, ftol, abstol);
    }
    if (cmp_bool(fp, "bX", -1, fr1->bX, fr2->bX))
    {
        cmp_rvecs(fp, "x", std::min(fr1->natoms, fr2->natoms), fr1->x, fr2->x, bRMSD, ftol, abstol);
    }
    if (cmp_bool(fp, "bV", -1, fr1->bV, fr2->bV))
    {
        cmp_rvecs(fp, "v", std::min(fr1->natoms, fr2->natoms), fr1->v, fr2->v, bRMSD, ftol, abstol);
    }
    if (cmp_bool(fp, "bF", -1, fr1->bF, fr2->bF))
    {
        cmp_rvecs(fp, "f", std::min(fr1->natoms, fr2->natoms), fr1->f, fr2->f, bRMSD, ftol, abstol);
    }
    if (cmp_bool(fp, "bBox", -1, fr1->bBox, fr2->bBox))
    {
        cmp_rvecs(fp, "box", 3, fr1->box, fr2->box, FALSE, ftol, abstol);
    }
}

void done_frame(t_trxframe *frame)
{
    if (frame->atoms)
    {
        done_atom(frame->atoms);
        sfree(frame->atoms);
    }
    sfree(frame->x);
    sfree(frame->v);
    sfree(frame->f);
}

void gmx::trajectory::trxframe_deleter(t_trxframe* f)
{
    // Must only free memory allocated.
    if (f->bX)
    {
        sfree(f->x);
    }
    if (f->bV)
    {
        sfree(f->v);
    }
    if (f->bF)
    {
        sfree(f->f);
    }
    if (f->bTitle)
    {
        delete f->title;
    }
    if (f->atoms)
    {
        done_atom(f->atoms);
        delete f->atoms;
    }
    if (f->bIndex)
    {
        sfree(f->index);
    }
    delete f;
};

std::unique_ptr<t_trxframe, void(*)(t_trxframe*)> gmx::trajectory::trxframe_copy(const t_trxframe &frame)
{
    // Copy construct the trajectory frame struct.
    // std::make_unique not available until C++14, but we probably want a
    // custom deleter anyway.
    std::unique_ptr<t_trxframe, void(*)(t_trxframe*)> frame_copy(nullptr, &trxframe_deleter);
    frame_copy.reset(new t_trxframe(frame));

    // Allocate memory and copy the available member arrays.
    // Allow for addition of non-default copy constructor with
    // deep copy by checking whether arrays are distinct non-null addresses.
    // Note that struct t_trxframe definition is in trajectoryframe.h and there is no other documented interface to member data
    if (frame.bX && frame.x && (!frame_copy->x || frame_copy->x == frame.x))
    {
        // allocate new memory and perform copy
        snew(frame_copy->x, frame.natoms);
        for (auto i(0); i < frame.natoms; ++i)
        {
            std::copy(std::begin(frame.x[i]), std::end(frame.x[i]), frame_copy->x[i]);
        }
        frame_copy->bX = true;
    }
    else
    {
        frame_copy->bX = false;
    }

    if (frame.bV && frame.v && (!frame_copy->v || frame.v == frame_copy->v))
    {
        snew(frame_copy->v, frame.natoms);
        for (auto i(0); i < frame.natoms; ++i)
        {
            std::copy(std::begin(frame.v[i]), std::end(frame.v[i]), frame_copy->v[i]);
        }
        frame_copy->bV = true;
    }
    else
    {
        frame_copy->bV = false;
    }

    if (frame.bF && frame.f && (!frame_copy->f || frame.f == frame_copy->f))
    {
        snew(frame_copy->f, frame.natoms);
        for (auto i(0); i < frame.natoms; ++i)
        {
            std::copy(std::begin(frame.f[i]), std::end(frame.f[i]), frame_copy->f[i]);
        }
        frame_copy->bF = true;
    }
    else
    {
        frame_copy->bF = false;
    }
    // TODO: this is not a complete copy... missing atoms, title, index.
    frame_copy->bTitle = false;
    frame_copy->bAtoms = false;
    frame_copy->bIndex = false;
    // Does matrix have copy constructor and deleter? Defer for now...
    frame_copy->bBox = false;

    return frame_copy;
}
