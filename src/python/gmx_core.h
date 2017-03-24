
/*! \internal \file
 * \brief Declares symbols to be exported to gmx.core Python module.
 *
 * Declares namespace gmx::pyapi
 */
#ifndef PYGMX_CORE_H
#define PYGMX_CORE_H

#include <memory>
#include "gromacs/trajectoryanalysis/analysismodule.h"
#include "gromacs/trajectoryanalysis/runner.h"

namespace gmx
{
/*! \brief API wrappers for Python bindings
 */
namespace pyapi
{

/*! \brief Wraps Trajectory Analyis Runner for Python interface.
 *
 * Exported to Python as gmx.core.TafRunner
 */
class PyRunner
{
public:
    /// Empty constructor not yet used.
    PyRunner() = delete;

    /// Construct runner with a single bound module.
    PyRunner(std::shared_ptr<gmx::TrajectoryAnalysisModule> module);

    virtual ~PyRunner();

    /*! \brief Advance the current frame one step.
     *
     * Returns when data dependencies on the next trajectory frame have been
     * satisfied.
     */
    bool next();

private:
    /// has a common runner for most behavior
    gmx::trajectoryanalysis::Runner runner_;

    /// binds to one analysis module
    std::shared_ptr<gmx::TrajectoryAnalysisModule> module_;
};

// class CachingTafModule;

} // end namespace pyapi
} // end namespace gmx

#endif // PYGMX_CORE_H
