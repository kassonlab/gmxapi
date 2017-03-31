/*! \file
 * \brief Defines the CachingTafModule
 *
 */

#include "gromacs/trajectoryanalysis/modules/caching.h"

#include <memory>

#include "gromacs/trajectoryanalysis/analysissettings.h"
#include "gromacs/trajectory/trajectoryframe.h"
#include "gromacs/fileio/trxio.h"

namespace gmx
{
namespace trajectoryanalysis
{

const char CacheInfo::name[] = "cache";
const char CacheInfo::shortDescription[] =
    "Cache a frame of trajectory data";

TrajectoryAnalysisModulePointer CacheInfo::create()
{
    return TrajectoryAnalysisModulePointer(new CachingTafModule);
}

// Implement required functions from base class
// Is there a Gromacs convention for tagging unused function parameters?
void CachingTafModule::initOptions(IOptionsContainer *options,
                             TrajectoryAnalysisSettings *settings)
{
    // TODO: convert TRX_ flags in trxio.h to named enum
    // TODO: update gmx::TrajectoryAnalysisSettings::set{,Frame}Flags() call signature and enum to identifiable types.
    // TODO: get more helpful error from read_next_frame when _NEED_ flags aren't present?
    // Note that memory is allocated for v and f even if they are not available
    // for reading.
    settings->setFrameFlags(TRX_NEED_X | TRX_READ_V | TRX_READ_F);
}

// Is there a Gromacs convention for tagging unused function parameters?
void CachingTafModule::initAnalysis(const TrajectoryAnalysisSettings &settings,
                              const TopologyInformation &top)
{}

// Is there a Gromacs convention for tagging unused function parameters?
void CachingTafModule::analyzeFrame(int frnr,
                              const t_trxframe &fr,
                              t_pbc *pbc,
                              TrajectoryAnalysisModuleData *pdata)
{
    // Let's just grab a copy of the frame, using the trxframe interface.
    // We can stash it in an AnalysisData object, but don't need to for a first draft.
    // Copy assign the member shared_ptr with the input frame.
    last_frame_ = gmx::trajectory::trxframe_copy(fr);
    /*
    Note AnalysisData != TrajectoryAnalysisModuleData. The TrajectoryAnalysisModuleData object provided by the runner mediates access
    to the AnalysisData members of *this as configured with initAnalysis() and startFrames(). The Selection objects available via the TrajectoryAnalysisModuleData are probably more useful than direct trxframe access, anyway.
    */
    /*! TODO: use data module for analyzeFrame to retain a shared_ptr
    * to the trajectory frame data rather than copying fr.
    */
}

// Is there a Gromacs convention for tagging unused function parameters?
void CachingTafModule::finishAnalysis(int nframes)
{
    // If we're just caching trajectories, there is no post-processing.
}

/// Does not produce output unless requested.
void CachingTafModule::writeOutput() {}

/// Get a shared handle to the last frame processed.
std::shared_ptr<t_trxframe> CachingTafModule::frame() const
{
    return last_frame_;
}

} // end namespace trajectoryanalysis
} // end namespace gmx
