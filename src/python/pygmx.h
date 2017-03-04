/*! \libinternal \file
 * \brief
 * Declares pygmx c++ namespace
 *
 * \defgroup pygmx
 */

#ifndef GMX_PYGMX_H
#define GMX_PYGMX_H

#include <string>
#include "pybind11/pybind11.h"
#include "gromacs/version.h"
#include "gromacs/fileio/gmxfio.h"
//#include "gromacs/fileio/tpxio.h"
#include "gromacs/fileio/trrio.h"
#include "gromacs/math/vectypes.h"
//#include "gromacs/math/vecdump.h"
#include "gromacs/utility/basedefinitions.h"
// smalloc manages memory for raw pointers
//#include "gromacs/utility/smalloc.h"
//#include "gromacs/utility/txtdump.h"

namespace py = pybind11;

/*! \libinternal \brief
 * C++ implementation for pygmx Python module
 * \ingroup pygmx
 */
namespace pygmx
{

/// Make sure this module knows what Gromacs version we're in.
const auto gmx_version{GMX_VERSION};

/*! \brief Gromacs version
 * \returns Gromacs version as integer
 */
 constexpr int version()
 {
     return int(gmx_version);
 }

class TrajectoryFrame;

class Trajectory
{
public:
    Trajectory(const std::string& filename);
    // Not sure what an empty Trajectory is...
    Trajectory() = delete;
    // Not sure what it means to copy or assign these yet...
    Trajectory(const Trajectory&) = delete;
    Trajectory& operator=(const Trajectory&) = delete;

    virtual ~Trajectory();

    int version() const { return pygmx::version(); };
    void dump();

    std::unique_ptr< TrajectoryFrame > nextFrame() noexcept(false);

private:
    // These private data members maintain internal state and cache
    const std::string& filename_;     ///< name of file to read
    t_fileio          *fpread_;       ///< read file pointer
    int               nframe_;        ///< last read frame
    // Error: dump frees x, v, and f
    rvec              *x_, *v_, *f_;  ///< cached values in dynamically allocated arrays
    matrix            box_;           ///< last read box matrix
    gmx_bool          bOK_;           ///< error state of last frame read
};

class TrajectoryFrame
{
public:
    typedef std::vector< std::array<real, 3> > vecvec;
    // Let's make sure we allocate memory during construction
    TrajectoryFrame() = delete;

    TrajectoryFrame(const gmx_trr_header_t& trrheader);
    virtual ~TrajectoryFrame();

    // default assignment operator and copy constructor are fine.
    TrajectoryFrame(const TrajectoryFrame&) = default;
    TrajectoryFrame & operator=(const TrajectoryFrame&) = default;

    unsigned int natoms() const { return natoms_; };

    //auto box() { return Matrix(box); };
    auto position() {return position_;};
    auto velocity() {return velocity_;};
    auto force() {return force_;};
    unsigned int x_size() const { return position_->size(); };
    unsigned int v_size() const { return velocity_->size(); };
    unsigned int f_size() const { return force_->size(); };
    gmx_int64_t step() const { return step_; };
    real time() const { return time_; };
    real lambda() const { return lambda_; };
    int fep_state() const { return fep_state_; }
private:
    friend std::unique_ptr< TrajectoryFrame > Trajectory::nextFrame() noexcept(false);
    const int         natoms_;    //!< The total number of atoms
    const gmx_int64_t step_;      //!< Current step number
    const real        time_;         //!< Current time
    const real        lambda_;    //!< Current value of lambda
    const int         fep_state_; //!< Current value of alchemical state

    real      box_[3][3];
    std::shared_ptr< vecvec > position_;
    std::shared_ptr< vecvec > velocity_;
    std::shared_ptr< vecvec > force_;
};

} // end pygmx

#endif // GMX_PYGMX_H
