/*! \file
 * \brief Declares the CachingTafModule
 *
 * \internal
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

/*! \brief Provide a dummy module to grab copies of frames received.
 *
 * Objects of this class are useful for testing runners, pipelines,
 * and other proofs of concept. This rough draft should be replaced
 * soon with a class that uses the data modules to retrieve and
 * store trajectory info and to use selection processing.
 * /internal
 */
class CachingTafModule : public gmx::TrajectoryAnalysisModule
{
public:
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

    /*! \brief Additional methods provided by this class.
     *
     * \internal
     */
    std::shared_ptr<t_trxframe> frame() const;

private:
    std::shared_ptr<t_trxframe> last_frame_; //!< cache the last frame read.
};

/*! \brief Module info for Caching module
 *
 * Various code for registering modules requires a class (undocumented?)
 * providing these three members.
 * \internal
 * \ingroup module_trajectoryanalysis
 */
class CacheInfo
{
public:
    /// Name to register for module
    static const char name[];
    /// Description for registration
    static const char shortDescription[];

    /*! \brief Get pointer for registering module
     *
     * \return pointer to a new CachingTafModule
     */
    static TrajectoryAnalysisModulePointer create();
};

} // end namespace trajectoryanalysis
} // end namespace gmx

#endif // GMX_TRAJECTORYANALYSIS_CACHING_H
