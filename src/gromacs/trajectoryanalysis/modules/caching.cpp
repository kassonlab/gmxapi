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

// Implement required functions from base class

void CachingTafModule::initOptions(IOptionsContainer *options,
                             TrajectoryAnalysisSettings *settings)
{
    // TODO: convert TRX_ flags in trxio.h to named enum
    // TODO: update gmx::TrajectoryAnalysisSettings::set{,Frame}Flags() call signature and enum to identifiable types.
    settings->setFrameFlags(TRX_NEED_X | TRX_NEED_V | TRX_NEED_F);
}

void CachingTafModule::initAnalysis(const TrajectoryAnalysisSettings &settings,
                              const TopologyInformation &top)
{}

void CachingTafModule::analyzeFrame(int frnr,
                              const t_trxframe &fr,
                              t_pbc *pbc,
                              TrajectoryAnalysisModuleData *pdata)
{
    // Let's just grab a copy of the frame, using the unpublished trxframe interface.
    // We can stash it in an AnalysisData object, but don't need to for a first draft.
    // The AnalysisData protocol seems inconsistent between the TAF overview
    // and the class documentation.
    // Copy assign the member shared_ptr with the input frame.
    last_frame_ = trxframe_copy(fr);
}

void CachingTafModule::finishAnalysis(int nframes)
{
    // If we're just caching trajectories, there is no post-processing.
}

/// Does not produce output unless requested.
void CachingTafModule::writeOutput() {}

/// Return the last frame processed.
// TODO implement
void CachingTafModule::frame() {}

} // end namespace trajectoryanalysis
} // end namespace gmx
