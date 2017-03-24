/*! \file
 * \brief Declares the CachingTafModule
 *
 */

#ifndef GMX_TRAJECTORYANALYSIS_CACHING_H
#define GMX_TRAJECTORYANALYSIS_CACHING_H

#include "gromacs/trajectoryanalysis/analysismodule.h"

namespace gmx
{
namespace trajectoryanalysis
{
using gmx::TrajectoryAnalysisSettings;
using gmx::TopologyInformation;
using gmx::IOptionsContainer;

class CachingTafModule : public gmx::TrajectoryAnalysisModule
{
public:
    // Additional methods provide by derived class
    void frame();

    // Implement required virtual functions from base class

    virtual void initOptions(IOptionsContainer *options,
                             TrajectoryAnalysisSettings *settings);

    virtual void initAnalysis(const TrajectoryAnalysisSettings &settings,
                              const TopologyInformation &top);

    virtual void analyzeFrame(int frnr,
                              const t_trxframe &fr,
                              t_pbc *pbc,
                              TrajectoryAnalysisModuleData *pdata);

    virtual void finishAnalysis(int nframes);

    virtual void writeOutput();
    
private:
    std::shared_ptr<t_trxframe> last_frame_; //!< cache the last frame read.
};

} // end namespace trajectoryanalysis
} // end namespace gmx

#endif // GMX_TRAJECTORYANALYSIS_CACHING_H
