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

TrajectoryFrame::TrajectoryFrame(const gmx_trr_header_t& trrheader) :
    natoms_{trrheader.natoms},
    step_{trrheader.step},
    time_{trrheader.t},
    lambda_{trrheader.lambda},
    fep_state_{trrheader.fep_state},
    box_{{0,0,0},{0,0,0},{0,0,0}},
    position_{nullptr},
    velocity_{nullptr},
    force_{nullptr}
{
    // We want to allocate new memory if data is available
    // because the arrays will be wrapped in a Frame object
    // and returned. Otherwise, do_trr_frame_data won't do
    // anything with the pointer passed, but we shouldn't rely
    // on those semantics and the behavior of gmx_trr_read_frame_header
    // is unspecified.
    // TODO: don't rely on unspecified semantics
    if (trrheader.x_size)
    {
        position_ = std::make_shared< vecvec >(trrheader.natoms);
    }
    if (trrheader.v_size)
    {
        velocity_ = std::make_shared< vecvec >(trrheader.natoms);
    }
    if (trrheader.f_size)
    {
        force_ = std::make_shared< vecvec >(trrheader.natoms);
    }
}

TrajectoryFrame::~TrajectoryFrame()
{}

/*! \brief Construct from filename
 * \param filename unicode string
 */
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

// gmx::RVec version of rvec is a typedef for gmx::BasicVector< real >
std::unique_ptr< TrajectoryFrame > Trajectory::nextFrame() noexcept(false)
{
    gmx_trr_header_t trrheader;

    // calls do_trr_frame_header which prints with cstdio
    if (gmx_trr_read_frame_header(fpread_, &trrheader, &bOK_))
    {
        // we will return a pointer to a new frame if even a partial
        // frame exists or nullptr if not
        // Note: std::make_unique is available in C++14 but not C++11
#ifdef __cpp_lib_make_unique
        auto frame = std::make_unique<TrajectoryFrame>(trrheader);
#else
        std::unique_ptr<TrajectoryFrame> frame(new TrajectoryFrame(trrheader));
#endif
        rvec* position{nullptr};
        rvec* velocity{nullptr};
        rvec* force{nullptr};
        static_assert(sizeof(rvec) == sizeof(*frame->position_->data()), "wrong size\n");
        if (trrheader.x_size)
        {
            position = reinterpret_cast<rvec(*)>(frame->position_->data());
            //position_ = std::make_shared< vecvec >(trrheader.natoms);
        }
        if (trrheader.v_size)
        {
            velocity = reinterpret_cast<rvec(*)>(frame->velocity_->data());
            //velocity_ = std::make_shared< vecvec >(trrheader.natoms);
        }
        if (trrheader.f_size)
        {
            force = reinterpret_cast<rvec(*)>(frame->force_->data());
            //force_ = std::make_shared< vecvec >(trrheader.natoms);
        }
        if (gmx_trr_read_frame_data(fpread_,
                                    &trrheader,
                                    reinterpret_cast<rvec(*)>(frame->box_),
                                    position,
                                    velocity,
                                    force) )
/*
        // gmx_trr_read_frame_data calls do_trr_frame, which calls
        // do_trr_frame_header and do_trr_frame_data, which use stderr, etc.,
        // and use various gmx_fio_... macros
        if (gmx_trr_read_frame_data(fpread_,
                                    &trrheader,
                                    reinterpret_cast<rvec(*)>(frame->box_.data()),
                                    reinterpret_cast<rvec(*)>(frame->position_->data()),
                                    reinterpret_cast<rvec(*)>(frame->velocity_->data()),
                                    reinterpret_cast<rvec(*)>(frame->force_->data()) ))
*/        {
            //natoms_ = trrheader.natoms;
            //step_ = trrheader.step;
            //time_ = trrheader.t;
            //lambda_ = trrheader.lambda;
        }
        else
        {
            //error: "\nWARNING: Incomplete frame: nr %d, t=%g\n",
            //        nframe_, trrheader.t
        }

        return frame;
    }
    else
    {
        // error: "\nWARNING: Incomplete frame header: nr %d, t=%g\n",
        //        nframe_, trrheader.t)
        return nullptr;
    }
}

// can only dump once
// Only implements trr reading
// list_trr() is hidden in file scope of dump.cpp
void Trajectory::dump()
{
    int indent(0);
    char buf[256];
    gmx_trr_header_t trrheader;
    nframe_ = 0;
    while (gmx_trr_read_frame_header(fpread_, &trrheader, &bOK_))
    {
        snew(x_, trrheader.natoms);
        snew(v_, trrheader.natoms);
        snew(f_, trrheader.natoms);
        // Need to look at ...read_frame_data to see what a frame object should look like
        if (gmx_trr_read_frame_data(fpread_, &trrheader,
                                    trrheader.box_size ? box_ : nullptr,
                                    trrheader.x_size   ? x_ : nullptr,
                                    trrheader.v_size   ? v_ : nullptr,
                                    trrheader.f_size   ? f_ : nullptr))
        {
            sprintf(buf, "%s frame %d", filename_.c_str(), nframe_);
            indent = 0;
            indent = pr_title(stdout, indent, buf);
            pr_indent(stdout, indent);
            fprintf(stdout, "natoms=%10d  step=%10" GMX_PRId64 "  time=%12.7e  lambda=%10g\n",
                    trrheader.natoms, trrheader.step, trrheader.t, trrheader.lambda);
            if (trrheader.box_size)
            {
                pr_rvecs(stdout, indent, "box", box_, DIM);
            }
            if (trrheader.x_size)
            {
                pr_rvecs(stdout, indent, "x", x_, trrheader.natoms);
            }
            if (trrheader.v_size)
            {
                pr_rvecs(stdout, indent, "v", v_, trrheader.natoms);
            }
            if (trrheader.f_size)
            {
                pr_rvecs(stdout, indent, "f", f_, trrheader.natoms);
            }
        }
        else
        {
            fprintf(stderr, "\nWARNING: Incomplete frame: nr %d, t=%g\n",
                    nframe_, trrheader.t);
        }

        sfree(x_);
        sfree(v_);
        sfree(f_);
        nframe_++;
    }
    if (!bOK_)
    {
        fprintf(stderr, "\nWARNING: Incomplete frame header: nr %d, t=%g\n",
                nframe_, trrheader.t);
    }
}

} // end pygmx
