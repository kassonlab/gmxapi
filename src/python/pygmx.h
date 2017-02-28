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
int version();

/// Process TPR input file
void list_tpx();

/// Process a trajectory file
void list_trx(const std::string& fn);

class TrajectoryFrame
{

};

class Trajectory
{
public:
    Trajectory(const std::string& filename);
    virtual ~Trajectory();
    void dump();
private:
    const std::string& filename_;
    t_fileio          *fpread_;
    int               nframe_;
    rvec              *x_, *v_, *f_;
    matrix            box_;
    gmx_trr_header_t  trrheader_;
    gmx_bool          bOK_;
};

} // end pygmx

#endif // GMX_PYGMX_H
