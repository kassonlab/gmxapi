#include "pygmx.h"

#include <string>
#include <cstdio>

#include "gromacs/fileio/gmxfio.h"
#include "gromacs/fileio/tpxio.h"
#include "gromacs/fileio/trrio.h"
#include "gromacs/math/vectypes.h"
#include "gromacs/math/vecdump.h"
#include "gromacs/utility/basedefinitions.h"
// smalloc manages memory for raw pointers
#include "gromacs/utility/smalloc.h"
#include "gromacs/utility/txtdump.h"

namespace pygmx
{

int version()
{
    return int(gmx_version);
}

// Only implements trr reading
// list_trr() is hidden in file scope of dump.cpp
void list_trx(const std::string& fn)
{
    t_fileio          *fpread;
    int               nframe, indent;
    char              buf[256];
    rvec              *x, *v, *f;
    matrix            box;
    gmx_trr_header_t  trrheader;
    gmx_bool          bOK;

    fpread  = gmx_trr_open(fn.c_str(), "r");

    nframe = 0;
    while (gmx_trr_read_frame_header(fpread, &trrheader, &bOK))
    {
        snew(x, trrheader.natoms);
        snew(v, trrheader.natoms);
        snew(f, trrheader.natoms);
        // Need to look at ...read_frame_data to see what a frame object should look like
        if (gmx_trr_read_frame_data(fpread, &trrheader,
                                    trrheader.box_size ? box : nullptr,
                                    trrheader.x_size   ? x : nullptr,
                                    trrheader.v_size   ? v : nullptr,
                                    trrheader.f_size   ? f : nullptr))
        {
            sprintf(buf, "%s frame %d", fn.c_str(), nframe);
            indent = 0;
            indent = pr_title(stdout, indent, buf);
            pr_indent(stdout, indent);
            fprintf(stdout, "natoms=%10d  step=%10" GMX_PRId64 "  time=%12.7e  lambda=%10g\n",
                    trrheader.natoms, trrheader.step, trrheader.t, trrheader.lambda);
            if (trrheader.box_size)
            {
                pr_rvecs(stdout, indent, "box", box, DIM);
            }
            if (trrheader.x_size)
            {
                pr_rvecs(stdout, indent, "x", x, trrheader.natoms);
            }
            if (trrheader.v_size)
            {
                pr_rvecs(stdout, indent, "v", v, trrheader.natoms);
            }
            if (trrheader.f_size)
            {
                pr_rvecs(stdout, indent, "f", f, trrheader.natoms);
            }
        }
        else
        {
            fprintf(stderr, "\nWARNING: Incomplete frame: nr %d, t=%g\n",
                    nframe, trrheader.t);
        }

        sfree(x);
        sfree(v);
        sfree(f);
        nframe++;
    }
    if (!bOK)
    {
        fprintf(stderr, "\nWARNING: Incomplete frame header: nr %d, t=%g\n",
                nframe, trrheader.t);
    }
    gmx_trr_close(fpread);
}

Trajectory::Trajectory(const std::string& filename) :
    filename_{filename},
    nframe_{0},
    bOK_{true}
{
    fpread_  = gmx_trr_open(filename_.c_str(), "r");
}

Trajectory::~Trajectory()
{
    gmx_trr_close(fpread_);
}

// can only dump once
void Trajectory::dump()
{
    int indent(0);
    char buf[256];
    nframe_ = 0;
    while (gmx_trr_read_frame_header(fpread_, &trrheader_, &bOK_))
    {
        snew(x_, trrheader_.natoms);
        snew(v_, trrheader_.natoms);
        snew(f_, trrheader_.natoms);
        // Need to look at ...read_frame_data to see what a frame object should look like
        if (gmx_trr_read_frame_data(fpread_, &trrheader_,
                                    trrheader_.box_size ? box_ : nullptr,
                                    trrheader_.x_size   ? x_ : nullptr,
                                    trrheader_.v_size   ? v_ : nullptr,
                                    trrheader_.f_size   ? f_ : nullptr))
        {
            sprintf(buf, "%s frame %d", filename_.c_str(), nframe_);
            indent = 0;
            indent = pr_title(stdout, indent, buf);
            pr_indent(stdout, indent);
            fprintf(stdout, "natoms=%10d  step=%10" GMX_PRId64 "  time=%12.7e  lambda=%10g\n",
                    trrheader_.natoms, trrheader_.step, trrheader_.t, trrheader_.lambda);
            if (trrheader_.box_size)
            {
                pr_rvecs(stdout, indent, "box", box_, DIM);
            }
            if (trrheader_.x_size)
            {
                pr_rvecs(stdout, indent, "x", x_, trrheader_.natoms);
            }
            if (trrheader_.v_size)
            {
                pr_rvecs(stdout, indent, "v", v_, trrheader_.natoms);
            }
            if (trrheader_.f_size)
            {
                pr_rvecs(stdout, indent, "f", f_, trrheader_.natoms);
            }
        }
        else
        {
            fprintf(stderr, "\nWARNING: Incomplete frame: nr %d, t=%g\n",
                    nframe_, trrheader_.t);
        }

        sfree(x_);
        sfree(v_);
        sfree(f_);
        nframe_++;
    }
    if (!bOK_)
    {
        fprintf(stderr, "\nWARNING: Incomplete frame header: nr %d, t=%g\n",
                nframe_, trrheader_.t);
    }
}

} // end pygmx
